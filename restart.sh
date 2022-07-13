#!/bin/bash

docker stop action-server2
docker rm action-server2

docker build -f dockerfile -t sdifi_rasa_3 .
docker build -f sdk-dockerfile -t sdk_image .

docker run -d -v $(pwd)/actions:/app/actions --net my-project3 --name action-server2 sdk_image:latest
docker run -it -v $(pwd):/app -p 5005:5005 --net my-project3 sdifi_rasa_3:latest train
docker run -it -v $(pwd):/app -p 5005:5005 --net my-project3 sdifi_rasa_3:latest shell
