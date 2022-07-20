# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import requests
import json
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult

from rasa_sdk import Action, Tracker
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher

import sparql_queries

class ActionJoke(Action):
  def name(self):
    return "action_joke"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    dispatcher.utter_message(text="Ég er inni í ActionJoke")
    request = requests.get('http://api.icndb.com/jokes/random').json()  # make an api call
    joke = request['value']['joke']  # extract a joke from returned json response
    dispatcher.utter_message(text=joke)  # send the message back to the user
    return []

class ActionGetContactInfoFromContact(Action):
    def name(self) -> Text:
        return "action_get_contact_info"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        contact = tracker.get_slot('contact')
        dispatcher.utter_message(text="Ég er inni í ActionGetContactInfoFromContact.run()")

        # g = Graph()
        # g.parse('offices_staff.rdf')
        
        # query = sparql_queries.get_contact_info_query(contact)
        # result = g.query(query)
        
        # for r in result:
        #     dispatcher.utter_message(text=r['name'] + " er með netfangið: " + r['email'])
        
        return [Restarted()]


class ActionGetContactNumberFromContact(Action):
    def name(self) -> Text:
        return "action_get_contact_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        contact = tracker.get_slot('contact')
        dispatcher.utter_message(text="Ég er inni í ActionGetContactNumberFromContact.run()")
        return []


class ActionGetContactEmailFromContact(Action):
    def name(self) -> Text:
        return "action_get_contact_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        contact = tracker.get_slot('contact')
        dispatcher.utter_message(text="Ég er inni í ActionGetContactEmailFromContact.run()")
        return []


