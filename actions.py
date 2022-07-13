# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import requests
import json
from rdflib import Graph
from rasa_sdk import Action, Tracker
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher

employees = [{"name": "Sævar Freyr Þráinsson", 
              "email": "Sævar er of mikilvægur til þess að vera með opinbert netfang",
              "title": "Bæjarstjóri"},
              {"name": "Valgerður Janusdóttir",
               "email": "skoliogfristund@akranes.is",
               "title": "sviðsstjóri skóla- og frí­stunda­sviðs"},
              {"name": "Dagný Hauksdóttir",
               "email": "dagnyh@akranes.is",
               "title": "Verkefnastjóri hjá skóla- og frístundasviði"},
              {"name": "Ólafi Ragnari",
               "email": "olafur.ragnar@skeljungur.is",
               "title": "starfsmaður á plani"},
               {"name": "Daníel Sævarsson",
               "email": "daniel@skeljungur.is",
               "title": "starfsmaður í þjálfun"}
              ]


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


class ActionLookupEmployee(Action):
  def name(self):
    return "action_lookup_employee"

  def run(self, dispatcher, tracker, domain):
    employee_name = tracker.get_slot("employee_name")
    dispatcher.utter_message(text=employee_name)
    employee_dict = next(item for item in employees if item["name"] == employee_name)
    employee_email = employee_dict["email"]
    dispatcher.utter_message(text=f"Netfangið hjá {employee_name} er: {employee_email}")
    return []

class ActionLookupTitle(Action):
  def name(self):
    return "action_lookup_title"

  def run(self, dispatcher, tracker, domain):
    employee_name = tracker.get_slot("employee_name")
    employee_dict = next(item for item in employees if item["name"] == employee_name)
    employee_title = employee_dict["title"]
    dispatcher.utter_message(text=f"{employee_name} er: {employee_title}")
    return []

class ActionGetContactInfoFromContact(Action):
    def name(self) -> Text:
        return "action_get_contact_info"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        contact = tracker.get_slot('contact')

        g = Graph()
        g.parse('offices_staff.rdf')
        
        contact_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?email ?name
        WHERE {
            ?p rdf:type foaf:Person .
            
            ?p foaf:name ?name .
              
            ?p foaf:mbox ?email .
        }"""

        qres = g.query(contact_query)
        email = None
        for r in qres:
            if contact in r["name"]:
                email = r["email"]
        if email:
            dispatcher.utter_message(text=contact + " er með tölvupóstfangið " + email)
        else:
            dispatcher.utter_message(text="Því miður fann ég engan með þessu nafni.")
        return [Restarted()]
