import pytest
from pydantic import ValidationError
from scraper.models import Listing

def make(**over):
    base = dict(id="1", price_raw="900 €", title="T2 Ajuda",
                detail=["T2", "75 m²"], tags=[], freguesia="ajuda")
    return Listing(**{**base, **over})

@pytest.mark.parametrize("raw, expected", [
    ("1.200 €/mês", 1200),
    ("950 €", 950),
    ("Sob consulta", None),
    ("", None),
])
def test_price_eur(raw, expected):
    assert make(price_raw=raw).price_eur == expected

@pytest.mark.parametrize("detail, rooms, sqm", [
    (["T2", "75 m²"], 2, 75),
    (["T0", "30 m²"], 0, 30),
    ([], None, None),
])
def test_rooms_sqm(detail, rooms, sqm):
    l = make(detail=detail)
    assert (l.rooms, l.sqm) == (rooms, sqm)

@pytest.mark.parametrize("over", [
    {"id": "  "}, {"title": ""},
    {"price_raw": "99999 €"}, {"price_raw": "50 €"},
])
def test_invalid(over):
    with pytest.raises(ValidationError):
        make(**over)
