import pytest
from pydantic import ValidationError

from scraper.models import Listing
from scraper.parser import get_listings, parse_listings


def make(**over):
    base = dict(
        id_raw="1",
        price_raw="900 €",
        title_raw="T2 Ajuda",
        detail_raw=["T2", "75 m²"],
        tags_raw=[],
        freguesia_raw="ajuda",
    )
    return Listing(**{**base, **over})


def test_price_simple():
    listing = make(price_raw="1.200 €/mês")
    assert listing.price == 1200


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1.200 €/mês", 1200),
        ("Sob consulta", None),
        ("40.200 €/mês", 40200),
    ],
)
def test_price(raw, expected):
    assert make(price_raw=raw).price == expected


@pytest.mark.parametrize(
    "detail, rooms, sqm",
    [
        (["T2", "75 m²"], 2, 75),
        (["30 m²"], None, 30),
        (["T6"], 6, None),
    ],
)
def test_rooms_sqm(detail, rooms, sqm):
    listing = make(detail_raw=detail)
    assert (listing.rooms, listing.sqm) == (rooms, sqm)  # compare both at once


@pytest.mark.parametrize(
    "over",
    [
        {"id_raw": "  "},  # blank after str_strip_whitespace
        {"title_raw": "  "},
        {"price_raw": "80.200 €/mês"},  # too high
        {"price_raw": "40 €/mês"},  # too low
    ],
)
def test_invalid(over):
    with pytest.raises(ValidationError):
        make(**over)


def test_parsed_listings_are_valid(lisboa_ajuda_page1):
    container = get_listings(lisboa_ajuda_page1)
    rows = parse_listings(container, freguesia="ajuda")
    for d in rows:
        renamed = {
            f"{k}_raw": v for k, v in d.items()
        }  # id -> id_raw, price -> price_raw, ...
        listing = Listing(**renamed)
        print(listing.detail_raw, listing.rooms, listing.sqm)
