import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import blended_rate, required_rate, mmk_with_split, mmk_full_black


def test_blended_rate():
    assert blended_rate(25, 2000, 3000) == 0.25 * 2000 + 0.75 * 3000


def test_required_rate():
    assert math.isclose(required_rate(3000, 25, 2100), 3300)
    assert required_rate(3000, 100, 2100) == float("inf")


def test_fee_application():
    usd = 100
    p1 = 25
    r1 = 2100
    r2 = 3000
    pct = 0.01
    mmk_split = mmk_with_split(usd, p1, r1, r2, pct_fee=pct)
    mmk_black = mmk_full_black(usd, r2, pct_fee=pct)
    assert math.isclose(mmk_split, 277500 - pct * (usd * 0.75) * r2)
    assert math.isclose(mmk_black, 300000 - pct * usd * r2)
