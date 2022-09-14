#! /bin/bash

MODEL_DIR=`pwd`/models
AUTH_TOKEN=${TOKEN:-sdifi}

if [ -n "$(ls -A ${MODEL_DIR} 2>/dev/null)" ]
then
  echo "Directory ${MODEL_DIR} contains files, incremental training ..."
  # We could do this, but for now, always make a full training when starting
  # rasa train --finetune
  rasa train
else
  echo "No models found in directory ${MODEL_DIR}, retraining ..."
  rasa train
fi

# Start Rasa, enable API, debugging and require a token when doing
# REST requests
rasa run --enable-api --cors "*" --debug --auth-token ${AUTH_TOKEN}
