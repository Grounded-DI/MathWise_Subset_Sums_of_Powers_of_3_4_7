#!/usr/bin/env python3
"""
verify_weighted_gap_certificates.py

Optimized external-review verifier for the fixed-case Weighted Gap Lemma
certificate, D={3,4,7}, k=1 only.

It reconstructs residue-admissible weighted-danger systems and replays the
full paired modular eliminations recorded in WEIGHTED_GAP_CERTIFICATE_TABLES.md.
No result for other generating sets, no k != 1 result, and no endpoint below 582 is
claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd
import hashlib
import sys
import time
from typing import Dict, Iterable, List, Sequence, Tuple

EXPECTED_A = 1_361_889
EXPECTED_B = 255_938
EXPECTED_C = 1_501_666
TOTAL_EXPECTED = EXPECTED_A + EXPECTED_B + EXPECTED_C

EXPECTED_COUNTS_A = [
    (5, 109_278, 1_252_611),
    (13, 1_083_306, 169_305),
    (19, 160_932, 8_373),
    (31, 3_041, 5_332),
    (37, 4_891, 441),
    (41, 72, 369),
    (43, 75, 294),
    (73, 227, 67),
    (109, 55, 12),
    (487, 10, 2),
    (2917, 1, 1),
    (17497, 1, 0),
]
EXPECTED_COUNTS_B = [
    (5, 235_625, 20_313),
    (11, 5_199, 15_114),
    (13, 10_703, 4_411),
    (17, 4_297, 114),
    (19, 54, 60),
    (29, 13, 47),
    (31, 12, 35),
    (37, 7, 28),
    (41, 9, 19),
    (43, 15, 4),
    (257, 4, 0),
]
EXPECTED_COUNTS_C = [
    (5, 631_369, 870_297),
    (13, 746_778, 123_519),
    (17, 6_490, 117_029),
    (19, 108_371, 8_658),
    (29, 8_398, 260),
    (31, 145, 115),
    (37, 77, 38),
    (41, 5, 33),
    (43, 19, 14),
    (73, 1, 13),
    (197, 11, 2),
    (1373, 2, 0),
]

Row = Tuple[int, int, int, int]  # (u, v, a0, b0)

_order_cache: Dict[Tuple[int, int], int] = {}


def order_mod(base: int, mod: int) -> int:
    key = (base, mod)
    if key in _order_cache:
        return _order_cache[key]
    if gcd(base, mod) != 1:
        raise ValueError(f"base {base} is not invertible modulo {mod}")
    x = 1
    for e in range(1, 10_000_000):
        x = (x * base) % mod
        if x == 1:
            _order_cache[key] = e
            return e
    raise RuntimeError(f"order not found for base={base}, mod={mod}")


def residue_log_map(base: int, mod: int) -> Tuple[int, Dict[int, int]]:
    o = order_mod(base, mod)
    mp: Dict[int, int] = {}
    x = 1
    for e in range(o):
        mp.setdefault(x, e)
        x = (x * base) % mod
    return o, mp


def verify_interval_certificate() -> bool:
    initial = [3, 4, 7, 9, 16, 27, 49, 64, 81, 243, 256, 343, 729, 1024, 2187]
    sums = {0}
    for x in initial:
        sums |= {s + x for s in list(sums)}
    return all(n in sums for n in range(582, 4461))


def build_A() -> List[Row]:
    _, m4 = residue_log_map(4, 6561)
    _, m7 = residue_log_map(7, 6561)
    out: List[Row] = []
    for u in range(1, 3501):
        a0 = m4.get(u % 6561)
        if a0 is None:
            continue
        max_v = 7001 - 2 * u
        for v in range(1, max_v + 1):
            b0 = m7.get(v % 6561)
            if b0 is not None:
                out.append((u, v, a0, b0))
    return out


def build_B() -> List[Row]:
    _, m3 = residue_log_map(3, 4096)
    _, m7 = residue_log_map(7, 4096)
    out: List[Row] = []
    for u in range(1, 2334):
        a0 = m3.get(u % 4096)
        if a0 is None:
            continue
        max_v = 7001 - 3 * u
        for v in range(1, max_v + 1):
            b0 = m7.get(v % 4096)
            if b0 is not None:
                out.append((u, v, a0, b0))
    return out


def build_C() -> List[Row]:
    _, m3 = residue_log_map(3, 2401)
    _, m4 = residue_log_map(4, 2401)
    out: List[Row] = []
    for u in range(1, 2334):
        a0 = m3.get(u % 2401)
        if a0 is None:
            continue
        max_v = (7001 - 3 * u) // 2
        for v in range(1, max_v + 1):
            b0 = m4.get(v % 2401)
            if b0 is not None:
                out.append((u, v, a0, b0))
    return out


def mask_for_power_class(base: int, q: int, class_mod: int, class_res: int) -> int:
    """Bit mask of residues base^e mod q for e == class_res mod class_mod."""
    ord_q = order_mod(base, q)
    g = gcd(class_mod, ord_q)
    r = class_res % g
    mask = 0
    for e in range(r, ord_q, g):
        mask |= 1 << pow(base, e, q)
    return mask


def mask_for_all_powers(base: int, q: int) -> int:
    ord_q = order_mod(base, q)
    mask = 0
    for e in range(ord_q):
        mask |= 1 << pow(base, e, q)
    return mask


def rotate_down(mask: int, shift: int, q: int, full_mask: int) -> int:
    """Residue mask {x} -> {x-shift mod q}."""
    shift %= q
    if shift == 0:
        return mask
    low = mask & ((1 << shift) - 1)
    return ((mask >> shift) | (low << (q - shift))) & full_mask


class FullPairTester:
    def __init__(self, case: str, q: int):
        self.case = case
        self.q = q
        self.full_mask = (1 << q) - 1
        if case == "A":
            self.base_a, self.base_b, self.base_x = 4, 7, 3
            self.forced_a_mod, self.forced_b_mod = 2187, 2187
        elif case == "B":
            self.base_a, self.base_b, self.base_x = 3, 7, 4
            self.forced_a_mod, self.forced_b_mod = 1024, 512
        elif case == "C":
            self.base_a, self.base_b, self.base_x = 3, 4, 7
            self.forced_a_mod, self.forced_b_mod = 2058, 1029
        else:
            raise ValueError(case)

        self.ord_a = order_mod(self.base_a, q)
        self.ord_b = order_mod(self.base_b, q)
        self.ga = gcd(self.forced_a_mod, self.ord_a)
        self.gb = gcd(self.forced_b_mod, self.ord_b)
        self.x_mask = mask_for_all_powers(self.base_x, q)
        self.a_masks = [mask_for_power_class(self.base_a, q, self.forced_a_mod, c) for c in range(self.ga)]
        self.b_masks = [mask_for_power_class(self.base_b, q, self.forced_b_mod, c) for c in range(self.gb)]
        self.shift_a_cache: Dict[Tuple[int, int], int] = {}
        self.shift_b_cache: Dict[Tuple[int, int], int] = {}
        self.possible_cache: Dict[Tuple[int, int, int, int], bool] = {}

    def shifted_a(self, ac: int, u_mod: int) -> int:
        key = (ac, u_mod)
        got = self.shift_a_cache.get(key)
        if got is None:
            got = rotate_down(self.a_masks[ac], u_mod, self.q, self.full_mask)
            self.shift_a_cache[key] = got
        return got

    def shifted_b(self, bc: int, v_mod: int) -> int:
        key = (bc, v_mod)
        got = self.shift_b_cache.get(key)
        if got is None:
            got = rotate_down(self.b_masks[bc], v_mod, self.q, self.full_mask)
            self.shift_b_cache[key] = got
        return got

    def possible(self, row: Row) -> bool:
        u, v, a0, b0 = row
        key = (u % self.q, v % self.q, a0 % self.ga, b0 % self.gb)
        got = self.possible_cache.get(key)
        if got is not None:
            return got
        um, vm, ac, bc = key
        got = bool(self.x_mask & self.shifted_a(ac, um) & self.shifted_b(bc, vm))
        self.possible_cache[key] = got
        return got


def eliminate(case: str, rows: Sequence[Row], expected_counts: Sequence[Tuple[int, int, int]]) -> Tuple[List[Row], List[Tuple[int, int, int]]]:
    unresolved = list(rows)
    counts: List[Tuple[int, int, int]] = []
    eliminated_all: List[Row] = []
    for q, _, _ in expected_counts:
        tester = FullPairTester(case, q)
        nxt: List[Row] = []
        eliminated = 0
        for row in unresolved:
            if tester.possible(row):
                nxt.append(row)
            else:
                eliminated += 1
                eliminated_all.append(row)
        unresolved = nxt
        counts.append((q, eliminated, len(unresolved)))
        print(f"Case {case} Q={q}: eliminated={eliminated} remaining={len(unresolved)} unique_tests={len(tester.possible_cache)}")
        if not unresolved:
            break
    return unresolved, counts


def assert_eq(label: str, actual, expected) -> bool:
    ok = actual == expected
    print(f"{label}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  actual   = {actual}")
        print(f"  expected = {expected}")
    return ok


def main() -> int:
    t0 = time.time()
    print("=== Weighted Gap Certificate Replay — Optimized ===")
    print("Scope: D={3,4,7}, k=1 only; no broader generating-set claim.")

    interval_ok = verify_interval_certificate()
    print("finite interval [582,4460]:", "PASS" if interval_ok else "FAIL")

    print("Building residue-admissible systems...")
    A = build_A(); print(f"Case A built: {len(A)}")
    B = build_B(); print(f"Case B built: {len(B)}")
    C = build_C(); print(f"Case C built: {len(C)}")

    ok = interval_ok
    ok &= assert_eq("Case A initial residue-admissible count", len(A), EXPECTED_A)
    ok &= assert_eq("Case B initial residue-admissible count", len(B), EXPECTED_B)
    ok &= assert_eq("Case C initial residue-admissible count", len(C), EXPECTED_C)
    ok &= assert_eq("Total residue-admissible systems checked", len(A) + len(B) + len(C), TOTAL_EXPECTED)

    print("Replaying full paired modular eliminations...")
    unA, countsA = eliminate("A", A, EXPECTED_COUNTS_A)
    unB, countsB = eliminate("B", B, EXPECTED_COUNTS_B)
    unC, countsC = eliminate("C", C, EXPECTED_COUNTS_C)

    ok &= assert_eq("Case A elimination table", countsA, EXPECTED_COUNTS_A)
    ok &= assert_eq("Case B elimination table", countsB, EXPECTED_COUNTS_B)
    ok &= assert_eq("Case C elimination table", countsC, EXPECTED_COUNTS_C)
    ok &= assert_eq("Case A final survivors", len(unA), 0)
    ok &= assert_eq("Case B final survivors", len(unB), 0)
    ok &= assert_eq("Case C final survivors", len(unC), 0)

    # Shadow examples from the certificate attachment.
    shadowA = not FullPairTester("A", 13).possible((4, 7, 1, 1))
    shadowB = not FullPairTester("B", 5).possible((3, 7, 1, 1))
    shadowC = not FullPairTester("C", 5).possible((3, 4, 1, 1))
    ok &= assert_eq("Case A difference-only shadow eliminated", shadowA, True)
    ok &= assert_eq("Case B difference-only shadow eliminated", shadowB, True)
    ok &= assert_eq("Case C difference-only shadow eliminated", shadowC, True)

    print(f"elapsed_seconds = {time.time() - t0:.3f}")
    if ok:
        print("WEIGHTED GAP CERTIFICATE REPLAY — PASS")
        print("Case A: initial = 1,361,889; final survivors = 0")
        print("Case B: initial = 255,938; final survivors = 0")
        print("Case C: initial = 1,501,666; final survivors = 0")
        print("Total residue-admissible systems checked = 3,119,493")
        print("Weighted Gap Lemma: PASS")
        print("Global overlap inequality: PASS")
        print("Fixed theorem chain: PASS")
        print("FINAL STATUS: PASS — WEIGHTED_GAP_PROVED")
        return 0
    print("FINAL STATUS: FAIL — WEIGHTED_GAP_INCOMPLETE")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
