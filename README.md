# sdifi_rasa_docker_3

Dockerfile & resources to build Rasa image (version 3.0) and data to train and test on.

## Installation & Docker build

The Convbert language model is included as a submodule, so either clone this directory using the command:

```bash
git clone --recurse-submodules git@github.com:SDiFI/sdifi_rasa_3_docker.git
```
or:

```bash
git clone git@github.com:SDiFI/sdifi_rasa_3_docker.git
git submodule update --init
```

Once everything is checked out and the repo cloned, run the following to build the docker image:

```bash
docker build -f dockerfile -t sdifi_rasa_3 .
```

## Training

To train the model:

```bash
docker run -v $(pwd):/app sdifi_rasa_3:latest train --domain domain.yml --data data --out models
```

## Running

To test the model (with default training data, can only respond to a greeting, a thank you, an empty message or a goodbye in Icelandic):

### Interactive shell

```bash
docker run -it -v $(pwd):/app sdifi_rasa_3:latest shell
```

(Add the --debug flag in order to view logs, confidence threshold of predictions, etc.)

### Web widget

In order to start rasa and test it via a web chat widget, expose port 5005 in docker and enable web api-access :

```bash
docker run -p 5005:5005 -it -v $(pwd):/app sdifi_rasa_3:latest run -m models --enable-api --cors "*" --debug
```

Then open the file [webchat/index.html](/webchat/index.html) in a web browser.
