# sdifi_rasa_akranes

Dockerfile & resources to build Rasa image (version 3.0) and data to train and test on for Akranes use case.

## Installation

The Convbert language model is included as a submodule, so either clone this directory using the command:

```bash
git clone --recurse-submodules git@github.com:SDiFI/sdifi_rasa_akranes.git
```
or:

```bash
git clone git@github.com:SDiFI/sdifi_rasa_akranes.git
git submodule update --init
```

## Docker build, training and testing

The docker commands to train and test the model are the same as in our original sdifi_rasa_docker_3 repo. The file restart.sh contains all commands necessary to build the docker images, start an action server called action-server2, train using the current data and run the rasa server in a shell. It expects a docker network called my-project3, so first create that network with the command:

```bash
docker network create my-project3
```

and then, if you have made changes to any data or code, you can re-build, train and open a rasa server with:

```bash
bash restart.sh
```
