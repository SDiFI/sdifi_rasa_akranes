![Build](https://github.com/SDiFI/sdifi_rasa_akranes/actions/workflows/rasa.yml/badge.svg?event=push)

An example project to demonstrate a use case for a Rasa chatbot handling a municipality service center use case.
The example data is based around the well known municipality 'Andabær' and the chatbot is called 'Jóakim'.

## Setup/Installation

### Running via docker-compose
This is the recommended way to run Rasa in a production environment. Clone the repo. Add a new file `.env` with the
following contents set:

```bash
RASA_VERSION=3.4.2                        # Rasa version to use, you should also set an appropriate Rasa SDK version
                                          # when building the action_server via docker/sdk/Dockerfile
                                          # in case the major or minor number changes
RASA_TOKEN=<some_rasa_token>              # Access token for using the Restful API of Rasa
RABBITMQ_PASSWORD=<some_rabbitmq_passwd>  # Password to use for RabbitMQ
DB_PASSWORD=<some_database_passwd>        # PostgreSQL password
RASA_TELEMETRY_ENABLED=false              # Set to true in case you want to send anonymous usage data to Rasa
DEBUG_MODE=true                           # Set to false, if you don't want lots of infomration from Rasa
FUSEKI_VERSION=4.7.0
```
You can also use the provided `.env.template` file as an example.

Currently, the docker-compose setup is only meant for running a Rasa instance with an already trained model
from the directory `./models`. To train a model, the local development method should be used before starting Rasa
in this way (see further down). Rasa always uses the model with the latest timestamp in case multiple model files exist
inside `models/`

After training, run the following commands: (docker-compose needs to be installed):

```bash
docker-compose build    # this builds the action_server, fuseki, etc.
# This (optional) step prepares the fuseki-data volume to import RDF data mounted as docker-volume. By default, the
# RDF database is already prepared with default contents of `src/municipal_info_api/offices_staff.rdf`. If you activate
# the commented-out Fuseki DB volume, use the following snippet to prepare the volume with dummy data. Please refer
# to [docker-compose.yml](docker-compose.yml) service definition if you want to use a different RDF file as
# initial DB
docker-compose run --rm --entrypoint="sh /fuseki/scripts/db_init.sh /fuseki/rdf/initial.rdf" fuseki
# This starts all services

docker-compose up
```

To test availability of the Fuseki server, try the following command that runs a query inside the fuseki container:

``` bash
docker exec -it fuseki_server bin/rsparql --query ex.sparql --service=http://localhost:3030/ds/query
```

It should return something like:

``` bash
--------------------
| role             |
====================
| "Skólamál"       |
| "Stjórnsýslumál" |
| "Launamál"       |
| "Velferðarmál"   |
--------------------
```

#### Replace the database

If you need to change or add information in the knowledge base, you can do so by editing the RDF-file (or creating a new
one), deleting the Fuseki database and replacing it with your new or updated data. Assuming there is a folder ```rdf/```
in the project root folder containing a new RDF-file ```updated_kb.rdf```, the steps to replace the Fuseki database are 
as follows:

``` bash
# Go into the Fuseki container and delete the database
docker exec -it fuseki_server rm -rf databases/DB2/Data-0001/
# Stop all containers so that we can perform the dataloading, then, similar as above, but with the /rdf directory mounted:
docker-compose run --rm  -v $(pwd)/rdf:/fuseki/rdf/ --entrypoint="sh /fuseki/scripts/db_init.sh /fuseki/rdf/updated_kb.rdf" fuseki
# Start the containers again
```

### Local development with Rasa

Currently, this approach is necessary to train a model, but is also similar to the setup stated inside the official [Rasa
documentation](https://rasa.com/docs/rasa/installation/environment-set-up). However, for a production setup this approach
should not be used.

Create a virtual environment (use Python 3.9, not 3.10) and install all dependencies via the following command:

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

Train and test a model. The model file will be placed inside the directory `./models`. As mentioned above, Rasa
automatically uses the latest trained model inside directory `models/` when started. You can also cross-validate
your model. Running cross-validation gives you valuable info about your model and training data.

Optionally, you can disable sending of telemetry data home to Rasa.

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

This needs a long time, as there are multiple models trained and tested. All test and cross-validation results are
placed into the subdirectory `results/`

#### Running Rasa

To start locally a standalone Rasa server, you need to start the action server in another terminal session as well. For
actions, we need to add the directory `src/municipal_info_api` to the variable `PYTHONPATH`, and for querying the 
Fuseki database, we need to add 'localhost' to the variable `FUSEKI_NETWORK_HOST`:

```bash
export PYTHONPATH="`pwd`/src/municipal_info_api"
export FUSEKI_NETWORK_HOST="localhost"
python -m rasa_sdk --actions actions --port 5055
```

The Fuseki service needs to be up (and already built, see section on setup) and can be started on its own by running:

```bash
docker-compose up fuseki -d
```

Note that, when running a standalone Rasa server, in order to be able to update the RDF file used to initialise the 
database, the file `fuseki_override_template.yml` needs to be renamed `docker-compose.override.yml` and the following
lines in the file `docker-compose.yml` need to be uncommented:

```bash
# Under the 'fuseki' service section, towards the end of the file:


#volumes:
#  - fuseki-data:/fuseki/databases/DB2

#depends_on:
#  fuseki-init:
#    condition: service_completed_successfully

```

Start the Rasa server:

```bash
rasa run -vv --credentials config/credentials.yml --endpoints config/endpoints.yml --port 8180 --cors "*" models/
```

#### Test actions / SPARQL queries

The following command runs tests for the SPARQL queries and Rasa actions:

```bash
# If not exported already, see 'Running Rasa' section:
export PYTHONPATH="`pwd`/src/municipal_info_api"
export FUSEKI_NETWORK_HOST="localhost"

pytest .
```

The SPARQL query tests are located [here](src/municipal_info_api/sparql_test.py) and action tests
[here](tests/test_actions.py).

### Integration with Masdif
The Rasa server can be integrated with [Masdif](https://github.com/SDiFI/masdif). The provided docker-compose snippet
[masdif_override_template.yml](masdif_override_template.yml) can be used to start the Rasa server and Masdif together.
Please refer to the documentation of Masdif for further details.

###  Talk to Rasa via web widget

You can use the web-widget for both approaches: starting Rasa via `docker-compose up` or if you prefer using
the Python virtual environment.
Open the file `./webchat/index.html` with a web browser. It will automatically connect to the running Rasa server at
`localhost:8180`.

In case you start Rasa via `docker-compose up`, you can simply navigate with your browser to URL http://localhost:8180 and
the web widget is served directly from Nginx.

## Implemented intents

Currently, the system can identify the following intents:

* greet (_halló_, _hæ_, _góðan daginn_,)
* thank (_takk_, _kærar þakkir_)
* bye (_bless_, _vertu blessaður_)
* stop (_hætta við_, _ég vil byrja aftur_)
* affirm (_já_, _já ég er með aðra spurningu_)
* deny (_nei takk, þetta er komið_, _ekkert meira_)
* request contact (_hvernig næ ég í X_, _mig vantar að ná í Y_, _hver sér um Z_)
* ask joke (_kanntu brandara_, _segðu mér eitthvað fyndið_)
* ask operator (_get ég fengið samband við þjónustufulltrúa_, _má ég tala við manneskju_)
* inform (user answers to a question the bot needs to fill a slot)
* out of scope input
* no intent (empty input)
* chitchat:
  * ask the bot its name
  * ask about the weather
* faq:
  * population of Andabær

## Knowledge base

The knowledge base is initialised via an RDF document (`src/municipal_info_api/offices_staff.rdf`) and uses the following ontologies:

* The Organization Ontology https://www.w3.org/TR/vocab-org/
* The vCard Ontology https://www.w3.org/TR/vcard-rdf/ (NS: http://www.w3.org/2006/vcard/ns#)
* The FOAF Ontology http://xmlns.com/foaf/0.1/
* The DBPedia Ontology https://dbpedia.org/ontology/

As well as RDF, RDFS and SKOS, along with some custom defined entities.

Andabær is defined as an Organization, having OrganizationalUnits connected to it 
as the different divisions (building and construction matters, education, welfare, etc.). Each of
the OrganizationalUnits has members which are defined as FOAF-entities with available contact information.

**All names inside the knowledge base are invented and shall not refer to real persons.**
