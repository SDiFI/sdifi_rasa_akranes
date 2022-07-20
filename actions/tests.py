from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult

import sparql_queries

STAFF_RDF = 'offices_staff.rdf'
GRAPH = Graph().parse(STAFF_RDF)


def get_info_for_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_info_for_contact_query(contact)
    result = GRAPH.query(query)
    return result
    

def get_number_for_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_number_for_contact_query(contact)
    result = GRAPH.query(query)
    return result
    
    
def get_email_for_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_email_for_contact_query(contact)
    result = GRAPH.query(query)
    return result
    

def get_info_for_partial_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_info_for_partial_contact_query(contact)
    result = GRAPH.query(query)
    return result
    

def get_number_for_partial_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_number_for_partial_contact_query(contact)
    result = GRAPH.query(query)
    return result
    
    
def get_email_for_partial_contact(contact: str) -> SPARQLResult:
    query = sparql_queries.get_email_for_partial_contact_query(contact)
    result = GRAPH.query(query)
    return result


# def get_info_for_partial_contact_department(contact: str, department: str) -> SPARQLResult:
#     query = sparql_queries.get_info_for_partial_contact_department_query(contact, department)
#     result = GRAPH.query(query)
#     return result
#

# def get_number_for_partial_contact_department(contact: str, department: str) -> SPARQLResult:
#     query = sparql_queries.get_number_for_partial_contact_department_query(contact, department)
#     result = GRAPH.query(query)
#     return result
#
#
# def get_email_for_partial_contact_department(contact: str, department: str) -> SPARQLResult:
#     query = sparql_queries.get_email_for_partial_contact_department_query(contact, department)
#     result = GRAPH.query(query)
#     return result
    

def get_contact_from_subject(subject: str) -> SPARQLResult:
    query = sparql_queries.get_contact_from_subject_query(subject)
    result = GRAPH.query(query)
    return result
    
    
# def get_contact_from_department(department: str) -> SPARQLResult:
#     query = sparql_queries.get_contact_from_department_query(department)
#     result = GRAPH.query(query)
#     return result


# def get_general_info(entity: str) -> SPARQLResult:
#     query = sparql_queries.get_general_info_query(entity)
#     result = GRAPH.query(query)
#     return result


def main():
    res = get_info_for_contact('Jón Arnar Sverrisson')
    assert len(res) != 0
    for r in res:
        assert r['name'].strip() == 'Jón Arnar Sverrisson'
        assert r['phone'].strip() == 'tel:898 3490'
        assert r['email'].strip() == 'jonsverris@akranes.is'
    res = get_email_for_contact('Ásbjörn Egilsson')
    assert len(res) != 0
    for r in res:
        assert r['name'].strip() == 'Ásbjörn Egilsson'
        assert r['email'].strip() == 'asbjorn@akranes.is'
    res = get_info_for_partial_contact('Ásdís')
    assert len(res) != 0
    for r in res:
        assert r['name'].strip() == 'Ásdís Gunnarsdóttir'
        assert r['phone'].strip() == 'tel:433 1015'
        assert r['email'].strip() == 'asdis.gunnarsdottir@akranes.is'
    res = get_info_for_partial_contact('Jón')
    assert len(res) == 6
    for r in res:
        assert r['name'].strip() in ['Jón Arnar Sverrisson','Ásta Jóna Ásmundsdóttir','Kristín Björg Jónsdóttir','Laufey Jónsdóttir','Vigdís Elfa Jónsdóttir','Heiðrún Jónsdóttir']
    res = get_contact_from_subject('Skipulagsmál')
    assert len(res) != 0
    for r in res:
        assert r['name'].strip() == 'Halla Marta Árnadóttir'
        assert r['email'].strip() == 'halla@akranes.is'
        assert 'phone' not in r

if __name__ == '__main__':
    main()