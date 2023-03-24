"""
SPARQL queries for the municipality RDF-knowledge base.
Helper methods to prepare arguments, where needed, otherwise arguments are fed directly into the prepared
queries.
"""
import re


def get_rdf_prefix() -> str:
    """Prefixes as defined in 'offices_staff.rdf'"""

    return """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX org: <https://www.w3.org/TR/vocab-org>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX akranes: <https://grammatek.com/munic/akranes/>
            """


def extract_names_for_query(contact: str) -> tuple:
    """Extract first name, middle name (abbreviation) and family name (abbreviation) from the contact string.
    The resulting first_name and family_name strings are ready for a SPARQL query. If the contact contains
    an abbreviated middle name, it will be added to the first name without the abbreviation dot.
    An abbreviated family name will also be returned without the dot, e.g. 'Sturlaugsd.' will be returned as
    'Sturlaugsd'"""

    arr = contact.split()
    first_name = arr[0]
    family_name = '.*'
    if len(arr) == 1:
        # the contact string should be validated before calling this method, but we don't rely on that
        family_name = 'none_valid'
    elif re.match('^[A-ZÁÉÍÓÚÝÞÆÖ]\\.?$', arr[1]):
        # add the abbreviated middle name to first name, without the dot that might be added,
        # e.g. 'Lilja L.' becomes 'Lilja L'
        first_name = f"{first_name} {arr[1][0]}"
        if len(arr) == 3:
            family_name = arr[-1]
    else:
        # we need to add the regex for word boundary/EOS if we are not dealing with an abbreviated middle name
        first_name = f"{first_name}( |$)"
        family_name = arr[-1]

    # delete a dot that might follow an abbreviated family name, like 'Sturlaugsd.'
    if family_name.endswith('.'):
        family_name = family_name[:-1]

    return first_name, family_name


def get_all_names_query() -> str:
    """A query to extract full names from all foaf:Person entities in a graph."""

    query = """
            SELECT ?name
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name ?name .
            }
            """
    return get_rdf_prefix() + query


def get_all_roles_query() -> str:
    """A query to extract full names from all foaf:Person entities in a graph."""

    query = """
            SELECT ?role
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity org:role ?role .
            }
            """
    return get_rdf_prefix() + query


def get_info_for_contact_query(contact: str) -> str:
    """A query to extract full name, and both email
    and phone number where possible, from a foaf:Person
    entity in a graph matching 'contact' either as a full name (foaf:name)
    or first name, where the match can be either an exact match or the first of two first names.
    Example: 'Lilja' will find 'Lilja Lind Sturlaugsdóttir', as will 'Lilja Lind'
    Regex explanation: match any name or firstName that starts with 'contact' (^) and is either a full match (EOS: $)
    or matches a whole word (ends with a space)."""

    query = """
            SELECT DISTINCT ?email ?name ?phone ?title
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:name|foaf:firstName ?matching_name 
                    FILTER regex(str(?matching_name), '^""" + contact + """( |$)') .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
                OPTIONAL {?entity foaf:title ?title .}
            }
            """
    return get_rdf_prefix() + query


def get_info_for_contact_abbreviated_name_query(contact: str) -> str:
    """A query that needs processing of the 'contact' argument, because no exact matches have been found in a
     previous queries. This query finds results for different versions of a contact, like:
     'Lilja L. Sturlaugsdóttir', 'Lilja L.', 'Lilja Lind Sturlaugsd.'
    All should return info for 'Lilja Lind Sturlaugsdóttir'.
   """

    first_name, family_name = extract_names_for_query(contact)

    query = """
                    SELECT DISTINCT ?email ?name ?phone ?title
                    WHERE {
                        ?entity rdf:type foaf:Person .
                        ?entity foaf:firstName ?matching_name 
                            FILTER regex(str(?matching_name), '^""" + first_name + """') .
                        ?entity foaf:familyName ?famName 
                            FILTER regex(str(?famName), '^""" + family_name + """') .
                        ?entity foaf:name ?name .
                        OPTIONAL {?entity foaf:mbox ?email .}
                        OPTIONAL {?entity vcard:hasTelephone [
                            vcard:hasValue ?phone ] .}
                        OPTIONAL {?entity foaf:title ?title .}
                    }
                    """
    return get_rdf_prefix() + query


def get_names_for_title_query(title: str) -> str:
    """A query to extract full name, and both email
    and phone number where possible, from a foaf:Person
    entity in a graph matching
    'title' as a title (foaf:title)."""

    query = """
            SELECT DISTINCT ?name ?email ?name ?phone ?title
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity foaf:title ?title FILTER regex(str(?title), '""" + title + """') .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
            }
            """
    return get_rdf_prefix() + query


def get_contact_from_subject_query(subject: str) -> str:
    """A query to extract full name, and email
     and phone number where possible, from a
     foaf:Person entity in a graph having exact
     match of 'subject' as org:role."""

    query = """
            SELECT DISTINCT ?email ?name ?phone ?title
            WHERE {
                ?entity rdf:type foaf:Person .
                ?entity org:role ?role FILTER (?role = '""" + subject + """') .
                ?entity foaf:name ?name .
                OPTIONAL {?entity foaf:mbox ?email .}
                OPTIONAL {?entity vcard:hasTelephone [
                    vcard:hasValue ?phone ] .}
                OPTIONAL {?entity foaf:title ?title .}
            }
            """
    return get_rdf_prefix() + query
