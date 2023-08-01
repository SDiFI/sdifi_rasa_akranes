# BÍN entity extractor. This extractor uses the BÍN database to extract entities from the user input.
# The BÍN database is a database of Icelandic words and their inflections. This extractor is useful
# for extracting entities that are not in the training data or are inflections of entities that are in the
# training data. For example, if the user asks for the mayor of a town that is in the training data but uses a
# different inflection, this extractor will extract the entity.
# If placed inside the pipeline behind other entity extractors, this extractor will only extract entities which are not
# already extracted.
#
# Note: This entity extractor does not rely on any featurizer as it extracts features on its own.

from typing import Dict, Text, Any, List
import logging
import string
import re
import yaml

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.exceptions import InvalidConfigException
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.core.domain import Domain

from islenska import Bin

# see https://bin.arnastofnun.is/gogn/storasnid/ord/
ALL_BIN_TAGS = ["heö", "alm", "ism", "föð", "móð", "fyr", "bibl", "gæl", "lönd", "gras", "efna", "tölv", "lækn",
                "örn", "tón", "natt", "göt", "lög", "íþr", "málfr", "tími", "við", "fjár", "bíl", "ffl", "mat",
                "bygg", "tung", "erl", "hetja", "bær", "þor", "mvirk", "brag", "jard", "stærð", "hug", "erm",
                "mæl", "titl", "gjald", "stja", "dýr", "hann", "ætt", "ob", "entity", "spurn"]

logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False
)
class BinEntityExtractor(GraphComponent, EntityExtractorMixin):

    def __init__(self, component_config: Dict[Text, Any]) -> None:
        self.component_config = component_config
        self.validate_component_config(component_config=self.component_config)
        self.domain = Domain.load("domain.yml")

    @staticmethod
    def nlu_examples() -> Dict:
        with open('data/nlu.yml', 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples['nlu']

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
        if "enable" not in component_config or not component_config["enable"]:
            logger.info("BÍN Entity extractor: disabled")
            return

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
        else:
            logger.info("Rasa/BÍN Entity mappings: " + str(component_config["entity_mappings"]))

        if "stop_words" not in component_config:
            logger.warning("No stop words specified. This may lead to false positives.")

        if "extraction_mode" not in component_config:
            raise InvalidConfigException(
                f"your configuration is missing the section 'extraction_mode', "
                f"which should contain the extraction mode, either 'append', 'overwrite' or 'skip'"
            )
        if component_config["extraction_mode"] not in ['append', 'overwrite', 'skip']:
            raise InvalidConfigException(
                f"your configuration should contain the section 'extraction_mode' and a value of 'append', 'overwrite' "
                f"or 'skip'. Please specify whether the featurizer should append, overwrite or skip entities that "
                f"are already extracted."
            )
        logger.info("BÍN Entity extractor: extraction mode: " + str(component_config["extraction_mode"]))

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

    @classmethod
    def find_entity_with_value(cls, dicts: List[Dict[Text, Any]], value: Text):
        for d in dicts:
            if value in d.values():
                return d
        return None

    def process(self, messages: List[Message], **kwargs: Any) -> List[Message]:
        is_enabled = self.component_config.get("enabled", True)
        if not is_enabled:
            return messages

        stop_words = self.component_config.get("stop_words", [])
        extraction_mode = self.component_config.get("extraction_mode")

        for message in messages:
            # logger.info("BÍN Entity extractor: processing message: " + str(message.data))
            tokens = message.data["text_tokens"]
            intent = message.get("intent")
            message_text = message.get("text")

            # Check whether user message matches example in training data exactly,
            # but with labeled entity replaced with new entity
            if self.component_config["match_training_data"]:
                # overwrite tokens with detected tokens from training examples
                tokens = self.nlu_example_match(tokens, intent, message_text)
            extracted = self._match_entities(tokens, stop_words)
            if extracted:
                if extraction_mode == 'append':
                    message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
                else:
                    entities = message.get("entities")
                    d = BinEntityExtractor.find_entity_with_value(entities, extracted[0]["value"])
                    if d is not None:
                        if extraction_mode == 'skip':
                            # If the entity is already extracted, we don't want to add it to the list of entities
                            # again, so we skip it.
                            continue
                        elif extraction_mode == 'overwrite':
                            d.update(extracted[0])
                    else:
                        message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
        return messages

    def _match_entities(self, tokens: List, stop_words: List) -> List:
        extracted_entities = []
        matched_tag = None
        tag = None
        confidence = 0.0
        for token in tokens:
            if token.text not in stop_words:
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
                        "confidence_entity": confidence,
                        "entity": tag,
                        "extractor": self.name
                    }
                    extracted_entities.append(match)
                    matched_tag = tag
            else:
                matched_tag = None
        return extracted_entities

    # Check whether user message matches example in training data exactly,
    # but with labeled entity replaced with matchall regex. In that case, return the tokens
    # that match the entity.
    #
    # Example: training example: "[email]{"entity": "email_or_phone", "value": "email"} hjá [Ástu Jónu](contact)?"
    #          message_text: "tölvupóst hjá steinari adolfssyni"
    #           -> matchall regex: "(.*) hjá (.*)"
    #           -> match: "tölvupóst" and "steinari adolfssyni"
    #           -> returned tokens [
    #                   Token('tölvupóst', 0, 9),
    #                   Token('steinari', 14, 22),
    #                   Token('adolfssyni', 23, 33)
    #               ]
    # @param tokens: List of tokens from the user message passed to the extractor
    # @param intent: Intent of the user message passed to the extractor
    # @param message_text: Text of the user message passed to the extractor
    #
    # @return: List of tokens that match entities in the user message according to the training data
    def nlu_example_match(self, tokens: List, intent: Any, message_text: Text) -> List:
        entity_tokens = []
        LABEL_REGEX = r'\[(.*?)\][\{\(](.*?)[\)\}]'
        REPLACE_PATTERN = '(.*)'
        for nlu_entry in self.nlu_examples():
            if 'intent' in nlu_entry and nlu_entry['intent'] == intent['name']:
                for intent_example in nlu_entry['examples'].split('\n'):
                    if re.findall(LABEL_REGEX, intent_example):
                        # replace the entity label with a matchall regex, so that we can match the entity values
                        # in the user message
                        training_string = re.sub(LABEL_REGEX, REPLACE_PATTERN, intent_example)
                        # remove leading dash and trailing question mark from training example
                        training_string = training_string.removeprefix('- ').rstrip("?").rstrip()
                        re_match = re.search(training_string, message_text)
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
        # find all possible BÍN attributes for the token
        w, attr = b.lookup(token.lower(), False, True)
        if attr:
            attributes.append(attr)
        confidence = 1.0 / len(attributes) if attributes else 1.0
        for key in bin_entity_tags.keys():
            for entry in attributes:
                if entry[0].hluti in bin_entity_tags[key]:
                    return key, confidence
        return None, None
