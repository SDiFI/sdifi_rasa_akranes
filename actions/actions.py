# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import json

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import AllSlotsReset, SessionStarted, ActionExecuted
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
                'chitchat': 'bara spjalla aðeins'}

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

        if contact:
            prompt += f" við {contact}"
            entities["contact"] = contact
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

        dispatcher.utter_message("Ég hætti þá leitinni og við getum byrjað upp á nýtt ef þú vilt. Afsakaðu vesenið.")

        return [AllSlotsReset()]


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
                elif email_or_phone == 'both':
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

    def subject_buttons(self) -> List[Dict]:
        """Buttons suggesting all possible subjects to user, in case of trouble."""
        buttons = []
        for subject in self.subject_list():
            # Unnecessary step below, but seemingly only way to correctly format the output as a proper json object.
            subject_dict = {"subject": subject}
            buttons.append({'title': subject, 'payload': '/request_contact'+json.dumps(subject_dict)})
        return buttons

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

        if slot_value.title() in self.subject_list():
            return {'subject': slot_value}
        else:
            dispatcher.utter_message(text=f"Því miður fann ég engar upplýsingar um {slot_value}."
                                          f"Er það örugglega rétt skrifað?")
            dispatcher.utter_message(text="Þú getur reynt að umorða spurninguna eða valið málaflokk:",
                                     buttons=self.subject_buttons())
            return {'subject': None}

    def validate_contact(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate contact value."""

        candidates = []
        nominative_names = declension.get_nominative_name(slot_value.title())
        for name in nominative_names:
            for contact in self.contact_list():
                if name in contact:
                    candidates.append(contact)
        candidates = [*set(candidates)]

        if len(candidates) == 1:
            return {'contact': candidates[0]}
        elif len(candidates) > 1:
            # Pass list of possible names to user.
            dispatcher.utter_message(text="Ég fann fleiri en einn starfsmann með þessu nafni:")
            for candidate in candidates:
                dispatcher.utter_message(text=candidate)
            return {'contact': None}
        else:
            dispatcher.utter_message(text=f"Því miður fann ég engan starfsmann með nafninu {slot_value.title()}. "
                                          f"Er það örugglega rétt skrifað?")
            dispatcher.utter_message(text="Þú getur spurt eftir öðrum starfsmanni eða valið málaflokk:",
                                     buttons=self.subject_buttons())
        return {'contact': None}

    def validate_email_or_phone(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate email_or_phone value."""

        if slot_value.lower() in ['phone', 'email', 'both']:
            return {'email_or_phone': slot_value}
        else:
            return {'email_or_phone': None}
