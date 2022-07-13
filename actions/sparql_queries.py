def get_rdf_prefix() -> str:
    """Prefixes as defined in 'offices_staff.rdf'"""

    return """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX org: <https://www.w3.org/TR/vocab-org>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            """


def get_contact_info_query(contact: str) -> str:

    query = """
            SELECT ?email ?name
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name ?name FILTER (?name = '""" + contact + """') .
                ?entity foaf:mbox ?email .
            }
            """
    return get_rdf_prefix() + query

