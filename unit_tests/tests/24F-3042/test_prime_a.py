"""Person A (24F-3042) - is_prime: equivalence class partitioning (ECP)."""
import csv
from pathlib import Path

import pytest

from maths.prime_check import is_prime

pytestmark = [pytest.mark.prime, pytest.mark.person_a, pytest.mark.xdist_group("prime")]
DATA = Path(__file__).resolve().parents[2] / "data"


@pytest.mark.smoke
def test_two_is_prime():
    assert is_prime(2) is True


@pytest.mark.scenario
def test_primes_below_50_match_known_list():
    known = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    assert [n for n in range(50) if is_prime(n)] == known


def _rows():
    with open(DATA / "prime_ecp.csv", newline="") as f:
        return [pytest.param(r, id=r["tc_id"]) for r in csv.DictReader(f)]


@pytest.mark.csv_driven
@pytest.mark.ecp
@pytest.mark.parametrize("row", _rows())
def test_is_prime_ecp_from_csv(row):
    assert is_prime(int(row["number"])) is (row["expected"] == "True")
