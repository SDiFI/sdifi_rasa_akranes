"""
A custom entity extractor that uses the BÍN database and tagset
to look up possible named entities. Can be configured to extract
all words which are labeled with some NER-tag in BÍN or only in cases
where the user message matches some example from our training data
with some new term instead of the labeled entity in the training data.
"""

from typing import Dict, Text, Any, List
import yaml
import re

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.exceptions import InvalidConfigException
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.core.domain import Domain

from islenska import Bin

ALL_BIN_TAGS = ["heö", "alm", "ism", "föð", "móð", "fyr", "bibl", "gæl", "lönd", "gras", "efna", "tölv", "lækn",
                "örn", "tón", "natt", "göt", "lög", "íþr", "málfr", "tími", "við", "fjár", "bíl", "ffl", "mat",
                "bygg", "tung", "erl", "hetja", "bær", "þor", "mvirk", "brag", "jard", "stærð", "hug", "erm",
                "mæl", "titl", "gjald", "stja", "dýr", "hann", "ætt", "ob", "entity", "spurn"]


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False
)
class BinEntityExtractor(GraphComponent, EntityExtractorMixin):

    def __init__(self, component_config: Dict[Text, Any]) -> None:
        self.component_config = component_config
        self.validate_component_config(component_config=self.component_config)

    @staticmethod
    def nlu_examples() -> Dict:
        with open('data/nlu.yml', 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(config)

    @classmethod
    def validate_component_config(cls, component_config: Dict[Text, Any]) -> None:
        if "match_training_data" not in component_config:
            raise InvalidConfigException(
                f"your configuration should contain the section 'match_training_data' and a value of true or false. "
                f"Please specify whether the featurizer should be used only when user input matches an example "
                f"from your training data, with different entities"
            )
        if component_config["match_training_data"] not in [True, False]:
            raise InvalidConfigException(
                f"your configuration should contain the section 'match_training_data' and a value of true or false. "
                f"Please specify whether the featurizer should be used only when user input matches an example "
                f"from your training data, with different entities"
            )
        if "match_all_entities" not in component_config:
            raise InvalidConfigException(
                f"your configuration should contain the section 'match_all_entities' and a value of true or false. "
                f"Please specify whether the featurizer should return all possible matches according to a Bín-lookup."
                f"(If match_training_data is set to True, this is only done as a backup in case of no matches)"
            )
        if component_config["match_all_entities"] not in [True, False]:
            raise InvalidConfigException(
                f"your configuration should contain the section 'match_all_entities' and a value of true or false. "
                f"Please specify whether the featurizer should return all possible matches according to a Bín-lookup."
                f"(If match_training_data is set to True, this is only done as a backup in case of no matches)"
            )
        if "entity_mappings" not in component_config:
            raise InvalidConfigException(
                f"your configuration is missing the section 'entity mappings', "
                f"which should contain mappings of Bin tags to slots in your domain, "
                f"e.g. contact:- ism"
            )
        bin_entity_tags = component_config["entity_mappings"]
        for key in bin_entity_tags.keys():
            domain = Domain.load("domain.yml")
            domain_dict = domain.as_dict()
            if key not in domain_dict["entities"]:
                raise InvalidConfigException(
                    f"{key} is listed as a slot mapping in your configuration "
                    f"but not as a valid slot in your domain."
                )
            for tag in bin_entity_tags[key]:
                if tag not in ALL_BIN_TAGS:
                    raise InvalidConfigException(
                        f"{tag} is listed as a possible tag in your configuration "
                        f"but does not exist in the Bin tagset."
                    )

    def process(self, messages: List[Message], **kwargs: Any) -> List[Message]:
        for message in messages:
            extracted = None
            tokens = message.data["text_tokens"]
            intent = message.get("intent")
            message_text = message.get("text")
            if self.component_config["match_training_data"]:
                # Check whether user message matches example in training data exactly,
                # but with labeled entity replaced with new entity
                matched_nlu_tokens = self.nlu_example_match(tokens, intent, message_text)
                extracted = self._match_entities(matched_nlu_tokens)
            if self.component_config["match_all_entities"]:
                if not extracted:
                    extracted = self._match_entities(tokens)
            for entity in message.get("entities"):
                if not extracted or extracted[0]["value"] in entity["value"]:
                    return messages
            message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
        return messages

    def _match_entities(self, tokens: List) -> List:
        extracted_entities = []
        matched_tag = None
        for token in tokens:
            tag, confidence = self.bin_lookup_tag(token.text)
            if tag:
                # Check whether the last token was also matched as an entity with the same tag,
                # in that case assume a multi-word token and concatenate.
                if matched_tag == tag:
                    extracted_entities[-1]["value"] += f" {token.text}"
                    extracted_entities[-1]["end"] = token.end
                else:
                    match = {
                        "start": token.start,
                        "end": token.end,
                        "value": token.text,
                        "confidence": confidence,
                        "entity": tag,
                        "extractor": self.name
                    }
                    extracted_entities.append(match)
                    matched_tag = tag
            else:
                matched_tag = None
        return extracted_entities

    def nlu_example_match(self, tokens: List, intent: Text, message_text: Text) -> List:
        entity_tokens = []
        for nlu_entry in self.nlu_examples()['nlu']:
            if 'intent' in nlu_entry and nlu_entry['intent'] == intent['name']:
                for intent_example in nlu_entry['examples'].split('\n'):
                    entity_type_matches = re.findall(r'\[(.*?)\][\{\(](.*?)[\)\}]', intent_example)
                    if entity_type_matches:
                        example_string = re.sub(r'\[(.*?)\][\{\(](.*?)[\)\}]', '(.*?)', intent_example)
                        example_string = example_string.removeprefix('- ')
                        if example_string.endswith('?'):
                            example_string = re.sub(r"\?$", r"\?", example_string)
                        re_match = re.search(example_string, message_text)
                        if re_match:
                            for i, match in enumerate(re_match.groups()):
                                start = message_text[:re_match.start(i + 1)].count(' ')
                                end = start + match.count(' ') + 1
                                matched_tokens = tokens[start:end]
                                for token in matched_tokens:
                                    entity_tokens.append(token)
                            return entity_tokens
        return entity_tokens

    def bin_lookup_tag(self, token: Text) -> Any:
        b = Bin()
        attributes = []
        bin_entity_tags = self.component_config["entity_mappings"]
        for option in [token.lower(), token.title()]:
            w, attr = b.lookup(option)
            if attr:
                attributes.append(attr)
        confidence = 1.0/len(attributes) if attributes else 1.0
        for key in bin_entity_tags.keys():
            for entry in attributes:
                if entry[0].hluti in bin_entity_tags[key]:
                    return key, confidence
        return None, None
