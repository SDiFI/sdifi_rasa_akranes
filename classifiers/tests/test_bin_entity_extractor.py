"""Unit tests for BÍN entity extractor """

import pytest

from rasa.shared.exceptions import InvalidConfigException
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.tokenizers.tokenizer import Token

from classifiers.bin_entity_extractor import BinEntityExtractor

config = {
    "enable": True,
    "entity_mappings": {
        # city, place not in training data yet
        # "city": ['bær'],
        "contact": ['ism', 'gæl', 'föð', 'móð', 'erm'],
        # "place": ['fyr', 'göt', 'þor', 'örn']
    },
    "stop_words": ['á', 'dag', 'tala'],
    "match_training_data": True,
    "match_all_entities": False,
    "extraction_mode": "append"     # note: if you change this mode, also adapt processing_result below
}

messages = [Message(data={
    'text': 'tölvupóst hjá steinari adolfssyni',
    'message_id': '9f4b355fa6ca4e85936217fe8a4b27b7',
    'metadata': None,
    'text_tokens': [Token('tölvupóst', 0, 9), Token('hjá', 10, 13), Token('steinari', 14, 22),
                    Token('adolfssyni', 23, 33)],
    'intent': {'name': 'request_contact', 'confidence': 0.9999537467956543},
    'entities': [
        {'entity': 'email_or_phone', 'start': 0, 'end': 9, 'confidence_entity': 0.9997983574867249,
         'value': 'tölvupóst', 'extractor': 'DIETClassifier'},
        {'entity': 'contact', 'start': 14, 'end': 33, 'confidence_entity': 0.7713441848754883,
         'value': 'steinari adolfssyni', 'extractor': 'DIETClassifier'}
    ]
})]

match_entities_result = [
    {
        'entity': 'contact',
        'start': 14,
        'end': 33,
        'confidence_entity': 1.0,
        'value': 'steinari adolfssyni',
        'extractor': 'BinEntityExtractor'
    }
]

nlu_example_match_result = [
    [
        Token('tölvupóst', 0, 9),
        Token('steinari', 14, 22),
        Token('adolfssyni', 23, 33)
    ]
]

processing_result = [
    Message(data={'text': 'tölvupóst hjá steinari adolfssyni',
                  'message_id': '9f4b355fa6ca4e85936217fe8a4b27b7',
                  'metadata': None,
                  'text_tokens': [Token('tölvupóst', 0, 9),
                                  Token('hjá', 10, 13),
                                  Token('steinari', 14,  22),
                                  Token('adolfssyni', 23, 33)],
                  'intent': {'name': 'request_contact', 'confidence': 0.9999537467956543},
                  'entities': [{'entity': 'email_or_phone', 'start': 0, 'end': 9, 'confidence_entity': 0.9997983574867249,
                                'value': 'tölvupóst', 'extractor': 'DIETClassifier'},
                               {'entity': 'contact', 'start': 14, 'end': 33, 'confidence_entity': 0.7713441848754883,
                                'value': 'steinari adolfssyni', 'extractor': 'DIETClassifier'},
                               {'start': 14, 'end': 33, 'value': 'steinari adolfssyni', 'confidence_entity': 1.0,
                                'entity': 'contact', 'extractor': 'BinEntityExtractor'}]})
]


def test_create():
    bin_entity_extractor = BinEntityExtractor.create(
        config=config,
        model_storage=None,
        resource=None,
        execution_context=None
    )
    assert isinstance(bin_entity_extractor, BinEntityExtractor)


def test_validate_component_config():
    valid_config = config.copy()
    invalid_config = config.copy()
    invalid_config.pop('entity_mappings')  # making the config invalid

    # Test with a valid config, should not raise an exception
    try:
        BinEntityExtractor.validate_component_config(valid_config)
    except InvalidConfigException:
        pytest.fail("validate_component_config raised InvalidConfigException unexpectedly!")

    # Test with an invalid config, should raise an exception
    with pytest.raises(InvalidConfigException):
        BinEntityExtractor.validate_component_config(invalid_config)


def test_match_entities():
    extractor = BinEntityExtractor(config)
    message = messages[0]
    tokens = message.data["text_tokens"]

    actual_result = extractor._match_entities(tokens, config['stop_words'])
    expected_result = [match_entities_result[0]]
    assert actual_result == expected_result, "The _match_entities function did not return the expected result."


def test_nlu_example_match():
    extractor = BinEntityExtractor(config)
    message = messages[0]
    tokens = message.get("text_tokens")
    intent = message.get("intent")
    message_text = message.get("text")

    actual_result = extractor.nlu_example_match(tokens, intent, message_text)
    expected_result = nlu_example_match_result[0]
    assert actual_result == expected_result, "The nlu_example_match function did not return the expected result."


def test_process():
    bin_entity_extractor = BinEntityExtractor.create(
        config=config,
        model_storage=None,
        resource=None,
        execution_context=None
    )

    processed_messages = bin_entity_extractor.process(messages)

    assert len(processed_messages) == 1
    assert isinstance(processed_messages[0], Message)
    actual_result = processed_messages[0].get('entities')
    expected_result = processing_result[0].get('entities')
    assert actual_result == expected_result, "The process function did not return the expected result."
