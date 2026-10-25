"""Person B (24F-3084) - is_prime: boundary value analysis (BVA) + invalid input."""
import csv
from pathlib import Path

import pytest

from maths.prime_check import is_prime

pytestmark = [pytest.mark.prime, pytest.mark.person_b, pytest.mark.xdist_group("prime")]
DATA = Path(__file__).resolve().parents[2] / "data"


def _rows():
    with open(DATA / "prime_bva.csv", newline="") as f:
        return [pytest.param(r, id=r["tc_id"]) for r in csv.DictReader(f)]


@pytest.mark.csv_driven
@pytest.mark.bva
@pytest.mark.parametrize("row", _rows())
def test_is_prime_bva_from_csv(row):
    assert is_prime(int(row["number"])) is (row["expected"] == "True")


@pytest.mark.negative
@pytest.mark.parametrize(
    "bad", [-1, 5.5, "7", None], ids=["negative", "float", "string", "none"]
)
def test_invalid_input_raises_valueerror(bad):
    with pytest.raises(ValueError, match="only accepts positive integers"):
        is_prime(bad)
