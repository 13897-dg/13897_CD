#!/bin/bash

source environment.sh

FLASK_APP=Server.py

export FLASK_APP

FLASK_BIN=${Directory_PythonEnv}/bin/flask

${FLASK_BIN} run --port ${Port} --host="0.0.0.0"


