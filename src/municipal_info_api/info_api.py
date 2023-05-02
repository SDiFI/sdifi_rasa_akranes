import os

from rdflib import Graph
import requests
import sparql_queries

FUSEKI_HOST = os.environ.get('FUSEKI_NETWORK_HOST', 'fuseki')
FUSEKI_PORT = os.environ.get('FUSEKI_NETWORK_PORT', '3030')
FUSEKI_DATASET = 'ds'
FUSEKI_QUERY_ENDPOINT = f'http://{FUSEKI_HOST}:{FUSEKI_PORT}/{FUSEKI_DATASET}/query'
FUSEKI_DATA_ENDPOINT = f'http://{FUSEKI_HOST}:{FUSEKI_PORT}/{FUSEKI_DATASET}/data?default'

# Info: append endpoint with "?graph=some_named_graph" instead of ?default to specify a named graph instead of the
# default graph

CONTENT_TYPES = {
        'rdf': 'application/rdf+xml',
        'turtle': 'text/turtle',
        'ntriples': 'application/n-triples',
        'jsonld': 'application/ld+json',
    }

class Person:
    def __init__(self, name=None, phone=None, email=None, department=None, title=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.department = department
        self.title = title


def get_all_names() -> list:
    query = sparql_queries.get_all_names_query()
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        contacts.append(r['name']['value'])
    return contacts


def get_valid_subjects() -> list:
    query = sparql_queries.get_all_roles_query()
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        contacts.append(r['role']['value'])
    return contacts


def get_office_contact_info() -> list:
    """Get the phone number and email of the main office."""
    query = sparql_queries.get_office_contact_info_query()
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
    results = response.json()['results']['bindings']
    contacts = []
    for r in results:
        contacts.append(Person(phone=r['phone']['value'], email=r['email']['value']))
    return contacts


def get_office_phone_number() -> str:
    """Get phone number of main office, to be returned as default phone number in contact searches."""
    query = sparql_queries.get_office_contact_info_query()
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
    results = response.json()['results']['bindings']
    phone = ""
    for r in results:
        phone = r['phone']['value']
    return phone


def get_info_for_contact(contact: str) -> list:
    """Find the contact info for persons that match 'contact'. First, we try to find a match of the 'contact'
     as is, either a first name, first names or a full name. If nothing is found, we check if the 'contact'
     is missing a middle name or abbreviating it, e.g. 'Anna Árnadóttir' should give us results
     for 'Anna Jóna Árnadóttir', as should 'Anna J. Árnadóttir'."""

    query = sparql_queries.get_info_for_contact_query(contact)
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
    results = response.json()['results']['bindings']
    # Try another query if we don't have any results, however, only if we have more than one
    # tokens in 'contact'. Querying with one token will not get another result than the above query.
    if not results and len(contact.split()) > 1:
        query = sparql_queries.get_info_for_contact_abbreviated_name_query(contact)
        response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
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


def get_contact_from_subject(subject: str) -> list:
    query = sparql_queries.get_contact_from_subject_query(subject)
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
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


def get_name_for_title(title: str) -> list:
    query = sparql_queries.get_names_for_title_query(title)
    response = requests.post(FUSEKI_QUERY_ENDPOINT, data={'query': query})
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


def get_db(format_type, endpoint=FUSEKI_DATA_ENDPOINT):
    """
    Retrieves DB from a Fuseki endpoint in the specified format and returns the data as a string.
    :param format_type: The desired format ('rdf', 'turtle', 'ntriples', 'jsonld', 'rdfjson', 'trig', or 'nquads') as a string
    :param endpoint: The Fuseki endpoint (URL) as a string

    :return: The retrieved data in the specified format as a string
    """

    format_type_lower = format_type.lower()
    if format_type_lower not in CONTENT_TYPES:
        raise ValueError(f"The format type must be one of {', '.join(CONTENT_TYPES.keys())}.")

    accept_header = CONTENT_TYPES[format_type_lower]
    headers = {'Accept': accept_header}

    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        # Parse the response as the specified format for validation and then serialize it as a string
        # again
        response_data = response.content.decode('utf-8')

        # Adaptions for rdflib
        if format_type_lower == 'rdf':
            format_type = 'xml'
        if format_type_lower == 'jsonld':
            format_type = 'json-ld'

        graph = Graph()
        graph.parse(data=response_data, format=format_type)
        return graph.serialize(format=format_type, encoding='utf-8')
    else:
        raise Exception(f"Error: HTTP {response.status_code}: {response.text}")


def is_utf8_encoded(byte_array):
    try:
        byte_array.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False
    except AttributeError:
        return False


def update_db(data_string, data_type, endpoint=FUSEKI_DATA_ENDPOINT):
    """
    Sends db contents as string containing RDF data to a Fuseki endpoint using PUT, replacing the existing data.

    :param data_string: The RDF data as a string
    :param data_type: The data type ('rdf', 'turtle', 'ntriples', 'jsonld', 'rdfjson', 'trig', or 'nquads') as a string
    :param endpoint: The Fuseki endpoint (URL) as a string
    """
    data_type_lower = data_type.lower()
    if data_type_lower not in CONTENT_TYPES:
        raise ValueError(f"The format type must be one of {', '.join(CONTENT_TYPES.keys())}.")

    content_type = CONTENT_TYPES[data_type_lower]
    headers = {'Content-Type': content_type}

    # make sure data_string is utf-8 encoded
    if not is_utf8_encoded(data_string):
        data_string = data_string.encode('utf-8')

    response = requests.put(endpoint, headers=headers, data=data_string)
    if response.status_code != 200:
        raise Exception(f"Error: HTTP {response.status_code}: {response.text}")
