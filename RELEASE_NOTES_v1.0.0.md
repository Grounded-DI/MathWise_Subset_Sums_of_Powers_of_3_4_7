# v1.0.0 — Fixed Covering Certificate

Initial public release of the paper and replayable computational certificate for the fixed-case theorem:

```text
[582, infinity) is contained in A_1({3,4,7}).
```

Equivalently, every integer `n >= 582` is representable as a subset sum of distinct elements of

```text
B = {3^a : a >= 1} union {4^b : b >= 1} union {7^c : c >= 1}.
```

## Included files

```text
FINAL_SUBMISSION_MEMO.md
INITIAL_INTERVAL_REPLAY_PASS.log
PACKAGE_SHA256SUMS.txt
README_FOR_REVIEWERS.md
SUBMISSION_CHECKLIST.md
WEIGHTED_GAP_CERTIFICATE_REPLAY_PASS.log
WEIGHTED_GAP_CERTIFICATE_TABLES.md
cover_letter.md
paper.pdf
paper.tex
verify_initial_interval.py
verify_weighted_gap_certificates.py
```

## Replay

Run:

```bash
python3 verify_initial_interval.py
python3 verify_weighted_gap_certificates.py
```

Expected status:

```text
INITIAL INTERVAL CERTIFICATE: PASS
WEIGHTED GAP CERTIFICATE REPLAY | PASS
FINAL STATUS: PASS | WEIGHTED_GAP_PROVED
```

The weighted-gap replay eliminates all residue-admissible systems:

```text
Case A: initial = 1,361,889; final survivors = 0
Case B: initial = 255,938; final survivors = 0
Case C: initial = 1,501,666; final survivors = 0
Total residue-admissible systems checked = 3,119,493
```

## Scope limitations

This release proves only the fixed case `D = {3,4,7}`, `k = 1`.

No result is claimed for:

- other generating sets;
- `k != 1`;
- optimality of the endpoint `582`;
- density;
- asymptotics;
- classification.

## Certificate status

The certificate is locally replayed and replayable from the included files.

No independent third-party acceptance of the certificate is asserted in this release.

## Integrity

Use the included SHA-256 manifest:

```bash
sha256sum -c PACKAGE_SHA256SUMS.txt
```

On macOS:

```bash
shasum -a 256 -c PACKAGE_SHA256SUMS.txt
```

#Grounded-DI
