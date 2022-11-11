# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import json

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import AllSlotsReset, SessionStarted, ActionExecuted, \
    ActiveLoop, ConversationPaused, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import info_api, declension


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        events = [SessionStarted()]
        dispatcher.utter_message(text="Góðan daginn! Hvernig get ég aðstoðað?")
        events.append(ActionExecuted("action_listen"))
        return events


class ActionDefaultAskAffirmation(Action):
    """Ask user for affirmation of intent, in case of low confidence."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    @staticmethod
    def intent_mappings():
        """Mappings of names of possible intents to user-readable text."""

        return {'request_contact': 'fá að tala', 'inform': 'fá að tala',
                'greet': 'heilsa mér', 'no_intent': 'ekkert sérstakt', 'out_of_scope': 'eitthvað sem ég ræð ekki við',
                'bye': 'kveðja', 'thank': 'þakka mér', 'stop': 'hætta við og byrja upp á nýtt',
                'chitchat': 'bara spjalla aðeins', 'faq': 'bara spjalla aðeins'}

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        intent_name = tracker.get_intent_of_latest_message()
        contact = tracker.get_slot('contact')
        subject = tracker.get_slot('subject')
        prompt = self.intent_mappings()[intent_name]
        entities = {}

        if prompt == 'fá að tala':
            if contact:
                prompt += f" við {contact}"
                entities["contact"] = contact
            else:
                prompt += f" við einhvern"
            if subject:
                prompt += f" um {subject}"
                entities["subject"] = subject
        out_text = f"Afsakaðu, ég er nýr og enn að læra. Er það rétt skilið hjá mér að þú viljir {prompt}?"
        buttons = [{'title': 'Já',
                    'payload': f'/{intent_name}'+json.dumps(entities)},
                    {'title': 'Nei',
                     'payload': '/stop'}]
        dispatcher.utter_message(text=out_text, buttons=buttons)

        return {}


class ActionDeactivateLoop(Action):
    """Stop active loop and clear all slots."""

    def name(self) -> Text:
        return "action_deactivate_loop"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        """"""
        validation_fails = tracker.get_slot('validation_fails')
        if validation_fails >= 3:
            dispatcher.utter_message(
                text="Því miður skil ég þetta ekki. Ég verð að hætta leitinni og byrja upp á nýtt.")
        else:
            dispatcher.utter_message(
                text="Ég hætti þá leitinni og við getum byrjað upp á nýtt ef þú vilt. Afsakaðu vesenið.")
        return [AllSlotsReset()]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="Því miður get ég ekki hjálpað þér með þetta. Ég sendi þig áfram á þjónustufulltrúa.")
        # pause tracker
        # undo last user interaction
        return [ConversationPaused(), UserUtteranceReverted()]


class ActionGetInfoForContact(Action):
    """Make call to RDF knowledge base to retrieve requested contact information."""

    def name(self) -> Text:
        return "action_get_contact_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[str, Any]]:

        contact = tracker.get_slot('contact')
        subject = tracker.get_slot('subject')
        email_or_phone = tracker.get_slot('email_or_phone')
        out_text = ''
        error_prompt = ''
        res = []

        if contact:
            res = info_api.get_info_for_contact(contact)
            error_prompt = contact
        elif subject:
            res = info_api.get_contact_from_subject(subject.title())
            error_prompt = subject
        if len(res) == 0:
            out_text += f"Því miður fann ég engar upplýsingar um {error_prompt}."
        else:
            for r in res:
                if r.title:
                    out_text += f"{r.name} er {r.title}."
                if email_or_phone == 'email':
                    if r.email:
                        out_text += f" {r.name} er með netfangið: {r.email}."
                    else:
                        out_text += f" Því miður er {r.name} ekki með skráð netfang hjá okkur. Þú getur prófað síma: {r.phone}."
                elif email_or_phone == 'phone':
                    out_text += f" {r.name} svarar frekari spurningum í síma: {r.phone}."
                else:
                    if r.email:
                        out_text += f" {r.name} svarar frekari spurningum í síma: {r.phone} og á netfangið: {r.email}."
                    else:
                        out_text += f" Því miður er {r.name} ekki með skráð netfang hjá okkur. Þú getur prófað síma: {r.phone}."
        dispatcher.utter_message(text=out_text)
        return [AllSlotsReset()]


class ValidateRequestContactForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_request_contact_form"

    async def required_slots(
            self,
            domain_slots: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        updated_slots = domain_slots.copy()
        if tracker.slots.get("validation_fails") > 3:
            return []
        else:
            if tracker.slots.get("subject"):
                updated_slots.remove("contact")
            elif tracker.slots.get("contact"):
                updated_slots.remove("subject")
            return updated_slots

    @staticmethod
    def subject_list() -> List[Text]:
        """List of possible subjects to inquire about."""

        return ['Skipulagsmál', 'Garðamál', 'Byggingarmál', 'Skólamál',
                'Stjórnsýslumál', 'Launamál', 'Fjármál', 'Bókhaldsmál',
                'Velferðarmál', 'Félagsþjónusta', 'Dýraeftirlit']

    @staticmethod
    def contact_list() -> List[Text]:
        """List of possible contacts from RDF graph."""

        return info_api.get_all_names()

    def validate_subject(
            self, slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate subject value."""
        validation_fails = tracker.get_slot('validation_fails')
        if slot_value:
            if slot_value.title() in self.subject_list():
                return {'subject': slot_value}
            else:
                validation_fails += 1
                return {'subject': None, 'subject_found_but_not_validated': True,
                        'validation_fails': validation_fails}
        validation_fails += 1
        return {'subject': None, 'validation_fails': validation_fails}

    def validate_contact(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate contact value."""

        candidates = []
        validation_fails = tracker.get_slot('validation_fails')
        if tracker.get_slot('contacts_found'):
            contacts = tracker.get_slot('contacts')
        else:
            contacts = self.contact_list()

        nominative_names = declension.get_nominative_name(slot_value.title())
        for name in nominative_names:
            for contact in contacts:
                for part_name in contact.split():
                    if name == part_name or name == contact:
                        candidates.append(contact)

        candidates = [*set(candidates)]
        if len(candidates) == 1:
            return {'contact': candidates[0]}
        elif len(candidates) > 1:
            validation_fails += 1
            contact_string = ",".join(candidates)
            return {'contact': None, 'contacts_found': True, 'contacts': candidates,
                    'contacts_string': contact_string, 'validation_fails': validation_fails}
        else:
            validation_fails += 1
            return {'contact': None, 'validation_fails': validation_fails,}
