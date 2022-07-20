def get_rdf_prefix() -> str:
    """Prefixes as defined in 'offices_staff.rdf'"""

    return """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX org: <https://www.w3.org/TR/vocab-org>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX akranes: <https://grammatek.com/munic/akranes/>
            """


def get_info_for_contact_query(contact: str) -> str:
    """A query to extract full name, and both email
    and phone number where possible, from a foaf:Person
    entity in a graph having exact match of
    'contact' as a full name (foaf:name)."""

    query = """
            SELECT ?email ?name ?phone
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name ?name FILTER (?name = '""" + contact + """') .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
            }
            """
    return get_rdf_prefix() + query
    
    
def get_number_for_contact_query(contact: str) -> str:
    """A query to extract full name, and phone
    number where possible, from a foaf:Person
    entity in a graph having exact match of
    'contact' as a full name (foaf:name)."""

    query = """
            SELECT ?name ?phone
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name ?name FILTER (?name = '""" + contact + """') .
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
            }
            """
    return get_rdf_prefix() + query


def get_email_for_contact_query(contact: str) -> str:
    """A query to extract full name, and email where
     possible, from a foaf:Person entity in a graph
     having exact match of 'contact' as a full name
     (foaf:name)."""

    query = """
            SELECT ?email ?name
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name ?name FILTER (?name = '""" + contact + """') .
                OPTIONAL {?entity foaf:mbox ?email .}
            }
            """
    return get_rdf_prefix() + query


def get_info_for_partial_contact_query(contact: str) -> str:
    """A query to extract full name, and email
    and phone number where possible, from a foaf:Person
    entity in a graph having a match of 'contact' either
    as full name, first name or family name, ignoring case."""

    query = """
            SELECT DISTINCT ?email ?name ?phone
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
                FILTER (regex(?partName, '""" + contact + """', "i"))
            }
            """
    return get_rdf_prefix() + query


def get_number_for_partial_contact_query(contact: str) -> str:
    """A query to extract full name, and phone number
    where possible, from a foaf:Person entity in a graph
    having a match of 'contact' either as full name,
    first name or family name, ignoring case."""

    query = """
            SELECT DISTINCT ?name ?phone
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
                ?entity foaf:name ?name .
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
                FILTER (regex(?partName, '""" + contact + """', "i"))
            }
            """
    return get_rdf_prefix() + query


def get_email_for_partial_contact_query(contact: str) -> str:
    """A query to extract full name, and email
    where possible, from a foaf:Person entity in a graph
    having a match of 'contact' either as full name,
    first name or family name, ignoring case."""

    query = """
            SELECT DISTINCT ?email ?name
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                FILTER (regex(?partName, '""" + contact + """', "i"))
            }
            """
    return get_rdf_prefix() + query


# def get_info_for_partial_contact_department_query(contact: str, department: str) -> str:
#      """A query to extract full name, and email
#      and phone number where possible, from a foaf:Person
#      entity in a graph having a match of 'contact' either
#      as full name, first name or family name, ignoring case,
#      with the added condition of a match of 'department'
#      as 'headOf' or 'memberOf'."""
#
#      query = """
#             SELECT DISTINCT ?email ?name ?phone
#             WHERE {
#                 ?entity rdf:type foaf:Person .
#                 ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
#                 ?entity foaf:name ?name .
#                 ?entity org:memberOf|org:headOf ?department
#                 ?department skos:prefLabel ?departmentName
#                 OPTIONAL {?entity foaf:mbox ?email .}
#                 OPTIONAL {?entity vcard:hasTelephone [
#                     vcard:hasValue ?phone ] .}
#                 FILTER (?departmentName = '""" + department + """') .
#                 FILTER (regex(?partName, '""" + contact + """', "i"))
#             }
#             """
#      return get_rdf_prefix() + query
#
# def get_number_for_partial_contact_department_query(contact: str, department: str) -> str:
#     """A query to extract full name, and phone
#     number where possible, from a foaf:Person
#     entity in a graph having a match of 'contact' either
#     as full name, first name or family name,
#     ignoring case, with the added condition of a match of
#     'department' as 'headOf' or 'memberOf'."""
#
#     query = """
#             SELECT DISTINCT ?name ?phone
#             WHERE {
#                 ?entity rdf:type foaf:Person .
#                 ?entity org:memberOf|org:headOf ?department FILTER (?department = '""" + department + """') .
#                 ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
#                 ?entity foaf:name ?name .
#                 OPTIONAL {?entity vcard:hasTelephone [
#                     vcard:hasValue ?phone ] .}
#                 FILTER (regex(?partName, '""" + contact + """', "i"))
#             }
#             """
#     return get_rdf_prefix() + query
#
#
# def get_email_for_partial_contact_department_query(contact: str, department: str) -> str:
#      """A query to extract full name, and email
#      where possible, from a foaf:Person entity
#      in a graph having a match of 'contact' either
#      as full name, first name or family name,
#      ignoring case, with the added condition of a match of
#      'department' as 'headOf' or 'memberOf'."""
#
#      query = """
#             SELECT DISTINCT ?name ?email
#             WHERE {
#                 ?entity rdf:type foaf:Person .
#                 ?entity org:memberOf|org:headOf ?department .
#                 ?department skos:prefLabel ?departmentname FILTER (?departmentname = '""" + department + """') .
#                 ?entity foaf:name|foaf:firstName|foaf:familyName ?partName .
#                 ?entity foaf:name ?name
#                 OPTIONAL {?entity foaf:mbox ?email .}
#                 FILTER (regex(?partName, '""" + contact + """', "i"))
#
#             }
#             """
#      return get_rdf_prefix() + query
        

def get_contact_from_subject_query(subject: str) -> str:
    """A query to extract full name, and email
     and phone number where possible, from a
     foaf:Person entity in a graph having exact
     match of 'subject' as org:role."""

    query = """
            SELECT ?email ?name
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity org:role ?role FILTER (?role = '""" + subject + """') .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
            }
            """
    return get_rdf_prefix() + query
    
    
# def get_contact_from_department_query(department: str) -> str:
#      """A query to extract full name, and email
#      and phone number where possible, from a
#      foaf:Person entity in a graph being
#      'org:headOf' of 'department'."""
#
#      query = """
#             SELECT ?email ?name ?phone
#             WHERE {
#                 ?entity rdf:type foaf:Person .
#                 ?entity org:headOf ?department .
#                 ?department skos:prefLabel ?departmentName FILTER (?department = '""" + department + """') .
#                 OPTIONAL {?entity foaf:mbox ?email .}
#                 OPTIONAL {?entity vcard:hasTelephone [
#                     vcard:hasValue ?phone ] .}
#             }
#             """
#      return get_rdf_prefix() + query


# def get_general_info_query(entity: str) -> str:
#     """A query to extract the most relevant
#     information possible from a non-foaf:Person
#     entity."""
#
#     query = """
#             SELECT ?entity
#             WHERE {
#                 ?entity rdf:type ?type FILTER (?type in (org:Organization, org:OrganizationalUnit, org:Site))
#             }
#             """
#     return get_rdf_prefix() + query