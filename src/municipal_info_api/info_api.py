import os

import requests

import sparql_queries

FUSEKI_HOST = os.environ.get('FUSEKI_NETWORK_HOST', 'fuseki')
FUSEKI_PORT = os.environ.get('FUSEKI_NETWORK_PORT', '3030')
db_url = f'http://{FUSEKI_HOST}:{FUSEKI_PORT}/ds/query'


class Person:
    def __init__(self, name=None, phone=None, email=None, department=None, title=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.department = department
        self.title = title


class WasteBinInfo:
    def __init__(self, start_time=None, end_time=None, place=None, place_prep=None):
        self.start_time = start_time
        self.end_time = end_time
        self.place = place
        self.place_prep = place_prep


def get_all_names() -> list:
    query = sparql_queries.get_all_names_query()
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        contacts.append(r['name']['value'])
    return contacts


def get_valid_subjects() -> list:
    query = sparql_queries.get_all_roles_query()
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        contacts.append(r['role']['value'])
    return contacts




def get_info_for_contact(contact: str) -> list:
    """Find the contact info for persons that match 'contact'. First, we try to find a match of the 'contact'
     as is, either a first name, first names or a full name. If nothing is found, we check if the 'contact'
     is missing a middle name or abbreviating it, e.g. 'Anna Árnadóttir' should give us results
     for 'Anna Jóna Árnadóttir', as should 'Anna J. Árnadóttir'."""

    query = sparql_queries.get_info_for_contact_query(contact)
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    # Try another query if we don't have any results, however, only if we have more than one
    # tokens in 'contact'. Querying with one token will not get another result than the above query.
    if not results and len(contact.split()) > 1:
        query = sparql_queries.get_info_for_contact_abbreviated_name_query(contact)
        response = requests.post(db_url, data={'query': query})
        results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        if 'phone' in r:
            phone = r['phone']['value']
        else:
            phone = '499-1000'
        if 'email' in r:
            email = r['email']['value']
        else:
            email = None
        contact = Person(name=r['name']['value'], phone=phone,
                         email=email, title=r['title']['value'])
        contacts.append(contact)
    return contacts


def get_contact_from_subject(subject: str) -> list:
    query = sparql_queries.get_contact_from_subject_query(subject)
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        if 'phone' in r:
            phone = r['phone']['value']
        else:
            phone = '499-1000'
        if 'email' in r:
            email = r['email']['value']
        else:
            email = None
        contact = Person(name=r['name']['value'], phone=phone,
                         email=email, title=r['title']['value'])
        contacts.append(contact)
    return contacts


def get_name_for_title(title: str) -> list:
    query = sparql_queries.get_names_for_title_query(title)
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        if 'phone' in r:
            phone = r['phone']['value']
        else:
            phone = get_office_phone_number()
        if 'email' in r:
            email = r['email']['value']
        else:
            email = None
        contact = Person(name=r['name']['value'], phone=phone,
                         email=email, title=r['title']['value'])
        contacts.append(contact)
    return contacts


# TODO: Replace this
def format_date_time(date_time: str) -> str:
    """Format datetime objects into human-readable output."""

    year, month, rest = date_time.split('-')
    day = rest[:2]
    date_time_string = f"{day}.{month}"
    return date_time_string


def get_street_endings() -> list:
    """Get all possible endings of street names."""

    query = sparql_queries.get_street_endings_query()
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    return results


def get_general_waste_bin_collection_info() -> list:
    """Get time intervals for upcoming waste bin collection, all areas."""

    collection_times = []
    query = sparql_queries.get_general_waste_bin_collection_info_query()
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    for r in results:
        start_time = format_date_time(r['starttime']['value'])
        end_time = format_date_time(r['endtime']['value'])
        times = WasteBinInfo(start_time=start_time, end_time=end_time, place=r['places']['value'], place_prep="á")
        collection_times.append(times)
    return collection_times[:2]


def get_waste_bin_collection_info(place: str) -> list:
    """Get time intervals for upcoming waste bin collection
    for some area, based on ending of given street name."""

    collection_times = []
    street_endings = get_street_endings()
    place_query = place
    place_prep = "á"
    for ending in street_endings:
        if place.endswith(ending['place']['value']):
            place_query = ending['place']['value']
            if ending['place']['value'] in ['torfa', 'torfu', 'torfan', 'torfunni']:
                place_prep = "í"
            break
    query = sparql_queries.get_waste_bin_collection_info_query(place_query)
    response = requests.post(db_url, data={'query': query})
    results = response.json()['results']['bindings']
    for r in results:
        start_time = format_date_time(r['starttime']['value'])
        end_time = format_date_time(r['endtime']['value'])
        times = WasteBinInfo(start_time=start_time, end_time=end_time, place=place, place_prep=place_prep)
        collection_times.append(times)
    return collection_times
