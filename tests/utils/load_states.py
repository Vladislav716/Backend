import json

def read_states():
    with open('data/states.json') as stream:
        countries = json.load(stream)
    return countries

dummy_states = read_states()