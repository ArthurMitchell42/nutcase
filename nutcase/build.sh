#! /usr/bin/bash

# docker build . -t nutcase -f docker/Dockerfile
# docker buildx create --name mybuilder --use
# docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 -t kronos443/nutcase:V0.3.0 -t kronos443/nutcase:latest -f docker/Dockerfile --push .

# docker buildx build --platform linux/amd64,linux/arm64/v8 -t kronos443/nutcase:V0.3.0 -t kronos443/nutcase:latest -f docker/Dockerfile --push .
# docker buildx build --platform linux/amd64,linux/arm64/v8 -t kronos443/nutcase:V0.3.0Beta7 -t kronos443/nutcase:latest-beta -f docker/Dockerfile --push .


