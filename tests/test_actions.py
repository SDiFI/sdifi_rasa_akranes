"""Unit tests for custom actions."""
import pytest
from typing import Text, Any

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, AllSlotsReset

from actions import actions


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
