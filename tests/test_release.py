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
        tags = ("v0.2.0", "indaga--v0.2.0", "indaga-weekly--v0.2.0")
        for existing in (None, *tags):
            with self.subTest(existing_tag=existing), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp)
                log = directory / "calls.jsonl"
                gh = directory / "gh"
                gh.write_text(f"#!{sys.executable}\n" +
                              "import json, os, sys\n" +
                              "with open(os.environ['GH_TEST_LOG'], 'a') as out:\n" +
                              "    out.write(json.dumps(sys.argv[1:]) + '\\n')\n" +
                              "if sys.argv[1] == 'api' and 'ref=refs/tags/' + os.environ['GH_TEST_EXISTING_TAG'] in sys.argv:\n" +
                              "    sys.exit(1)  # GitHub rejects an already-existing reference\n")
                gh.chmod(0o755)
                env = {**os.environ, "PATH": f"{directory}{os.pathsep}{os.environ['PATH']}",
                       "GH_TEST_LOG": str(log), "GH_TEST_EXISTING_TAG": existing or "none",
                       "RELEASE_VERSION": "0.2.0", "GITHUB_SHA": source,
                       "GITHUB_REPOSITORY": "indaga-ai/indaga-plugins", "GH_TOKEN": "synthetic-only"}
                result = subprocess.run(["bash", str(ROOT / "scripts/draft_release.sh")],
                                        cwd=ROOT, env=env, capture_output=True, text=True)
                calls = [json.loads(line) for line in log.read_text().splitlines()]
                expected_tags = tags[:tags.index(existing) + 1] if existing else tags
                for call, tag in zip(calls, expected_tags):
                    self.assertEqual(call[0], "api", "Reserve every release/dependency tag before uploading")
                    self.assertIn(f"ref=refs/tags/{tag}", call)
                    self.assertIn(f"sha={source}", call)
                if existing:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(len(calls), len(expected_tags), "Any tag collision must stop before upload")
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(len(calls), len(tags) + 1)
                    publication = calls[-1]
                    self.assertEqual(publication[:3], ["release", "create", "v0.2.0"])
                    self.assertIn("--verify-tag", publication)
                    self.assertIn("--draft", publication)
                    self.assertEqual(publication[publication.index("--repo") + 1], "indaga-ai/indaga-plugins")

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
            self.assertEqual({p.name for p in first.iterdir()}, {p.name for p in second.iterdir()})
            for artifact in first.iterdir():
                self.assertEqual(artifact.read_bytes(), (second / artifact.name).read_bytes())
            owners = {"indaga": {"record", "recovery", "labs"}, "indaga-weekly": {"weekly"}}
            self.assertEqual({pack["plugin"] for pack in receipt["plugin_archives"].values()}, set(owners))
            for filename, pack in receipt["plugin_archives"].items():
                plugin = pack["plugin"]
                archive = first / filename
                self.assertEqual(archive.read_bytes(), (first / pack["plugin_asset"]["name"]).read_bytes())
                self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), pack["sha256"])
                self.assertEqual(pack["sha256"], pack["plugin_asset"]["sha256"])
                self.assertEqual(set(pack["skills"]), owners[plugin])
                files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only",
                                                 "HEAD", "--", plugin]).decode().splitlines()
                with self.subTest(plugin=plugin), zipfile.ZipFile(archive) as bundle:
                    self.assertEqual(set(bundle.namelist()), {p.removeprefix(f"{plugin}/") for p in files})
                    self.assertIn(".claude-plugin/plugin.json", bundle.namelist())
                    self.assertIn(".codex-plugin/plugin.json", bundle.namelist())
                    self.assertEqual({Path(p).parent.name for p in bundle.namelist() if p.endswith("/SKILL.md")}, owners[plugin])
                    self.assertEqual({p for p in bundle.namelist() if Path(p).name in ("mcp.json", ".mcp.json")},
                                     {"mcp.json", ".mcp.json"} if plugin == "indaga" else set())
                    extracted = Path(temp) / "plugins" / plugin
                    bundle.extractall(extracted)
                    for info in bundle.infolist():
                        self.assertFalse(Path(info.filename).is_absolute())
                        self.assertNotIn("..", Path(info.filename).parts)
                        self.assertEqual(info.external_attr >> 16, 0o100644)
                        source = pack["canonical_sources"][info.filename]
                        self.assertTrue(source.startswith(f"{plugin}/"))
                        expected = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{source}"])
                        data = bundle.read(info.filename)
                        self.assertEqual(data, expected)
                        self.assertEqual(hashlib.sha256(data).hexdigest(), pack["files"][info.filename])
                        if info.filename.endswith(".md"):
                            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode()):
                                if target.startswith(("https://", "mailto:", "#")):
                                    continue
                                resolved = (extracted / info.filename).parent / target.split("#", 1)[0]
                                self.assertTrue(resolved.resolve().is_relative_to(extracted.resolve()))
                                self.assertTrue(resolved.is_file())
            self.assertEqual({pack["skill"] for pack in receipt["skill_archives"].values()},
                             {f"indaga-{workflow}" for workflows in owners.values() for workflow in workflows})
            checksums = dict(line.split("  ", 1)[::-1] for line in (first / "SHA256SUMS").read_text().splitlines())
            self.assertEqual(set(checksums), {p.name for p in first.iterdir() if p.suffix in (".zip", ".plugin")})
            for filename, digest in checksums.items():
                self.assertEqual(hashlib.sha256((first / filename).read_bytes()).hexdigest(), digest)
            for filename, pack in receipt["skill_archives"].items():
                name = pack["skill"]
                workflow = name.removeprefix("indaga-")
                self.assertIn(workflow, owners[pack["plugin"]])
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

    def test_rejects_plugin_drift_credentials_and_symlinks(self):
        # Each case changes a real consumer boundary in a clean isolated repository.
        cases = [(plugin, regression) for plugin in ("indaga", "indaga-weekly")
                 for regression in ("version", "repository", "symlink", "extra_workflow")]
        cases += [("indaga", "credentials"), ("indaga", "incompatible_contract")]
        cases += [("indaga-weekly", regression) for regression in
                  ("contract_drift", "transport_file", "transport_declaration", "auth_declaration",
                   "uncontained_link", "dependency", "codex_authentication")]
        for plugin, regression in cases:
            with self.subTest(plugin=plugin, regression=regression), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "repo"
                subprocess.run(["git", "clone", "--quiet", "--no-local", str(ROOT), str(root)], check=True)
                if regression == "version":
                    path = root / plugin / ".claude-plugin/plugin.json"
                    data = json.loads(path.read_text())
                    data["version"] = "999.0.0"
                    path.write_text(json.dumps(data))
                elif regression == "repository":
                    path = root / plugin / ".codex-plugin/plugin.json"
                    data = json.loads(path.read_text())
                    data["repository"] = "https://example.invalid/private-staging"
                    path.write_text(json.dumps(data))
                elif regression == "credentials":
                    path = root / "indaga/.mcp.json"
                    data = json.loads(path.read_text())
                    data["mcpServers"]["indaga-public-workflows"]["headers"] = {"Authorization": "Bearer synthetic"}
                    path.write_text(json.dumps(data))
                elif regression == "symlink":
                    (root / plugin / "external").symlink_to("../../outside")
                elif regression == "extra_workflow":
                    extra = "weekly" if plugin == "indaga" else "record"
                    source = root / ("indaga-weekly" if extra == "weekly" else "indaga") / f"skills/{extra}/SKILL.md"
                    path = root / plugin / f"skills/{extra}/SKILL.md"
                    path.parent.mkdir(parents=True)
                    path.write_bytes(source.read_bytes())
                elif regression == "contract_drift":
                    path = root / plugin / "references/public-contract.json"
                    data = json.loads(path.read_text())
                    data["version"] = "1.0.1"
                    path.write_text(json.dumps(data))
                elif regression == "transport_file":
                    (root / plugin / ".mcp.json").write_text((root / "indaga/.mcp.json").read_text())
                elif regression in ("transport_declaration", "auth_declaration", "dependency"):
                    path = root / plugin / ".claude-plugin/plugin.json"
                    data = json.loads(path.read_text())
                    if regression == "transport_declaration":
                        data["mcpServers"] = {"indaga-public-workflows": {"type": "http", "url": "https://app.indaga.ai/v1/mcp/public-workflows"}}
                    elif regression == "auth_declaration":
                        data["headers"] = {"Authorization": "Bearer synthetic"}
                    else:
                        data["dependencies"][0]["version"] = "~0.1.0"
                    path.write_text(json.dumps(data))
                elif regression == "uncontained_link":
                    path = root / plugin / "README.md"
                    path.write_text(path.read_text() + "\n[External procedure](../indaga/skills/record/SKILL.md)\n")
                elif regression == "codex_authentication":
                    path = root / ".agents/plugins/marketplace.json"
                    data = json.loads(path.read_text())
                    next(p for p in data["plugins"] if p["name"] == plugin)["policy"]["authentication"] = "ON_INSTALL"
                    path.write_text(json.dumps(data))
                elif regression == "incompatible_contract":
                    path = root / "indaga/references/public-contract.json"
                    data = json.loads(path.read_text())
                    data["supported_versions"] = ["999.0.0"]
                    path.write_text(json.dumps(data))
                subprocess.run(["git", "-C", str(root), "add", "indaga", "indaga-weekly", ".agents"], check=True)
                subprocess.run(["git", "-C", str(root), "-c", "user.name=Release test",
                                "-c", "user.email=test@example.invalid", "commit", "-qm", "Synthetic regression"], check=True)
                result = self.run_builder(root, Path(temp) / "dist")
                self.assertNotEqual(result.returncode, 0)
                expected = {"version": "manifests must agree", "credentials": "credential-free",
                            "repository": "public release mirror",
                            "symlink": "regular, non-executable",
                            "incompatible_contract": "no longer supports installed",
                            "extra_workflow": "only its assigned workflows",
                            "contract_drift": "references must agree",
                            "transport_file": "no MCP or credentials",
                            "transport_declaration": "must not declare transport",
                            "auth_declaration": "must not declare transport",
                            "uncontained_link": "Uncontained or missing link",
                            "dependency": "dependency must match",
                            "codex_authentication": "must not request separate authentication"}[regression]
                self.assertIn(expected, result.stderr)

    def test_contract_update_keeps_both_plugin_references_and_versions_together(self):
        spec = importlib.util.spec_from_file_location("updater", ROOT / "scripts/check_hosted_contract.py")
        updater = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(updater)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            subprocess.run(["git", "clone", "--quiet", "--no-local", str(ROOT), str(root)], check=True)
            paths = list(root.glob("*/skills/*/SKILL.md"))
            original_skills = {p: p.read_bytes() for p in paths}
            projection = json.loads((root / "indaga/references/public-contract.json").read_text())
            projection["version"] = "1.0.1"
            admitted = updater.admit(projection)
            old = json.loads((root / "indaga/plugin.json").read_text())["version"]
            major, minor, patch_number = map(int, old.split("."))
            expected_version = f"{major}.{minor}.{patch_number + 1}"
            with patch.object(updater, "ROOT", root), patch.object(updater, "fetch", return_value=admitted), \
                    patch.object(sys, "argv", ["check_hosted_contract.py", "--update"]):
                updater.main()
            for plugin in ("indaga", "indaga-weekly"):
                self.assertEqual(json.loads((root / plugin / "references/public-contract.json").read_text()), admitted)
                for manifest in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                    self.assertEqual(json.loads((root / plugin / manifest).read_text())["version"], expected_version)
            weekly = json.loads((root / "indaga-weekly/.claude-plugin/plugin.json").read_text())
            self.assertEqual(weekly["dependencies"], [{"name": "indaga", "marketplace": "indaga", "version": f"~{expected_version}"}])
            self.assertTrue(all(p.read_bytes() == data for p, data in original_skills.items()))
            marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
            self.assertEqual({p["version"] for p in marketplace["plugins"]}, {expected_version})
            validation = subprocess.run([sys.executable, str(root / "scripts/release.py"), "validate"], capture_output=True, text=True)
            self.assertEqual(validation.returncode, 0, validation.stderr)


if __name__ == "__main__":
    unittest.main()
