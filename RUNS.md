# RH port runs (ADB991)

Cloud runs port Alpöge's Lean archive to Lean 4.36 / Mathlib v4.36 (PORTING.md upstream).
One line per run, newest last: UTC start, packet, issue, PR, outcome.

## setup notes

(2026-11-22) Andrea added alpo.ge, releases.lean-lang.org and mathlib4.lean-cache.cloud to the environment's network allowlist after the first run. Retest them before treating any as blocked.

(2026-11-21, run ADB991-claude-20261121-7c3e) Cloud sandbox: 4 vCPU, 15 GB RAM, ~60 GB free disk.
- BLOCKED by proxy (CONNECT 403): alpo.ge (archive parts, the only official source), web.archive.org / archive.org,
  huggingface.co, releases.lean-lang.org (elan's default toolchain origin), mathlib4.lean-cache.cloud.
- Works: raw.githubusercontent.com (elan-init.sh installs elan fine), github.com release downloads
  (lean-4.36.0-linux.tar.zst reachable -> use `elan toolchain link`), lakecache.blob.core.windows.net (responds), zenodo.org.
- No official mirror of the archive parts found (upstream has no releases; nothing in repo docs). Third-party GitHub copies
  exist but are outside this session's repo scope and unofficial, so not used.
- Only one clone is checked out (upstream); fork is reached as remote `fork` in the same checkout.

## open

(none)

## runs

- 2026-11-21T22:15Z ADB991-claude-20261121-7c3e: no packet, no claim. Hard blocker: alpo.ge blocked by sandbox network policy, archive cannot be fetched. Read docs/queue only (port.py next showed P0165/P0166/P0139... unclaimed partial depth-1 packets).

## for Andrea

- [resolved 2026-11-22: hosts added to the allowlist] 2026-11-21: Porting is blocked in this cloud environment: the network policy denies alpo.ge (and archive.org, releases.lean-lang.org, mathlib4.lean-cache.cloud). To unblock, add alpo.ge (and ideally releases.lean-lang.org + mathlib4.lean-cache.cloud) to the environment's allowed hosts, or provide an official mirror of the 14 parts. Nothing was claimed or posted upstream.

