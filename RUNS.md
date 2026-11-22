# RH port runs (ADB991)

Cloud runs port Alpöge's Lean archive to Lean 4.36 / Mathlib v4.36 (PORTING.md upstream).
One line per run, newest last: UTC start, packet, issue, PR, outcome.

## setup notes

(2026-11-22, run ae30) Simplest path: install elan normally, download+unzip github.com/leanprover/lean4/releases/download/v4.36.0/lean-4.36.0-linux.zip to ~/dl, then put a tiny `elan` shim first on PATH that turns `elan toolchain install leanprover/lean4:v4.36.0` into `cp -a ~/dl/lean-4.36.0-linux $ELAN_HOME/toolchains/leanprover--lean4---v4.36.0` and execs the real elan otherwise. Then `port_build.py prepare WORK` runs unmodified end to end (parts from alpo.ge, lake update, cache get): ~4 min, 13 GB.

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

- P0255 | https://github.com/rohanarun/alpoge-rh-replay/issues/32617 | ADB991-claude-20261122-c075 | claude/port-P0255-c075 | PR: https://github.com/rohanarun/alpoge-rh-replay/pull/32858 | last touched 2026-11-22T13:04Z | partial: 51/64 submitted (3 fixed). Remaining 13 wait on unported imports: M073020(M073019) M073199(M073198) M073440(M073439) M073627(M073622) M073944(M073943) M073954,M074096(M073087) M074333(M005405) M074725(M072653,M073087) M074760(M074759) M075004(M075003) M075062(M073087,M075061) M075296(M004836,M075295). Next run: watch PR review/CI; once imports land, add members to this PR (one open submission per packet) or follow up after merge.

- P0244 | https://github.com/rohanarun/alpoge-rh-replay/issues/32669 | ADB991-claude-20261122-0562 | claude/port-P0244-0562 (pushed; evidence on claude/evidence-P0244-0562 @1abb1d5) | PR: https://github.com/rohanarun/alpoge-rh-replay/pull/33370 (partial, 48/51 live) | last touched 2026-11-22T14:30Z | partial PR open; claim kept open per PORTING.md. CI runs 'Port build check' and 'Validate tracker data' are action_required (need maintainer approval for fork PRs). Remaining live: M029428 (needs M037822), M031611 (needs M031610), M031671 (needs M031670). Next run: watch #33370 for review/CI; once imports land, port the 3 and add to the PR or a follow-up after merge. Build tree /home/user/work is ephemeral.

- P0247 | https://github.com/rohanarun/alpoge-rh-replay/issues/32694 | ADB991-claude-20261122-9c49 | claude/port-P0247-9c49 (pushed) | PR: https://github.com/rohanarun/alpoge-rh-replay/pull/33115 (partial, 37/40) | last touched 2026-11-22T13:30Z | awaiting review. Remaining M046414 (needs M037822), M046803 (needs M046802), M046864 (needs M056084): once those land, add to a follow-up PR after #33115 merges; keep claim open. Evidence branch claude/evidence-P0247-9c49. Build tree at /home/user/WORK is ephemeral.

- P0257 | https://github.com/rohanarun/alpoge-rh-replay/issues/32733 | ADB991-claude-20261122-ae30 | claude/port-P0257-ae30 (pushed; evidence on claude/evidence-P0257-ae30) | PR: https://github.com/rohanarun/alpoge-rh-replay/pull/33101 | last touched 2026-11-22T13:29Z | partial PR open (47/51 live members); claim kept open per PORTING.md. Remaining live: M087488 (needs M005459, M087487), M092132 (needs M005127), M092279 (needs M092278), M093011 (needs M005127). Next run: watch #33101 for review/CI; once those imports land, port the 4 and add to the PR or a follow-up

## runs

- 2026-11-21T22:15Z ADB991-claude-20261121-7c3e: no packet, no claim. Hard blocker: alpo.ge blocked by sandbox network policy, archive cannot be fetched. Read docs/queue only (port.py next showed P0165/P0166/P0139... unclaimed partial depth-1 packets).
- 2026-11-22T12:30Z ADB991-claude-20261122-c075: claimed P0255 (#32617); ready-only 51/64; fixed M073366 (prod_le_prod₀ rename), M073400 (show for inter_mem), M074311 (noncomputable abbrevs, note); audits 0 hits; reproduce 51/51; PR #32858 opened via bridge. CI had no check runs at time of posting.
- 2026-11-22T12:45Z ADB991-claude-20261122-ae30: P0257 claim #32733; 47 ready members built (5 patched: M086136 M086328 M088129 M090000 M090566; 42 unchanged), audits 0 hits, reproduce 47/47; partial PR #33101 opened 2026-11-22T13:29Z. CI is action_required (fork workflows need maintainer approval).
- 2026-11-22T12:41Z ADB991-claude-20261122-9c49: claimed P0247 (#32694); ready-only 37/40: 34 unchanged, 3 fixed (Sheaf .val->.obj; prod_le_one->prod_le_one₀ + contDiff_apply family arg; MultilinearMap (RingHom.id B)). reproduce 37/37 ok, IsLattice/reused audits 0 hits. Opened PR #33115. Setup notes from run 0562 worked as written (zip + manual lake update/cache get); check+reproduce ~20 min each at LEAN_NUM_THREADS=2.
- 2026-11-22T12:35Z ADB991-claude-20261122-0562: P0244 claimed (#32669); 48 ready members built (5 fixed: M030864 M031267 M032080 M033044 M033460; 43 unchanged); reused/IsLattice audits 0 hits; reproduce 48/48; partial PR #33370 opened 14:28Z. Note: Lake has no -j flag; during the first check the import-closure build briefly ran 3-4 Lean processes before I set LEAN_NUM_THREADS=2 for later steps (reproduce stayed <=2).

## for Andrea

- [resolved 2026-11-22: hosts added to the allowlist] 2026-11-21: Porting is blocked in this cloud environment: the network policy denies alpo.ge (and archive.org, releases.lean-lang.org, mathlib4.lean-cache.cloud). To unblock, add alpo.ge (and ideally releases.lean-lang.org + mathlib4.lean-cache.cloud) to the environment's allowed hosts, or provide an official mirror of the 14 parts. Nothing was claimed or posted upstream.
- 2026-11-22 (ae30): PR #33101 (Port P0257 partial, 47 modules) is open; its CI runs await a maintainer's workflow approval. Claim #32733 stays open while 4 members wait on imports (M005459, M087487, M005127, M092278); close it if you'd rather not hold the packet.
- 2026-11-22 (run 0562): PR #33370 (Port P0244, partial 48/51) is open; its CI workflows show action_required (maintainer must approve fork workflows). No action needed from you unless a maintainer asks.
