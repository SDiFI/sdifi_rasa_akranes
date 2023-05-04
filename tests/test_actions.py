"""Unit tests for custom actions."""
import pytest
from typing import Text, Any
from rdflib import Graph

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, AllSlotsReset

from actions import actions

import info_api


@pytest.mark.parametrize(
    "title, expected_events",
    [
        ("ruslakarl",
         [AllSlotsReset()]),
        ("matráður",
         [SlotSet("contact", "Guðbjörg Helgadóttir"), SlotSet("title", None)])
    ]
)
def test_get_who_is(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    title: Text,
    expected_events: Any
):
    tracker.slots["title"] = title
    action = actions.ActionGetWhoIs()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == expected_events


@pytest.mark.parametrize(
    "subject, expected_events",
    [
        ("rokktónlist",
         [AllSlotsReset()]),
        ("Velferðarmál",
         [SlotSet("contact", "María Jóhannsdóttir"), SlotSet("title", None)])
    ]
)
def test_get_who_is_from_subject(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    subject: Text,
    expected_events: Any
):
    tracker.slots["subject"] = subject
    action = actions.ActionGetWhoIs()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == expected_events


@pytest.mark.parametrize(
    "subject, expected_events",
    [
        ("Bókmenntasaga",
         [AllSlotsReset()]),
        ("Launamál",
         [SlotSet("contact", "Ásdís Guðmundsdóttir"), SlotSet("title", None),
          SlotSet("subject", None), SlotSet("pronoun", None)])
    ]
)
def test_get_info_for_contact_from_subject(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    subject: Text,
    expected_events: Any
):
    tracker.slots["subject"] = subject
    action = actions.ActionGetInfoForContact()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == expected_events


@pytest.mark.parametrize(
    "contact, expected_events",
    [
        ("Jón Jónsson",
         [AllSlotsReset()]),
        ("Jón",
         [SlotSet("contact", "Jón Sigurðsson"), SlotSet("title", None),
          SlotSet("subject", None), SlotSet("pronoun", None)])
    ]
)
def test_get_info_for_contact(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    contact: Text,
    expected_events: Any
):
    tracker.slots["contact"] = contact
    action = actions.ActionGetInfoForContact()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == expected_events


def test_get_operator(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
):
    action = actions.ActionGetOperator()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == []
    assert dispatcher.messages[0]['response'] == 'utter_operator'


test_string_no_info = """
<rdf:RDF
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  >

</rdf:RDF>
"""

test_string_no_phone = """
<rdf:RDF
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:org="https://www.w3.org/TR/vocab-org"
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  >
  
  <org:Site rdf:about="https://grammatek.com/munic/akranes/SkrifstofaAndabaejar">
    <foaf:mbox>andabaer@andabaer.is</foaf:mbox>
 </org:Site>

</rdf:RDF>
"""


def test_get_operator_no_info(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
):
    # For this test case, we need to import a dummy database that doesn't contain
    # the information it should.
    info_api.update_db(data_string=test_string_no_info, data_type='RDF')
    action = actions.ActionGetOperator()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == []
    assert dispatcher.messages[0]['response'] == 'utter_operator_no_info'

    # Here we replace the dummy database with the correct one.
    g = Graph()
    g.parse("./src/municipal_info_api/offices_staff.rdf")
    data = g.serialize(format="xml")
    info_api.update_db(data_string=data, data_type='RDF')


def test_get_operator_no_phone(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
):
    info_api.update_db(data_string=test_string_no_phone, data_type='RDF')
    action = actions.ActionGetOperator()
    actual_events = action.run(dispatcher=dispatcher, tracker=tracker, domain=domain)

    assert actual_events == []
    assert dispatcher.messages[0]['response'] == 'utter_operator_no_phone'

    g = Graph()
    g.parse("./src/municipal_info_api/offices_staff.rdf")
    data = g.serialize(format="xml")
    info_api.update_db(data_string=data, data_type='RDF')
