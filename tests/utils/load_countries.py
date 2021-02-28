import json

def read_countries():
    with open('data/countries.json') as stream:
        countries = json.load(stream)
    return countries

dummy_countries = read_countries()