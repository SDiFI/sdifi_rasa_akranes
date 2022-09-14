# sdifi_rasa_akranes

Dockerfile & resources to build Rasa image (version 3.0) and data to train and test on for Akranes use case.

## Installation

Make sure git lfs is installed to pull large files from the repo.

```bash
git lfs install
```

Also, you need to install docker, docker-compose:

```bash
sudo apt-get update
sudo apt-get install docker docker-compose
```

The Convbert language model is included as a submodule, so either clone this directory using the command:

```bash
git clone --recurse-submodules git@github.com:SDiFI/sdifi_rasa_akranes.git
```
or:

```bash
git clone git@github.com:SDiFI/sdifi_rasa_akranes.git
git submodule update --init
```

## Docker build, training and running

The docker commands to train and test the model are now different than in our original sdifi_rasa_docker_3 repo. The file restart.sh is adapted to contain all commands necessary to build the docker images, start an action server, train using the current data and run the rasa server:

```bash
bash restart.sh
```

This will start up a few services, including a Nginx server that listens on `localhost:8080`. Please be patient for the training stage to be completed and watch the logs until Rasa states in the console:

```
Rasa server is up and running
```

Rasa is configured to start in debugging mode and the REST API is by default available at `<server>:<port>/rasa` and can be fully accessed when given the correct token, which can be customized via environment variable (described further down). 

Example:

```curl
curl -X GET "localhost:8080/rasa/status"?token=topsecret
````

The web chat widget directs its web socket calls to the server's `/rasa/cable` route via Nginx.

### Customizing docker build

The `docker-compose.yml` file lets you customize some variables. These variables can be set via the file `docker/.env`:

Example:

```
NGINX_PORT=8780
REGISTRY_URL="registry.someurl.com/sdifi/"
APPLICATION_VERSION=v0.1
TOKEN=topsecret
```

In the above example, the Nginx server would listen on port `8780` when starting the service `web`, the container registry would be `registry.someurl.com/sdifi/` and the container tag for the services `action_server` and `sdifi_akranes` would be set to `v0.1`. The Rasa REST API can be fully accessed via the token `topsecret`, some unprivileged REST API endpoints are accessible without authentication as well (as e.g. `rasa/status`).

After building the container via `docker-compose -f docker/docker-compose.yml build`, you could then push the images to the registry via `docker-compose -f docker/docker-compose.yml push`.
