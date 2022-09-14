# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import info_api, declension


class ActionGetInfoForContact(Action):
    def name(self) -> Text:
        return "action_get_contact_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[str, Any]]:

        contact = tracker.get_slot('contact')
        subject = tracker.get_slot('subject')
        email_or_phone = tracker.get_slot('email_or_phone')
        out_text = ''

        if contact and contact != ' ':
            res = info_api.get_info_for_contact(contact.title())
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

    @staticmethod
    def subject_list() -> List[Text]:
        """List of possible subjects to inquire about."""

        return ['stjórnsýsla', 'skóli', 'skipulag', 'velferð']

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

        if slot_value.lower() in self.subject_list():
            return {'subject': slot_value, 'contact': ' '}
        else:
            return {'subject': None}

    def validate_contact(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate subject value."""

        if slot_value.lower() in self.contact_list():
            return {'contact': slot_value, 'subject': ' '}
        else:
            candidates = declension.get_nominative_name(slot_value)
            for candidate in candidates:
                if candidate.lower() in self.contact_list():
                    return {'contact': candidate, 'subject': ' '}
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
