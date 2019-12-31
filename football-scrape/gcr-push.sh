#!/usr/bin/env bash

docker build -t py_scrape .

docker tag py_scrape:latest gcr.io/football-scrape/py_scrape:latest
docker push gcr.io/football-scrape/py_scrape:latest