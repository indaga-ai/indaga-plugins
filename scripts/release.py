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
PLUGINS = {"indaga": {"record", "recovery", "labs"}, "indaga-weekly": {"weekly"}}
MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")


def git(*args, root=ROOT):
    return subprocess.check_output(["git", "-C", str(root), *args])


def read_json(path):
    return json.loads((ROOT / path).read_text())


def validate():
    version = read_json("indaga/plugin.json")["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Release version must be numeric major.minor.patch")
    contract = admit(read_json("indaga/references/public-contract.json"))
    compatible(contract)
    expected_contract = read_json("indaga/references/compatibility.json")["required_version"]
    for plugin, workflows in PLUGINS.items():
        manifests = [read_json(f"{plugin}/{path}") for path in MANIFESTS]
        if any(m["version"] != version or m["name"] != plugin for m in manifests):
            raise ValueError("Host manifests must agree on name and version")
        if any(m.get("repository") != "https://github.com/indaga-ai/indaga-plugins" for m in manifests):
            raise ValueError("Host manifests must use the public release mirror")
        skills = list((ROOT / plugin / "skills").rglob("SKILL.md"))
        if {p.relative_to(ROOT / plugin).as_posix() for p in skills} != {
                f"skills/{workflow}/SKILL.md" for workflow in workflows}:
            raise ValueError(f"{plugin} must contain only its assigned workflows")
        if read_json(f"{plugin}/references/public-contract.json") != contract or \
                read_json(f"{plugin}/references/compatibility.json") != read_json("indaga/references/compatibility.json"):
            raise ValueError("Plugin public contract and compatibility references must agree")
        for skill in skills:
            for declared in re.findall(r'"public_contract"\s*:\s*"([^"]+)"', skill.read_text()):
                if declared != expected_contract:
                    raise ValueError("Workflow call version disagrees with installed compatibility")
        if plugin == "indaga-weekly":
            allowed = {*MANIFESTS, "README.md", "LICENSE", "assets/icon-192.png", "assets/icon-512.png",
                       "skills/weekly/SKILL.md", *(f"references/{name}" for name in
                       ("connection.md", "evidence.md", "public-contract.json", "compatibility.json"))}
            if {p.relative_to(ROOT / plugin).as_posix() for p in (ROOT / plugin).rglob("*") if p.is_file()} != allowed:
                raise ValueError("Weekly addon may contain only its instruction-only plugin files; no MCP or credentials")
            forbidden = {"mcpservers", "hooks", "agents", "commands", "lspservers", "settings",
                         "authentication", "authorization", "auth", "oauth", "headers", "env", "access_token"}
            def has_transport(value):
                if isinstance(value, dict):
                    return bool(forbidden.intersection(k.lower() for k in value)) or any(has_transport(v) for v in value.values())
                return isinstance(value, list) and any(has_transport(v) for v in value)
            if any(has_transport(m) for m in manifests):
                raise ValueError("Weekly addon must not declare transport, authentication or executable components")
            if manifests[1].get("dependencies") != [{"name": "indaga", "marketplace": "indaga", "version": f"~{version}"}]:
                raise ValueError("Weekly Claude dependency must match the main release minimum")
            if any("dependencies" in m for m in (manifests[0], manifests[2])):
                raise ValueError("Main-plugin dependency belongs only in the supported Claude manifest")
    marketplace = read_json(".claude-plugin/marketplace.json")["plugins"]
    if len(marketplace) != len(PLUGINS) or {p["name"] for p in marketplace} != set(PLUGINS) or any(
            p["version"] != version or p["source"] != f"./{p['name']}" for p in marketplace):
        raise ValueError("Claude marketplace must match both plugin names, sources and versions")
    codex = read_json(".agents/plugins/marketplace.json")["plugins"]
    if len(codex) != len(PLUGINS) or {p["name"] for p in codex} != set(PLUGINS) or any(
            p["source"] != {"source": "local", "path": f"./{p['name']}"} for p in codex):
        raise ValueError("Codex marketplace must match both plugin names and local sources")
    if next(p for p in codex if p["name"] == "indaga-weekly")["policy"] != {"installation": "AVAILABLE"}:
        raise ValueError("Weekly Codex addon must not request separate authentication")
    for path, kind in (("indaga/.mcp.json", "http"), ("indaga/mcp.json", "streamable-http")):
        servers = read_json(path)["mcpServers"]
        if servers != {"indaga-public-workflows": {"type": kind, "url": "https://app.indaga.ai/v1/mcp/public-workflows"}}:
            raise ValueError("Only the credential-free hosted MCP endpoint is allowed")
    # Relative Markdown links must stay within the plugin (or root for the root README).
    for path in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md"),
                 *(p for plugin in PLUGINS for p in (ROOT / plugin).rglob("*.md"))]:
        boundary = next((ROOT / plugin for plugin in PLUGINS if path.is_relative_to(ROOT / plugin)), ROOT)
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


