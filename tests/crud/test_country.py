from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import app.crud.country as crud
from app.schemas.Country import CountryCreate, CountryUpdate
from tests.utils.load_countries import dummy_countries

def test_create_country(db: Session) -> None:
    for item in dummy_countries:
        country_in = CountryCreate(country_name=item['country_name'])
        country = crud.create_country(db, country=country_in)
        assert country.country_name == item['country_name']

def test_get_countries(db: Session) -> None:
    countries = crud.get_countries(db)
    assert countries

def test_get_country_by_id(db: Session) -> None:
    temp = crud.create_country(db, CountryCreate(country_name="BR"))
    country = crud.get_country_by_id(db, temp.id)
    assert country
    assert country.country_name == "BR"

def test_update_country(db: Session) -> None:
    temp = crud.create_country(db, CountryCreate(country_name="BR"))
    country_in = CountryUpdate(country_name='IT')
    country = crud.update_country(db, country_in, temp.id)
    assert country.country_name == 'IT'

def test_delete_country(db: Session) -> None:
    temp = crud.create_country(db, CountryCreate(country_name="BR"))
    country = crud.delete_country(db, temp.id)
    assert country.id == temp.id
    assert country.isdeleted == True