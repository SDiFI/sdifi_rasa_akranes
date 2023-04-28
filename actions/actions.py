# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import json
import logging
from datetime import date
import yaml

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import AllSlotsReset, SlotSet, BotUttered
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import info_api
import declension

# TODO: consider creating object classes e.g. for contacts, so that we don't need to rely on the structure of the
# TODO: sparql-query results in the actions (like 'r.name' etc.)

logger = logging.getLogger(__name__)


class ActionGetMOTD(Action):
    """Retrieve message-of-the-day greeting from external file.
    Only meant to be triggered remotely, not from a user message."""

    def name(self) -> Text:
        return "action_get_motd"

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        today = date.today()
        language = tracker.get_slot('language')
        motd_list = []
        output_dict = {}
        default_message_list = []
        logger.info(f"{self.name()} retrieving MOTD for date: {today}")
        with open('data/motd/motd.yml', 'r') as stream:
            motd_dict = yaml.safe_load(stream)
        for item in motd_dict['motd']:
            if 'date_range' in item:
                if item['date_range']['start'] <= today <= item['date_range']['end']:
                    for message in item['messages'][language]:
                        motd_list.append(message)
            elif 'default' in item:
                for message in item['messages'][language]:
                    default_message_list.append(message)
        # If no messages are found for the current date,
        # use the default message for the given language.
        if len(motd_list) != 0:
            output_dict["motd"] = {"language": language, "motd": motd_list}
        else:
            output_dict["motd"] = {"language": language, "motd": default_message_list}
        return [BotUttered(json.dumps(output_dict))]


class ActionDefaultAskAffirmation(Action):
    """Ask user for affirmation of intent, in case of low confidence."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    @staticmethod
    def get_intents():
        """List of possible intents for affirmation.
        Not all intents are on this list, only the ones where we want the bot to ask for affirmation, e.g.
        'I didn't quite get that, do you want to speak to X?'"""
        # TODO: Negla niður hvað á að vera á þessum lista og hvað ekki.
        # TODO: isn't it a bit awkward to ask "is it correct that you want to greet me/thank me/say good bye?" Better just to say
        # TODO: "didn't understand" in those cases?
        return ['request_contact',
                'who_is',
                #'greet',
                #'bye',
                #'thank',
                'stop']

    @staticmethod
    def get_entities(tracker: Tracker) -> dict:
        entities = {}
        contact = tracker.get_slot('contact')
        subject = tracker.get_slot('subject')
        title = tracker.get_slot('title')
        if contact:
            entities["contact"] = contact
        if subject:
            entities["subject"] = subject
        if title:
            entities["title"] = title

        return entities

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        intent_name = tracker.get_intent_of_latest_message()
        logger.info(f"{self.name()} affirming intent: {intent_name}")
        if intent_name not in self.get_intents():
            dispatcher.utter_message(response="utter_ask_rephrase")
        else:
            entities = self.get_entities(tracker)
            buttons = [{'title': 'Já',
                        'payload': f'/{intent_name}' + json.dumps(entities)},
                       {'title': 'Nei',
                        'payload': '/out_of_scope'}]
            if (intent_name == 'request_contact' or intent_name == 'who_is') and entities['contact']:
                dispatcher.utter_message(response="utter_affirm_contact", name=entities['contact'], buttons=buttons)
            elif intent_name == 'who_is' and entities['title']:
                dispatcher.utter_message(response="utter_affirm_contact", name=entities['title'], buttons=buttons)
            elif intent_name == 'request_contact' and entities['subject']:
                dispatcher.utter_message(response="utter_affirm_contact", name=entities['subject'], buttons=buttons)
            elif intent_name == 'stop':
                dispatcher.utter_message(response="utter_affirm_stop", buttons=buttons)

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
                template="utter_validation_failed_fallback")
        else:
            dispatcher.utter_message(
                template="utter_stop_restart")
        return [AllSlotsReset()]


class ActionGetInfoForContact(Action):
    """Make call to RDF knowledge base to retrieve requested contact information."""

    def name(self) -> Text:
        return "action_get_contact_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[str, Any]]:

        contact = tracker.get_slot('contact')
        contact_name = contact
        subject = tracker.get_slot('subject')
        email_or_phone = tracker.get_slot('email_or_phone')
        pronoun = tracker.get_slot('pronoun')

        logger.info(f"{self.name()} Contact: {contact}")
        logger.info(f"{self.name()} Subject: {subject}")
        logger.info(f"{self.name()} Pronoun: {pronoun}")

        # if we don't find an entity, we return a general "what you asked about"
        info_object = 'það sem þú spurðir um'
        res = []

        # If we have a subject, have a lookup there. Otherwise, we look up the contact.
        # If we have a pronoun, we have stored the contact from the previous dialogue turn.
        # If not, and we have a contact, either there was no previous 'who-is' turn or the contact
        # has been overridden by the new 'request-contact' intent.
        if subject:
            res = info_api.get_contact_from_subject(subject.title())
            info_object = subject
        elif contact:
            res = info_api.get_info_for_contact(contact)
            info_object = contact

        # nothing found
        if not res:
            dispatcher.utter_message(response="utter_no_info", object=info_object)
            return[AllSlotsReset()]

        for r in res:
            contact_name = r.name
            if r.title:
                full_contact = f"{contact_name}, {r.title},"
            else:
                full_contact = contact_name
            if email_or_phone == 'email':
                if r.email:
                    dispatcher.utter_message(response="utter_email", name=full_contact, email=r.email)
                else:
                    dispatcher.utter_message(response="utter_no_email", name=full_contact, phone=r.phone)
            elif email_or_phone == 'phone':
                dispatcher.utter_message(response="utter_phone", name=full_contact, phone=r.phone)
            else:
                if r.email:
                    dispatcher.utter_message(response="utter_phone_and_mail", name=full_contact, phone=r.phone, email=r.email)
                else:
                    dispatcher.utter_message(response="utter_phone", name=full_contact, phone=r.phone)

        # We want to keep track of the contact for the conversation, the other slots, however, might cause confusion
        # if kept, e.g. because of a mismatch between 'title' and 'contact' given different questions.
        return[SlotSet("contact", contact_name), SlotSet("title", None), SlotSet("subject", None), SlotSet("pronoun", None)]


