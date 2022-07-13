#!/bin/bash

sudo docker stop action-server2
sudo docker rm action-server2

sudo docker build -f dockerfile -t sdifi_rasa_3 .
sudo docker build -f sdk-dockerfile -t sdk_image .

sudo docker run -d -v $(pwd)/actions:/app/actions --net my-project3 --name action-server2 sdk_image:latest
sudo docker run -it -v $(pwd):/app -p 5005:5005 --net my-project3 sdifi_rasa_3:latest train
sudo docker run -it -v $(pwd):/app -p 5005:5005 --net my-project3 sdifi_rasa_3:latest shell
