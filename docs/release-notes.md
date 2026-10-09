Three contained read-only workflows in the main Indaga plugin: record, recovery
and labs, with the hosted connection. Indaga Weekly is a separately installed
instruction-only plugin. Install using the repository README or versioned assets.

Version 0.2.7 keeps inventory routing hints separate from focused producer
results and prefers absolute returned dates over conflicting relative wording.
Recovery-only requests do not read a training ceiling. Recovery and ceiling dates
come only from their own producer; an undated ceiling remains undated. Unsupported
clinical clearance, diagnosis, prescription/dosing, foreign-account and mutation
requests are checked before connection/context reads. Recovery and labs metadata
exclude pure clinical requests; supported own-record explanations remain bounded
reads. Both connection guides and standalone packs carry the same intent boundary.

Main still contains record/recovery/labs and the sole public connection; weekly
remains a separately installed instruction-only plugin with compatible main
`~0.2.7`. Weekly and labs focused procedural bodies, shared evidence, six hosted
tools, public contract and broad OAuth grant remain unchanged. This repair does
not establish native acceptance or directory eligibility by packaging alone.

Version 0.2.6 moves the unchanged weekly procedure to its own plugin with contained
references, license, icons and host manifests. Main no longer bundles weekly
instructions. Weekly requires compatible installed main `~0.2.6` and its
authenticated public connection. Claude declares the supported dependency;
Codex requires main to be installed explicitly. Weekly registers no MCP server
and performs no separate authentication. Both plugin ZIP/.plugin pairs and all
four standalone skill ZIPs are built from their actual source owners with exact
file, archive and transformation receipts. Contract-update proposals keep both
reference copies, versions and the Claude dependency minimum together.

The hosted six-tool inventory, including weekly.delta, public contract and broad
OAuth grant remain unchanged. All four procedural bodies, including the 0.2.5
recovery correction, are preserved. Modular distribution does not establish
health-use eligibility, directory approval or native acceptance.

Version 0.2.5 keeps incomplete recovery flags and counts from being interpreted
as an all-clear result. Recovery answers lead with the returned state, dated
coverage and blocking reason. A minimum paired-day threshold does not predict
when calibration will finish. Training-ceiling requirements come only from the
ceiling operation itself; an unavailable ceiling does not support a personal
workload or effort recommendation. The optional recovery pack carries the same
canonical repair. Hosted tools, permissions and public contract are unchanged.

Version 0.2.4 points all host manifests and installation links to the fresh public
release mirror, `indaga-ai/indaga-plugins`. Runtime procedures, evidence, hosted
tools, contract and permission disclosures are unchanged from 0.2.3. Private
review history is not included in the public mirror. Publication and native
acceptance remain separate from preparing this candidate.

Version 0.2.3 uses OpenAI's supported `Healthcare` listing category and three
starter prompts covering the same four workflows. The procedures, permissions,
hosted endpoint and public contract remain unchanged. These metadata corrections
do not establish OpenAI health-use eligibility or directory approval.

Version 0.2.2 names the bundled connection `indaga-public-workflows` so a legacy
global `indaga` server cannot hide it in Codex. The hosted endpoint, read tools,
workflow procedures and public contract remain unchanged.

Version 0.2.1 declares the existing Indaga icon and privacy policy for Anthropic's
directory. Its new package version lets hosts refresh previously installed 0.2.0
metadata. The workflow procedures and required public contract remain unchanged.

The ZIP and `.plugin` files contain identical bytes. `SHA256SUMS` verifies those
artifacts; `release.json` records the public source commit and packaged file hashes.
Directory approval and host/account availability are separate from this release.

## Supplemental standalone skills

The 0.2.4 release build also provides optional record, weekly, recovery and labs
skill ZIPs for an existing hosted connection. Each contains its own instructions
and references, with no MCP registration or account credentials. Selecting a
workflow does not narrow the OAuth grant. The complete starter's runtime behavior is
unchanged. Custom installation and public-directory eligibility remain separate;
this packaging change does not establish approval or new native acceptance.
