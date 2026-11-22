# RH port runs (ADB991)

Cloud runs port Alpöge's Lean archive to Lean 4.36 / Mathlib v4.36 (PORTING.md upstream).
One line per run, newest last: UTC start, packet, issue, PR, outcome.

## setup notes

(2026-11-22, run c075) alpo.ge, releases.lean-lang.org reachable now. elan's own toolchain download crashes (curl error in elan), so: download github.com/leanprover/lean4/releases/download/v4.36.0/lean-4.36.0-linux.zip (no zstd binary on box; use .zip), unzip, `elan toolchain link`. port_build.py prepare uses ELAN_HOME=WORK/elan, so link there too (ELAN_HOME=WORK/elan elan toolchain link ...) then rerun its remaining steps by hand: `lake update`, `lake exe cache get` in WORK/lean (cache works). gh: GraphQL is blocked, use `gh api` REST (search/issues needs is:issue or is:pr). In the shared checkout, `origin` = upstream: always push to remote `fork`.

(2026-11-22, run 0562) Retested: alpo.ge OK (parts download ~45 MB/s), github.com release zip OK. `elan toolchain install` still fails (CONNECT 403 on its download host): download https://github.com/leanprover/lean4/releases/download/v4.36.0/lean-4.36.0-linux.zip (no zstd on box, so not .tar.zst), unzip, move to WORK/elan/toolchains/leanprover--lean4---v4.36.0, then run the rest of prepare by hand (`lake update`, `lake exe cache get` with ELAN_HOME=WORK/elan XDG_CACHE_HOME=WORK/cache) -- cache get works.

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

- P0255 | https://github.com/rohanarun/alpoge-rh-replay/issues/32617 | ADB991-claude-20261122-c075 | claude/port-P0255-c075 (not pushed yet) | PR: none | last touched 2026-11-22T12:40Z | ready-only (51/64), check running

- P0244 | https://github.com/rohanarun/alpoge-rh-replay/issues/32669 | ADB991-claude-20261122-0562 | claude/port-P0244-0562 (not pushed yet) | PR: none | last touched 2026-11-22T12:41Z | ready-only (48/51), check running

- P0247 | https://github.com/rohanarun/alpoge-rh-replay/issues/32694 | ADB991-claude-20261122-9c49 | claude/port-P0247-9c49 (not pushed yet) | PR: none | last touched 2026-11-22T12:44Z | ready-only (37/40), setting up

- P0257 | https://github.com/rohanarun/alpoge-rh-replay/issues/32733 | ADB991-claude-20261122-ae30 | claude/port-P0257-ae30 (not pushed yet) | PR: none | last touched 2026-11-22T12:47Z | ready-only (47/51), setting up

## runs

- 2026-11-21T22:15Z ADB991-claude-20261121-7c3e: no packet, no claim. Hard blocker: alpo.ge blocked by sandbox network policy, archive cannot be fetched. Read docs/queue only (port.py next showed P0165/P0166/P0139... unclaimed partial depth-1 packets).

## for Andrea

- [resolved 2026-11-22: hosts added to the allowlist] 2026-11-21: Porting is blocked in this cloud environment: the network policy denies alpo.ge (and archive.org, releases.lean-lang.org, mathlib4.lean-cache.cloud). To unblock, add alpo.ge (and ideally releases.lean-lang.org + mathlib4.lean-cache.cloud) to the environment's allowed hosts, or provide an official mirror of the 14 parts. Nothing was claimed or posted upstream.

