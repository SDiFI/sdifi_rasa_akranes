# # This files contains your custom actions which can be used to run
# # custom Python code.
# #
# # See this guide on how to implement these action:
# # https://rasa.com/docs/rasa/custom-actions
#
# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker, FormValidationAction
# from rasa_sdk.events import Restarted, AllSlotsReset
# from rasa_sdk.executor import CollectingDispatcher
#
# import info_api, declension
#
#
# class ActionGetInfoForContact(Action):
#     def name(self) -> Text:
#         return "action_get_info_for_contact"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         contact = tracker.get_slot('contact')
#         if contact:
#             contact = contact.title()
#             result = info_api.get_info_for_contact(contact)
#
#             if len(result) == 0:
#                 candidates = declension.get_nominative_name(contact)
#                 for c in candidates:
#                     result = info_api.get_info_for_contact(c)
#                     if len(result) == 0:
#                         result = info_api.get_info_for_partial_contact(contact)
#                         if len(result) == 0:
#                             result = info_api.get_info_for_partial_contact(c)
#                             for r in result:
#                                 dispatcher.utter_message(text=r.name + " er með netfangið: " + r.email + " og síma: " + r.phone + ".")
#                         else:
#                             for r in result:
#                                 dispatcher.utter_message(text=r.name + " er með netfangið: " + r.email + " og síma: " + r.phone + ".")
#                     else:
#                         for r in result:
#                             dispatcher.utter_message(text=r.name + " er með netfangið: " + r.email + " og síma: " + r.phone + ".")
#
#             else:
#                 for r in result:
#                     dispatcher.utter_message(text=r.name + " er með netfangið: " + r.email + " og síma: " + r.phone + ".")
#         else:
#             dispatcher.utter_message(text="Því miður skil ég ekki alveg hjá hverjum þig vantar upplýsingar.")
#
#         return [Restarted()]
#
#
# class ActionGetNumberForContact(Action):
#     def name(self) -> Text:
#         return "action_get_number_for_contact"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         contact = tracker.get_slot('contact')
#         if contact:
#             contact = contact.title()
#             result = info_api.get_info_for_contact(contact)
#
#             if len(result) == 0:
#                 candidates = declension.get_nominative_name(contact)
#                 for c in candidates:
#                     result = info_api.get_info_for_contact(c)
#                     if len(result) == 0:
#                         result = info_api.get_info_for_partial_contact(contact)
#                         if len(result) == 0:
#                             result = info_api.get_info_for_partial_contact(c)
#                             for r in result:
#                                 dispatcher.utter_message(
#                                     text=r.name + " er með síma: " + r.phone + ".")
#                         else:
#                             for r in result:
#                                 dispatcher.utter_message(
#                                     text=r.name + " er með síma: " + r.phone + ".")
#                     else:
#                         for r in result:
#                             dispatcher.utter_message(
#                                 text=r.name + " er með síma: " + r.phone + ".")
#
#             else:
#                 for r in result:
#                     dispatcher.utter_message(
#                         text=r.name + " er með síma: " + r.phone + ".")
#         else:
#             dispatcher.utter_message(text="Því miður skil ég ekki alveg hjá hverjum þig vantar símanúmer.")
#
#         return [Restarted()]
#
#
# class ActionGetEmailForContact(Action):
#     def name(self) -> Text:
#         return "action_get_email_for_contact"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         contact = tracker.get_slot('contact')
#         if contact:
#             contact = contact.title()
#             result = info_api.get_info_for_contact(contact)
#
#             if len(result) == 0:
#                 candidates = declension.get_nominative_name(contact)
#                 for c in candidates:
#                     result = info_api.get_info_for_contact(c)
#                     if len(result) == 0:
#                         result = info_api.get_info_for_partial_contact(contact)
#                         if len(result) == 0:
#                             result = info_api.get_info_for_partial_contact(c)
#                             for r in result:
#                                 dispatcher.utter_message(
#                                     text=r.name + " er með netfangið: " + r.email + ".")
#                         else:
#                             for r in result:
#                                 dispatcher.utter_message(
#                                     text=r.name + " er með netfangið: " + r.email + ".")
#                     else:
#                         for r in result:
#                             dispatcher.utter_message(
#                                 text=r.name + " er með netfangið: " + r.email + ".")
#
#             else:
#                 for r in result:
#                     dispatcher.utter_message(
#                         text=r.name + " er með netfangið: " + r.email + ".")
#         else:
#             dispatcher.utter_message(text="Því miður skil ég ekki alveg hjá hverjum þig vantar netfang.")
#
#         return [Restarted()]
#
#
# # class ActionGiveContact(Action):
# #     """"""
# #
# #     def name(self) -> Text:
# #         return "action_give_contact"
# #
# #     def run(self, dispatcher: CollectingDispatcher,
# #             tracker: Tracker,
# #             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
# #         contact = tracker.get_slot('contact')
# #         candidates = declension.get_nominative_name(contact)
# #
# #         if len(candidates) == 0:
# #             dispatcher.utter_message(f"Því miður fundum við engan undir þessu nafni.")
# #             return [AllSlotsReset()]
# #         else:
# #             res = self.check_full_name_or_partial(candidates)
# #             if len(res) == 0:
# #                 dispatcher.utter_message(f"Því miður fundum við engan undir þessu nafni.")
# #             else:
# #                 out_text = "Þetta er það sem ég fann: \n"
# #                 for elem in res:
# #                     name = elem.name
# #                     title = elem.title
# #                     phone = elem.phone
# #                     email = elem.email
# #
# #                     if title != 'None':
# #                         out_text += f"{name} er {title}."
# #                     if email != 'None':
# #                         out_text += f" {contact} veitir nánari upplýsingar í tölvupósti á netfangið {email} eða í síma {phone}.\n"
# #                     else:
# #                         out_text += f" {contact} veitir nánari upplýsingar í síma {phone}.\n"
# #
# #             dispatcher.utter_message(text=out_text)
# #         return [AllSlotsReset()]
# #
# #     def check_full_name_or_partial(self, candidates: list) -> list:
# #         for c in candidates:
# #             res = info_api.get_info_for_contact(c)
# #             if len(res) == 0:
# #                 res = info_api.get_info_for_partial_contact
# #         return res
#
#
# # class ValidateContactForm(FormValidationAction):
# #     def name(self) -> Text:
# #         return "validate_request_contact_form"
#
#     # def validate_contact(
#     #         self,
#     #         slot_value: Any,
#     #         dispatcher: CollectingDispatcher,
#     #         tracker: Tracker,
#     #         domain: DomainDict,
#     # ) -> Dict[Text, Any]:
#     #     """Validate contact value."""
#
#         # contact = tracker.get_slot('contact')
#         # candidates = declension.get_nominative_name(contact)
#
#         # if len(candidates) == 0:
#         #     dispatcher.utter_message(f"Því miður fundum við engan undir þessu nafni.")
#         # else:
#         #     res = info_api.get_info_for_partial_contact(contact)
#         #     if len(res) == 0:
#         #         dispatcher.utter_message(f"Því miður fundum við engan undir nafninu {contact}.")
#         #         return {"contact": None}
#         #     return {"contact": contact}
#         #