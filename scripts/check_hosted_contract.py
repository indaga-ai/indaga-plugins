#!/usr/bin/env python3
"""Bounded anonymous contract check/update. Never download workflow instructions."""
import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://app.indaga.ai/v1/public-contract"
PUBLIC_KEYS = {"format", "mcp_url", "operations", "result_contract", "supported_versions", "version", "workflows"}
OPERATIONS = {"indaga.describe_context", "weekly.delta", "recovery.state",
              "decision.ceiling", "labs.query", "labs.panel_coverage"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, target):
        raise ValueError("Contract endpoint redirected; review the hosted route before contacting a new target")


def admit(contract):
    if not isinstance(contract, dict) or set(contract) != PUBLIC_KEYS:
        raise ValueError("Unexpected public contract fields; inspect the projection manually")
    if contract["format"] != "indaga-public-workflows-v1":
        raise ValueError("Unsupported public contract format")
    if contract["mcp_url"] != "https://app.indaga.ai/v1/mcp/public-workflows":
        raise ValueError("Public contract must describe the hosted MCP endpoint")
    if set(contract["operations"]) != OPERATIONS:
        raise ValueError("Changed public operation inventory requires manual review")
    if set(contract["workflows"]) != {"record", "weekly", "recovery", "labs"}:
        raise ValueError("Changed public workflow inventory requires manual review")
    if not re.fullmatch(r"\d+\.\d+\.\d+", contract["version"]):
        raise ValueError("Invalid public contract version")
    if not isinstance(contract["supported_versions"], list) or any(
            not isinstance(v, str) or not re.fullmatch(r"\d+\.\d+\.\d+", v)
            for v in contract["supported_versions"]):
        raise ValueError("Invalid supported versions")
    for operation in contract["operations"].values():
        if not isinstance(operation, dict) or set(operation) != {"input_schema"}:
            raise ValueError("Unexpected operation projection")
        schema = operation["input_schema"]
        if not isinstance(schema, dict) or "public_contract" not in schema.get("required", []):
            raise ValueError("Public tools must require a version before personal reads")
        if schema.get("additionalProperties") is not False:
            raise ValueError("Public tools must reject undeclared arguments")
    return contract


def fetch():
    request = urllib.request.Request(URL, headers={
        "User-Agent": "Indaga public contract checker (support@indaga.ai)",
        "Accept": "application/json",
    })
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
        if response.url != URL:
            raise ValueError("Contract endpoint redirected; review the hosted route")
        data = response.read(128 * 1024 + 1)
    if len(data) > 128 * 1024:
        raise ValueError("Contract response exceeds 128 KiB")
    return admit(json.loads(data))


def compatible(contract):
    installed = json.loads((ROOT / "indaga/references/compatibility.json").read_text())
    if installed["format"] != contract["format"] or installed["required_version"] not in contract["supported_versions"]:
        raise ValueError("Hosted contract no longer supports installed workflows; review a new client version")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="Write projection for a reviewable PR only")
    args = parser.parse_args()
    try:
        contract = fetch()
        local = ROOT / "indaga/references/public-contract.json"
        if args.update:
            if json.loads(local.read_text()) == contract:
                print("Public contract unchanged")
                return
            local.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
            # A changed packaged projection needs an explicit new client release.
            version_path = ROOT / "indaga/plugin.json"
            old = json.loads(version_path.read_text())["version"]
            major, minor, patch = map(int, old.split("."))
            new = f"{major}.{minor}.{patch + 1}"
            for relative in ("indaga/plugin.json", "indaga/.claude-plugin/plugin.json",
                             "indaga/.codex-plugin/plugin.json", ".claude-plugin/marketplace.json"):
                path = ROOT / relative
                value = json.loads(path.read_text())
                if relative.endswith("marketplace.json"):
                    value["plugins"][0]["version"] = new
                else:
                    value["version"] = new
                path.write_text(json.dumps(value, indent=2) + "\n")
            for relative in ("README.md", "indaga/README.md"):
                path = ROOT / relative
                path.write_text(path.read_text().replace(f"`{old}`", f"`{new}`"))
            print(f"Proposed public contract projection update and plugin {new}; review required")
        else:
            compatible(contract)
            print("Hosted server supports the installed public contract")
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        parser.exit(1, f"Contract check rejected: {error}\n")


if __name__ == "__main__":
    main()
