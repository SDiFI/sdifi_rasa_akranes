An example project to demonstrate a use case for a Rasa chatbot handling a municipality service center use case.
The example data is based around the well known municipality 'Andabær' and the chatbot is called 'Jóakim'.

## Setup

### Full setup via docker-compose
Clone the repo and run (docker-compose needs to be installed):

```bash
docker-compose build    # this builds action_server
docker-compose up
```

### Local development with Rasa

Create a virtual environment and install
all dependencies via the following command:

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Rasa needs certain configuration files to be present. For local development, these are:

```
./config.yml
./config/credentials.yml
./config/endpoints.yml
```

If Rasa should be able to train a model, the following files need to be present:

```
domain.yml
./data/nlu.yml
./data/rules.yml
./data/stories/stories.yml
```

#### Training

Train and test a model. The model file will be placed inside the directory `./models`. Rasa automatically uses the latest
trained model in the `models/` directory. Running cross-validation gives you valuable info about your model and training data.
Optionally, you can also disable sending of telemetry data home to Rasa.

```bash
rasa telemetry disable
rasa train --endpoints config/endpoints.yml --data data/ --config config.yml
rasa data validate --config config.yml --data data/
rasa test --endpoints config/endpoints.yml  --config config.yml -s tests/
```

To run cross validations:

```bash
rasa test --endpoints config/endpoints-standalone.yml  --config config.yml -s tests/ --cross-validation
```

This needs a long time, as there are multiple models trained and tested. All results are placed into the subdirectory
`results/`

#### Running Rasa

To start locally a standalone Rasa server, you need to start the action server in another terminal session as well. For
actions, we need to add the directory `src/municipal_info_api` to the variable `PYTHONPATH`.

```bash
export PYTHONPATH="`pwd`/src/municipal_info_api"
python -m rasa_sdk --actions actions --port 5055
```

Start the Rasa server:

```bash
rasa run -vv --credentials config/credentials.yml --endpoints config/endpoints.yml --port 8180 --cors "*" models/
```

#### Test actions / sparql queries

The following command runs tests for the SPARQL queries and Rasa actions:

```bash
pytest .
```

The SPARQL query tests are located [here](src/municipal_info_api/sparql_test.py`) and action tests
[here](tests/test_actions.py).

###  Connect to Rasa via web widget

You can use the web-widget for both approaches: starting Rasa via `docker-compose` or if you prefer using
the Python virtual environment.
Open the file `./webchat/index.html` with a web browser. It will automatically connect to the running Rasa server at
`localhost:8180`.

## Implemented intents

Currently, the system can identify the following intents:

* greet (_halló_, _hæ_, _góðan daginn_,)
* thank (_takk_, _kærar þakkir_)
* bye (_bless_, _vertu blessaður_)
* stop (_hætta við_, _ég vil byrja aftur_)
* affirm (_já_, _já ég er með aðra spurningu_)
* deny (_nei takk, þetta er komið_, _ekkert meira_)
* request contact (_hvernig næ ég í X_, _mig vantar að ná í Y_, _hver sér um Z_)
* inform (user answers to a question the bot needs to fill a slot)
* out of scope input
* no intent (empty input)
* chitchat:
  * ask the bot its name
  * ask about the weather
* faq:
  * population of Andabær


## Knowledge base

The knowledge base is stored in an RDF document (data/offices_staff.rdf) and uses the following ontologies:

* The Organization Ontology https://www.w3.org/TR/vocab-org/
* The vCard Ontology https://www.w3.org/TR/vcard-rdf/ (NS: http://www.w3.org/2006/vcard/ns#)
* The FOAF Ontology http://xmlns.com/foaf/0.1/
* The DBPedia Ontology https://dbpedia.org/ontology/

As well as RDF, RDFS and SKOS, along with some custom defined entities.

Andabær is defined as an Organization, having OrganizationalUnits connected to it 
as the different divisions (building and construction matters, education, welfare, etc.). Each of
the OrganizationalUnits has members which are defined as FOAF-entities with available contact information.
