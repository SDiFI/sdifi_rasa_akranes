#!/bin/bash

export JENA_HOME=/fuseki
export PATH=$PATH:$JENA_HOME/bin

RDF_FILE=$1
if [ -z "$RDF_FILE" ]; then
  echo "Please provide RDF file as argument"
  exit 1
fi

mkdir -p databases/DB2
tdb2.tdbloader --loc databases/DB2 "$RDF_FILE"