class ActionGetWhoIs(Action):
    """Make call to RDF knowledge base to retrieve requested information, given an employee title or name."""

    def name(self) -> Text:
        return "action_get_whois"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[str, Any]]:

        """Check if we have a title in the tracker, if yes, retrieve information on that title.
        Otherwise, check for name and retrieve the title for a given contact, if found,
        utter_no_info if nothing is found and reset all slots.
        On success, stores the 'contact' slot but resets the 'title', since otherwise we can run into
        the problem of mismatch between contact and title in follow-up questions."""

        title = tracker.get_slot('title')
        name = tracker.get_slot('contact')
        subject = tracker.get_slot('subject')
        info_object = 'það sem þú spurðir um'
        final_contact = ''  # full name of a found contact
        res = [] # the results from the knowledge base

        logger.info(f"{self.name()} Name: {name}")
        logger.info(f"{self.name()} Title: {title}")
        logger.info(f"{self.name()} Subject: {subject}")

        if title:
            info_object = title
            res = info_api.get_name_for_title(title)
        elif subject:
            info_object = subject
            res = info_api.get_contact_from_subject(subject.title())
        elif name:
            info_object = name
            nom_names = declension.get_nominative_name(name.title())
            for nom_name in nom_names:
                res = info_api.get_info_for_contact(nom_name)
                if res:
                    break

        # nothing found
        if not res:
            dispatcher.utter_message(response="utter_no_info", object=info_object)
            return[AllSlotsReset()]

        if len(res) > 1:
            names = ''
            title_plur = ''
            if title:
                # get the plural version of title to fit the enumeration of names
                title_plur = declension.get_declined_form(title, declension.NOMINATIVE_PL)
            # Iterate through the results and extract the names. Combine the names to an enumeration
            # of the form: "A, B, C and D" (in Icelandic there is no comma before the 'and')
            for i, r in enumerate(res):
                if i == len(res) - 2:
                    names += f"{r.name} og "
                else:
                    names += f"{r.name}, "
            # remove the last comma and space
            names = names[:-2]
            if title_plur:
                dispatcher.utter_message(response="utter_plural_titles", names=names, title_plur=title_plur)
            else:
                dispatcher.utter_message(response="utter_list_no_title", names=names)
        else:
            r = res[0]
            if r.title:
                dispatcher.utter_message(response="utter_title", name=r.name, title=r.title)
            else:
                dispatcher.utter_message(response="utter_name_no_title", name=r.name)
            final_contact = r.name

        if final_contact:
            # final_contact is not set if we have more than one name in the results
            name = final_contact

        return[SlotSet("contact", name), SlotSet("title", None)]


class ActionGetOperator(Action):
    """Here is where some kind of human connection mechanism would be implemented."""
    def name(self) -> Text:
        return "action_get_operator"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        res = info_api.get_office_contact_info()
        if res:
            r = res[0]
            if r.phone and r.email:
                dispatcher.utter_message(response="utter_operator", phone=r.phone, email=r.email)
            elif r.phone:
                dispatcher.utter_message(response="utter_operator_no_email", phone=r.phone)
            elif r.email:
                dispatcher.utter_message(response="utter_operator_no_phone", email=r.email)
            else:
                dispatcher.utter_message(response="utter_operator_no_info")
        else:
            dispatcher.utter_message(response="utter_operator_no_info")

        return []


class ValidateRequestContactForm(FormValidationAction):
    """Validate entities (subject or contact) extracted by request_contact form."""

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
            # Deactivate loop in case of repeated validation fails.
            return []
        else:
            # If a 'subject' entity is extracted, there is no need to keep asking for a contact
            # and vice-versa.
            if tracker.slots.get("subject"):
                updated_slots.remove("contact")
            elif tracker.slots.get("contact"):
                updated_slots.remove("subject")
            return updated_slots

    @staticmethod
    def subject_list() -> List[Text]:
        """List of possible subjects to inquire about."""
        return info_api.get_valid_subjects()

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
        logger.info(f"{self.name()} validating subject: {slot_value}")

        validation_fails = tracker.get_slot('validation_fails')
        if slot_value:
            if slot_value.title() in self.subject_list():
                return {'subject': slot_value}
            else:
                validation_fails += 1

                return {'contact': None, 'subject': None, 'subject_found_but_not_validated': True,
                        'found_subject': slot_value, 'validation_fails': validation_fails}
        validation_fails += 1
        return {'contact': None, 'subject': None, 'validation_fails': validation_fails}

    def validate_contact(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate contact value."""
        candidates = []
        logger.info(f"{self.name()} validating contact: {slot_value}")
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
            return {'contact': None, 'validation_fails': validation_fails}
