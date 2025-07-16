#!/bin/bash
docker-compose exec --user root titanic-api pytest ./tests/ -v