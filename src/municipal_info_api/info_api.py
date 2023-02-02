import os
from rdflib import Graph

import sparql_queries

STAFF_RDF = "{}/offices_staff.rdf".format(os.path.dirname(__file__))
GRAPH = Graph().parse(STAFF_RDF)


class Person:
    def __init__(self, name=None, phone=None, email=None, department=None, title=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.department = department
        self.title = title


def get_all_names() -> list:
    query = sparql_queries.get_all_names_query()
    result = GRAPH.query(query)
    contacts = []
    for r in result:
        contacts.append(str(r['name']))
    return contacts

def get_valid_subjects() -> list:
    query = sparql_queries.get_all_roles_query()
    result = GRAPH.query(query)
    contacts = []
    for r in result:
        contacts.append(str(r['role']))
    return contacts


def get_info_for_contact(contact: str) -> list:
    """Find the contact info for persons that match 'contact'. First, we try to find a match of the 'contact'
     as is, either a first name, first names or a full name. If nothing is found, we check if the 'contact'
     is missing a middle name or abbreviating it, e.g. 'Anna Árnadóttir' should give us results
     for 'Anna Jóna Árnadóttir', as should 'Anna J. Árnadóttir'."""

    query = sparql_queries.get_info_for_contact_query(contact)
    result = GRAPH.query(query)
    # Try another query if we don't have any results, however, only if we have more than one
    # tokens in 'contact'. Querying with one token will not get another result than the above query.
    if not result and len(contact.split()) > 1:
        query = sparql_queries.get_info_for_contact_abbreviated_name_query(contact)
        result = GRAPH.query(query)
    contacts = []
    for r in result:
        contact = Person(name=str(r['name']), phone=str(r['phone']), email=str(r['email']), title=str(r['title']))
        if contact.phone == 'None':
            contact.phone = '499-1000'
        if contact.email == 'None':
            contact.email = None
        contacts.append(contact)
    return contacts


def get_contact_from_subject(subject: str) -> list:
    query = sparql_queries.get_contact_from_subject_query(subject)
    result = GRAPH.query(query)
    contacts = []
    for r in result:
        contact = Person(name=str(r['name']), phone=str(r['phone']), email=str(r['email']), title=str(r['title']))
        if contact.phone == 'None':
            contact.phone = '499-1000'
        if contact.email == 'None':
            contact.email = None
        contacts.append(contact)
    return contacts


def get_name_for_title(title: str) -> list:
    query = sparql_queries.get_names_for_title_query(title)
    result = GRAPH.query(query)
    contacts = []
    for r in result:
        contact = Person(name=str(r['name']), phone=str(r['phone']), email=str(r['email']), title=str(r['title']))
        if contact.phone == 'None':
            contact.phone = '499-1000'
        if contact.email == 'None':
            contact.email = None
        contacts.append(contact)
    return contacts