def build_skill_archives(output, version, plugin, members):
    receipts = {}
    required_contract = json.loads(members["references/compatibility.json"])["required_version"]
    connection_replacements = [
        ("Use this plugin's hosted Indaga MCP connection", "Use the existing hosted Indaga MCP connection"),
        ("Resolve the actual host-prefixed names", "This instruction-only skill pack does not register a connection or authenticate you.\nResolve the actual host-prefixed names"),
        ("this plugin needs a compatibility", "this skill pack needs a compatibility"),
        ("The record, recovery\nand labs procedures are contained in this main plugin. Weekly comparisons require\nthe separately installed Indaga Weekly plugin; if it is absent, tell the person to\ninstall it before using that procedure. Do not reproduce weekly instructions from\nthe tool inventory or another source.",
         "This installed procedure and its required references are contained in this skill pack.\nUse another workflow only if separately installed; otherwise explain the limit."),
        ("These three workflows make no writes", "This workflow makes no writes"),
        ("They do not import", "It does not import"),
        ("package does not narrow that grant", "skill pack does not narrow that grant"),
        ("MCP surface for these\nworkflows", "MCP surface for this\nworkflow"),
        ("these installed procedures", "this installed procedure"),
    ] if plugin == "indaga" else [
        ("This instruction-only Indaga Weekly plugin", "This instruction-only weekly skill pack"),
        ("This addon does not register", "This skill pack does not register"),
        ("Claude Code declares the main dependency in this addon's Claude manifest; host\ndependency installation does not prove that the main version or OAuth connection\nis ready. Codex and other hosts require the main plugin to be installed explicitly.",
         "Install the required main plugin explicitly; this skill pack does not declare\nor install a plugin dependency. Verify the main version and OAuth connection."),
        ("this plugin needs a compatibility", "this skill pack needs a compatibility"),
        ("contained in this addon", "contained in this skill pack"),
    ]
    connection, connection_changes = adapt(members["references/connection.md"].decode(), connection_replacements)
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
        sources = {"SKILL.md": f"{plugin}/{source}",
                   "references/connection.md": f"{plugin}/references/connection.md", "LICENSE": f"{plugin}/LICENSE"}
        for reference in ("evidence.md", "public-contract.json", "compatibility.json"):
            path = f"references/{reference}"
            contents[path] = members[path]
            sources[path] = f"{plugin}/{path}"
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
            "Upload a skill, then enable it. "
            + ("Install the required main plugin and authenticate its connection first.\n\n" if workflow == "weekly" else
               "Configure the hosted connector separately if it is not already present.\n\n") +
            f"Codex: extract the `{name}/` folder into your user or repository "
            "`.agents/skills/` directory without replacing an existing folder. Start a "
            f"new session and select `{name}`. "
            + (f"Install the compatible main Indaga plugin at `~{version}` and authenticate "
               "its connection first.\n\n" if workflow == "weekly" else "Configure the hosted connection separately.\n\n") +
            f"Canonical owner: `{plugin}`; see the contained connection guide. "
            "Use the plugin or a standalone copy of a given "
            "workflow to avoid duplicate instructions. Installation and directory "
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
            "kind": "instruction-only-skill", "skill": name, "plugin": plugin,
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
    output.mkdir(parents=True, exist_ok=True)
    plugins, skills, assets = {}, {}, []
    for plugin, workflows in PLUGINS.items():
        entries = git("ls-tree", "-r", "-z", "HEAD", "--", plugin).split(b"\0")
        members = {}
        for entry in filter(None, entries):
            metadata, name = entry.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            if mode != b"100644" or kind != b"blob":
                raise ValueError("Plugin archives may contain regular, non-executable files only")
            relative = name.decode().removeprefix(f"{plugin}/")
            members[relative] = git("cat-file", "blob", oid.decode())
        archive = output / f"{plugin}-{version}.zip"
        write_archive(archive, members)
        host_asset = output / f"{plugin}-{version}.plugin"
        host_asset.write_bytes(archive.read_bytes())
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        plugins[archive.name] = {
            "kind": "hosted-connection-plugin" if plugin == "indaga" else "instruction-only-plugin",
            "plugin": plugin, "skills": sorted(workflows), "sha256": digest,
            "plugin_asset": {"name": host_asset.name, "sha256": digest},
            "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(members.items())},
            "canonical_sources": {name: f"{plugin}/{name}" for name in sorted(members)},
            "transformations": {}, "generated_files": [],
        }
        assets.extend((archive, host_asset))
        skills.update(build_skill_archives(output, version, plugin, members))
    checksums = output / "SHA256SUMS"
    checksums.write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                                 for path in (*assets, *(output / name for name in skills))))
    receipt = {
        "version": version,
        "source_commit": git("rev-parse", "HEAD").decode().strip(),
        "plugin_archives": plugins,
        "skill_archives": skills,
    }
    (output / "release.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return output / f"indaga-{version}.zip"


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
