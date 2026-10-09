#!/usr/bin/env python3
"""Validate portable files against reviewed, pinned official schemas."""
import hashlib
import json
import re
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parent.parent
schemas = {
    "plugin": "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883",
    "mcp": "6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb",
}
for name, expected in schemas.items():
    url = f"https://agent-plugins.org/schemas/1.0.0/{name}.schema.json"
    request = urllib.request.Request(url, headers={
        "User-Agent": "Indaga public plugin schema validator (support@indaga.ai)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(256 * 1024 + 1)
    if len(data) > 256 * 1024 or hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit(f"Reviewed {name} schema changed; inspect before updating its digest")
    validator = Draft202012Validator(json.loads(data))
    for plugin in ("indaga", "indaga-weekly") if name == "plugin" else ("indaga",):
        validator.validate(json.loads((root / f"{plugin}/{name}.json").read_text()))
        print(f"{plugin}/{name}: official schema passed")

contract = json.loads((root / "indaga/references/public-contract.json").read_text())
for operation, entry in contract["operations"].items():
    Draft202012Validator.check_schema(entry["input_schema"])
for skill in (p for plugin in ("indaga", "indaga-weekly") for p in (root / plugin / "skills").glob("*/SKILL.md")):
    calls = re.findall(r'`([a-z._]+)\((\{[^\n]+\})\)`', skill.read_text())
    for operation, arguments in calls:
        Draft202012Validator(contract["operations"][operation]["input_schema"]).validate(json.loads(arguments))
    print(f"{skill.parent.name}: documented calls satisfy public input schemas")
