#!/bin/bash

sudo docker-compose down;

sudo docker image prune -f
sudo docker volume prune -f

sudo docker network create nlp_project_default;

git pull;

# shellcheck disable=SC2116
sudo docker-compose build --no-cache;

sudo docker-compose up -d; 

sudo docker ps;
