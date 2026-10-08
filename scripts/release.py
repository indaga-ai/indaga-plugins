#!/usr/bin/env python3
"""Build credential-free plugin archives from a clean, committed public tree."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

from check_hosted_contract import admit, compatible

ROOT = Path(__file__).resolve().parent.parent


def git(*args, root=ROOT):
    return subprocess.check_output(["git", "-C", str(root), *args])


def read_json(path):
    return json.loads((ROOT / path).read_text())


def validate():
    manifests = [read_json(f"indaga/{path}") for path in
                 ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")]
    version = manifests[0]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Release version must be numeric major.minor.patch")
    if any(m["version"] != version or m["name"] != "indaga" for m in manifests):
        raise ValueError("Host manifests must agree on name and version")
    if any(m.get("repository") != "https://github.com/indaga-ai/indaga-plugins" for m in manifests):
        raise ValueError("Host manifests must use the public release mirror")
    contract = admit(read_json("indaga/references/public-contract.json"))
    compatible(contract)
    expected_contract = read_json("indaga/references/compatibility.json")["required_version"]
    for skill in (ROOT / "indaga/skills").glob("*/SKILL.md"):
        for declared in re.findall(r'"public_contract"\s*:\s*"([^"]+)"', skill.read_text()):
            if declared != expected_contract:
                raise ValueError("Workflow call version disagrees with installed compatibility")
    marketplace = read_json(".claude-plugin/marketplace.json")["plugins"]
    if len(marketplace) != 1 or marketplace[0]["version"] != version:
        raise ValueError("Claude marketplace must match the plugin version")
    for path, kind in (("indaga/.mcp.json", "http"), ("indaga/mcp.json", "streamable-http")):
        servers = read_json(path)["mcpServers"]
        if servers != {"indaga-public-workflows": {"type": kind, "url": "https://app.indaga.ai/v1/mcp/public-workflows"}}:
            raise ValueError("Only the credential-free hosted MCP endpoint is allowed")
    # Relative Markdown links must stay within the plugin (or root for the root README).
    for path in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md"), *(ROOT / "indaga").rglob("*.md")]:
        boundary = ROOT / "indaga" if path.is_relative_to(ROOT / "indaga") else ROOT
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.is_relative_to(boundary) or not resolved.is_file():
                raise ValueError(f"Uncontained or missing link in {path.relative_to(ROOT)}")
    return version


def write_archive(path, members):
    # Stored ZIP avoids compressor/library variation across operating systems.
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as bundle:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)


def adapt(text, replacements):
    changes = []
    for before, after in replacements:
        count = text.count(before)
        if not count:
            raise ValueError("Canonical skill packaging adapter needs review")
        text = text.replace(before, after)
        changes.append({"from": before, "to": after, "occurrences": count})
    return text.encode(), changes


def build_skill_archives(output, version, members):
    receipts = {}
    required_contract = json.loads(members["references/compatibility.json"])["required_version"]
    connection, connection_changes = adapt(members["references/connection.md"].decode(), [
        ("Use this plugin's hosted Indaga MCP connection", "Use the existing hosted Indaga MCP connection"),
        ("Resolve the actual host-prefixed names", "This instruction-only skill pack does not register a connection or authenticate you.\nResolve the actual host-prefixed names"),
        ("this plugin needs a compatibility", "this skill pack needs a compatibility"),
        ("All procedures for\nthe four workflows are contained in this plugin.",
         "The procedure for\nthis installed workflow and its required references are contained in this skill pack.\nUse another workflow only if separately installed; otherwise explain the limit."),
        ("These four workflows make no writes", "This workflow makes no writes"),
        ("They do not import", "It does not import"),
        ("package does not narrow that grant", "skill pack does not narrow that grant"),
        ("MCP surface for these\nworkflows", "MCP surface for this\nworkflow"),
        ("these four procedures", "this installed procedure"),
    ])
    for source in sorted(name for name in members if re.fullmatch(r"skills/[a-z]+/SKILL.md", name)):
        workflow = source.split("/")[1]
        name = f"indaga-{workflow}"
        replacements = [(f"name: {workflow}\n", f"name: {name}\n"),
                        ("../../references/", "references/")]
        if workflow == "weekly":
            # The standalone upload description limit is 200 characters.
            replacements.append(("about recorded HRV", "about HRV"))
        skill, skill_changes = adapt(members[source].decode(), replacements)
        description = re.search(r"^description: (.+)$", skill.decode(), re.MULTILINE)
        if not description or len(description[1]) > 200:
            raise ValueError("Standalone skill description exceeds the upload limit")
        contents = {"SKILL.md": skill, "references/connection.md": connection,
                    "LICENSE": members["LICENSE"]}
        sources = {"SKILL.md": f"indaga/{source}",
                   "references/connection.md": "indaga/references/connection.md", "LICENSE": "indaga/LICENSE"}
        for reference in ("evidence.md", "public-contract.json", "compatibility.json"):
            path = f"references/{reference}"
            contents[path] = members[path]
            sources[path] = f"indaga/{path}"
        contents["README.md"] = (
            f"# Indaga {workflow} skill — {version}\n\n"
            f"This archive contains only the `{name}` workflow and its local references.\n"
            "It requires an existing OAuth connection to "
            f"`https://app.indaga.ai/v1/mcp/public-workflows`, public contract `{required_contract}`, "
            "and an Indaga account with Connect access.\n\n"
            "This skill does not install an MCP server, sign you in or narrow the existing "
            "OAuth grant. The public endpoint exposes six read tools; the same credential "
            "retains broader permissions, including writes through other surfaces. "
            "Use only the public workflow connection for this skill.\n\n"
            "For adults reviewing their own consumer wellness record, not diagnosis or "
            "treatment. Your chosen AI provider receives the information it reads under "
            "its terms and privacy policy and may process it outside the EU. Revocation "
            "stops future access without deleting provider copies.\n\n"
            "Claude: upload this ZIP through Customize → Skills → + → Create skill → "
            "Upload a skill, then enable it. Configure the hosted connector separately "
            "if it is not already present.\n\n"
            f"Codex: extract the `{name}/` folder into your user or repository "
            "`.agents/skills/` directory without replacing an existing folder. Start a "
            f"new session and select `{name}`. Configure the hosted connection separately.\n\n"
            "Use either the complete Indaga starter bundle or standalone copies of its "
            "workflows to avoid duplicate instructions. Installation and directory "
            "approval are separate; no approval or authenticated acceptance is claimed "
            "by this archive. Support: https://app.indaga.ai/support.\n"
        ).encode()
        packed = {f"{name}/{path}": data for path, data in contents.items()}
        for path, data in packed.items():
            if not path.endswith(".md"):
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode()):
                if target.startswith(("https://", "mailto:", "#")):
                    continue
                resolved = Path(path).parent / target.split("#", 1)[0]
                if ".." in resolved.parts or str(resolved) not in packed:
                    raise ValueError("Standalone skill has an uncontained or missing link")
        archive = output / f"{name}-skill-{version}.zip"
        write_archive(archive, packed)
        receipts[archive.name] = {
            "kind": "instruction-only-skill", "skill": name,
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "files": {path: hashlib.sha256(data).hexdigest() for path, data in sorted(packed.items())},
            "canonical_sources": {f"{name}/{path}": source for path, source in sources.items()},
            "transformations": {f"{name}/SKILL.md": skill_changes,
                                f"{name}/references/connection.md": connection_changes},
            "generated_files": [f"{name}/README.md"],
        }
    return receipts


def build(output):
    version = validate()
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("Commit tracked changes before building release artifacts")
    entries = git("ls-tree", "-r", "-z", "HEAD", "--", "indaga").split(b"\0")
    members = {}
    for entry in filter(None, entries):
        metadata, name = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        if mode != b"100644" or kind != b"blob":
            raise ValueError("Plugin archives may contain regular, non-executable files only")
        relative = name.decode().removeprefix("indaga/")
        members[relative] = git("cat-file", "blob", oid.decode())
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"indaga-{version}.zip"
    write_archive(archive, members)
    plugin = output / f"indaga-{version}.plugin"
    plugin.write_bytes(archive.read_bytes())
    skills = build_skill_archives(output, version, members)
    checksums = output / "SHA256SUMS"
    checksums.write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                                 for path in (archive, plugin, *(output / name for name in skills))))
    receipt = {
        "version": version,
        "source_commit": git("rev-parse", "HEAD").decode().strip(),
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(members.items())},
        "skill_archives": skills,
    }
    (output / "release.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "build"))
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        print(validate() if args.command == "validate" else build(args.output))
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, f"Release rejected: {error}\n")


if __name__ == "__main__":
    main()
