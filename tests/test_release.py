"""Release-boundary proof: bytes, containment and invalid distribution rejection."""
import json
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


class ReleaseTests(unittest.TestCase):
    def test_contract_redirect_is_refused_without_contacting_its_target(self):
        spec = importlib.util.spec_from_file_location("public_checker", ROOT / "scripts/check_hosted_contract.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        requested = []
        projection = (ROOT / "indaga/references/public-contract.json").read_bytes()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requested.append(self.path)
                if self.path == "/contract":
                    self.send_response(307)
                    self.send_header("Location", "/redirect-target")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(projection)

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(checker, "URL", f"http://127.0.0.1:{server.server_port}/contract"):
                with self.assertRaisesRegex(ValueError, "redirect"):
                    checker.fetch()
            self.assertEqual(requested, ["/contract"], "A refused redirect must never contact its target")
        finally:
            server.shutdown()
            server.server_close()
            worker.join()

    def test_draft_publication_reserves_approved_source_and_stops_on_existing_tag(self):
        # Fake only the external CLI/API boundary. The actual publication shell owns ordering.
        source = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
        for existing in (False, True):
            with self.subTest(existing_tag=existing), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                log = directory / "calls.jsonl"
                gh = directory / "gh"
                gh.write_text(f"#!{sys.executable}\n" +
                              "import json, os, sys\n" +
                              "with open(os.environ['GH_TEST_LOG'], 'a') as out:\n" +
                              "    out.write(json.dumps(sys.argv[1:]) + '\\n')\n" +
                              "if sys.argv[1] == 'api' and os.environ['GH_TEST_EXISTING_TAG'] == 'yes':\n" +
                              "    sys.exit(1)  # GitHub rejects an already-existing reference\n")
                gh.chmod(0o755)
                env = {**os.environ, "PATH": f"{directory}{os.pathsep}{os.environ['PATH']}",
                       "GH_TEST_LOG": str(log), "GH_TEST_EXISTING_TAG": "yes" if existing else "no",
                       "RELEASE_VERSION": "0.2.0", "GITHUB_SHA": source,
                       "GITHUB_REPOSITORY": "indaga-ai/indaga-plugins", "GH_TOKEN": "synthetic-only"}
                result = subprocess.run(["bash", str(ROOT / "scripts/draft_release.sh")],
                                        cwd=ROOT, env=env, capture_output=True, text=True)
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                self.assertEqual(calls[0][0], "api", "Reserve the tag before creating a release")
                self.assertIn("ref=refs/tags/v0.2.0", calls[0])
                self.assertIn(f"sha={source}", calls[0])
                if existing:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(len(calls), 1, "Refusal must not upload artifacts to an old tag")
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(calls[1][:3], ["release", "create", "v0.2.0"])
                    self.assertIn("--verify-tag", calls[1])
                    self.assertIn("--draft", calls[1])
                    self.assertEqual(calls[1][calls[1].index("--repo") + 1], "indaga-ai/indaga-plugins")

    def run_builder(self, root, output, env=None):
        return subprocess.run([sys.executable, str(root / "scripts/release.py"), "build",
                               "--output", str(output)], capture_output=True, text=True, env=env)

    def test_archives_are_repeatable_contained_and_match_committed_files(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp) / "one", Path(temp) / "two"
            for output, timezone in ((first, "UTC"), (second, "Pacific/Honolulu")):
                result = self.run_builder(ROOT, output, {**os.environ, "TZ": timezone})
                self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads((first / "release.json").read_text())
            archive = first / f"indaga-{receipt['version']}.zip"
            self.assertEqual({p.name for p in first.iterdir()}, {p.name for p in second.iterdir()})
            for artifact in first.iterdir():
                self.assertEqual(artifact.read_bytes(), (second / artifact.name).read_bytes())
            self.assertEqual(archive.read_bytes(), next(first.glob("*.plugin")).read_bytes())
            files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only",
                                             "HEAD", "--", "indaga"]).decode().splitlines()
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(set(bundle.namelist()), {p.removeprefix("indaga/") for p in files})
                self.assertIn(".claude-plugin/plugin.json", bundle.namelist())
                self.assertIn(".codex-plugin/plugin.json", bundle.namelist())
                for source in files:
                    expected = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{source}"])
                    self.assertEqual(bundle.read(source.removeprefix("indaga/")), expected)
                    self.assertFalse(Path(source).is_absolute())
                    self.assertNotIn("..", Path(source).parts)
            workflows = {Path(p).parent.name for p in files if p.endswith("/SKILL.md")}
            self.assertEqual({pack["skill"] for pack in receipt["skill_archives"].values()},
                             {f"indaga-{workflow}" for workflow in workflows})
            for filename, pack in receipt["skill_archives"].items():
                name = pack["skill"]
                skill_archive = first / filename
                self.assertEqual(hashlib.sha256(skill_archive.read_bytes()).hexdigest(), pack["sha256"])
                with self.subTest(skill=name), zipfile.ZipFile(skill_archive) as bundle:
                    names = bundle.namelist()
                    self.assertEqual({Path(p).parts[0] for p in names}, {name})
                    self.assertEqual([p for p in names if p.endswith("/SKILL.md")], [f"{name}/SKILL.md"])
                    self.assertFalse(any(Path(p).name in (".mcp.json", "mcp.json", "plugin.json") for p in names))
                    self.assertFalse(any(Path(p).suffix not in (".md", ".json", "") for p in names))
                    extracted = Path(temp) / name
                    for info in bundle.infolist():
                        self.assertFalse(Path(info.filename).is_absolute())
                        self.assertNotIn("..", Path(info.filename).parts)
                        self.assertEqual(info.external_attr >> 16, 0o100644)
                    bundle.extractall(extracted)
                    skill = bundle.read(f"{name}/SKILL.md").decode()
                    self.assertEqual(re.search(r"^name: (.+)$", skill, re.MULTILINE)[1], name)
                    self.assertLessEqual(len(re.search(r"^description: (.+)$", skill, re.MULTILINE)[1]), 200)
                    canonical = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                                         f"HEAD:{pack['canonical_sources'][f'{name}/SKILL.md']}"]).decode()
                    # Only packaging links change in the reviewed workflow body.
                    self.assertEqual(skill.split("---", 2)[2],
                                     canonical.split("---", 2)[2].replace("../../references/", "references/"))
                    for path, expected_hash in pack["files"].items():
                        data = bundle.read(path)
                        self.assertEqual(hashlib.sha256(data).hexdigest(), expected_hash)
                        if path.endswith(".md"):
                            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode()):
                                if target.startswith(("https://", "mailto:", "#")):
                                    continue
                                resolved = (extracted / path).parent / target.split("#", 1)[0]
                                self.assertTrue(resolved.resolve().is_relative_to((extracted / name).resolve()))
                                self.assertTrue(resolved.is_file())
                    for path, source in pack["canonical_sources"].items():
                        expected = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{source}"])
                        if path in pack["transformations"]:
                            text = expected.decode()
                            for change in pack["transformations"][path]:
                                self.assertEqual(text.count(change["from"]), change["occurrences"])
                                text = text.replace(change["from"], change["to"])
                            expected = text.encode()
                        self.assertEqual(bundle.read(path), expected)

    def test_rejects_version_drift_credentials_and_symlinks(self):
        # Each case changes a real consumer boundary in a clean isolated repository.
        for regression in ("version", "repository", "credentials", "symlink", "incompatible_contract"):
            with self.subTest(regression=regression), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "repo"
                subprocess.run(["git", "clone", "--quiet", "--no-local", str(ROOT), str(root)], check=True)
                if regression == "version":
                    path = root / "indaga/.claude-plugin/plugin.json"
                    data = json.loads(path.read_text())
                    data["version"] = "999.0.0"
                    path.write_text(json.dumps(data))
                elif regression == "repository":
                    path = root / "indaga/.codex-plugin/plugin.json"
                    data = json.loads(path.read_text())
                    data["repository"] = "https://example.invalid/private-staging"
                    path.write_text(json.dumps(data))
                elif regression == "credentials":
                    path = root / "indaga/.mcp.json"
                    data = json.loads(path.read_text())
                    data["mcpServers"]["indaga-public-workflows"]["headers"] = {"Authorization": "Bearer synthetic"}
                    path.write_text(json.dumps(data))
                elif regression == "symlink":
                    (root / "indaga/external").symlink_to("../../outside")
                else:
                    path = root / "indaga/references/public-contract.json"
                    data = json.loads(path.read_text())
                    data["supported_versions"] = ["999.0.0"]
                    path.write_text(json.dumps(data))
                subprocess.run(["git", "-C", str(root), "add", "indaga"], check=True)
                subprocess.run(["git", "-C", str(root), "-c", "user.name=Release test",
                                "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic regression"], check=True)
                result = self.run_builder(root, Path(temp) / "dist")
                self.assertNotEqual(result.returncode, 0)
                expected = {"version": "manifests must agree", "credentials": "credential-free",
                            "repository": "public release mirror",
                            "symlink": "regular, non-executable",
                            "incompatible_contract": "no longer supports installed"}[regression]
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
