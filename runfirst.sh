#!/bin/bash

#Run before opening in container to create mongodb container

docker run --name mongo -d mongodb/mongodb-community-server:latest --network host

