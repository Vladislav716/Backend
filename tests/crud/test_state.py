from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import app.crud.country as crud_country
import app.crud.state as crud
from app.schemas.State import StateCreate, StateUpdate
from app.schemas.Country import CountryCreate, CountryUpdate
from tests.utils.load_states import dummy_states

def test_create_state(db: Session) -> None:
    for item in dummy_states:
        country = crud_country.create_country(db, CountryCreate(country_name="UK"))
        state_in = StateCreate(state_name=item['state_name'],country_id=country.id)
        state = crud.create_state(db, state=state_in)
        assert state
        assert state.state_name == item['state_name']
        assert state.country_id == country.id

def test_get_states(db: Session) -> None:
    states = crud.get_states(db)
    assert states

def test_get_state_by_id(db: Session) -> None:
    country = crud_country.create_country(db, CountryCreate(country_name="UK"))
    temp = crud.create_state(db, StateCreate(state_name="London",country_id=country.id))
    state = crud.get_state_by_id(db, temp.id)
    assert state
    assert state.state_name == "London"
    assert state.country_id == country.id

def test_update_state(db: Session) -> None:
    country = crud_country.create_country(db, CountryCreate(country_name="UK"))
    temp = crud.create_state(db, StateCreate(state_name="London", country_id=country.id))
    state_in = StateUpdate(state_name='Scotland', country_id=country.id)
    state = crud.update_state(db, state_in, temp.id)
    assert state
    assert state.state_name == 'Scotland'
    assert state.country_id == country.id

def test_delete_state(db: Session) -> None:
    country = crud_country.create_country(db, CountryCreate(country_name="UK"))
    temp = crud.create_state(db, StateCreate(state_name="London", country_id=country.id))
    state = crud.delete_state(db, temp.id)
    assert state.id == temp.id
    assert state.isdeleted == True
    assert state.country_id == country.id