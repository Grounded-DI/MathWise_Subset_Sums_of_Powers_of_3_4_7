License

The verifier source code in this repository is released under the MIT License.

The paper, certificate tables, replay logs, README materials, submission notes, and other non-code documentation are released under the Creative Commons Attribution 4.0 International License (CC BY 4.0), unless otherwise stated.

SPDX:
- Code: MIT
- Documentation and paper materials: CC-BY-4.0

# A Fixed Covering Certificate for Subset Sums of Powers of 3, 4, and 7

This repository contains the paper and replayable computational certificate for the fixed-case theorem:

```text
[582, infinity) is contained in A_1({3,4,7}).
```

Equivalently, every integer `n >= 582` is representable as a subset sum of distinct elements of

```text
B = {3^a : a >= 1} union {4^b : b >= 1} union {7^c : c >= 1}.
```

## Contents

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

## Paper

- Title: **A Fixed Covering Certificate for Subset Sums of Powers of 3, 4, 7**
- Version: `v1.0.0`
- Status: fixed-case certificate package
- Scope: fixed case `D = {3,4,7}`, `k = 1`

## Replay instructions

The package contains two replayable checks.

```bash
python3 verify_initial_interval.py
python3 verify_weighted_gap_certificates.py
```

Expected terminal status:

```text
INITIAL INTERVAL CERTIFICATE: PASS
WEIGHTED GAP CERTIFICATE REPLAY | PASS
FINAL STATUS: PASS | WEIGHTED_GAP_PROVED
```

The weighted-gap verifier checks three finite residue-admissible systems and eliminates all survivors:

```text
Case A: initial = 1,361,889; final survivors = 0
Case B: initial = 255,938; final survivors = 0
Case C: initial = 1,501,666; final survivors = 0
Total residue-admissible systems checked = 3,119,493
```

## Integrity check

A SHA-256 manifest is included:

```bash
sha256sum -c PACKAGE_SHA256SUMS.txt
```

On macOS, use:

```bash
shasum -a 256 -c PACKAGE_SHA256SUMS.txt
```

If any source file, log file, or PDF is regenerated, regenerate `PACKAGE_SHA256SUMS.txt`.

## Scope limitations

This release proves only the fixed case `D = {3,4,7}`, `k = 1`.

It does **not** claim:

- that `582` is the least possible endpoint;
- any result for other generating sets;
- any result for `k != 1`;
- any density theorem;
- any asymptotic theorem;
- any classification theorem.

## Certificate status

The certificate is locally replayed and replayable from the included files.

No independent third-party acceptance of the certificate is asserted in this repository.

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

See [`README.md`].
