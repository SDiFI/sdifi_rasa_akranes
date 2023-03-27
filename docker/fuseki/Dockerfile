## Licensed to the Apache Software Foundation (ASF) under one or more
## contributor license agreements.  See the NOTICE file distributed with
## this work for additional information regarding copyright ownership.
## The ASF licenses this file to You under the Apache License, Version 2.0
## (the "License"); you may not use this file except in compliance with
## the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

## Apache Jena Fuseki server Dockerfile.

## This Dockerfile builds a reduced footprint container.

ARG OPENJDK_VERSION=17
ARG ALPINE_VERSION=3.15.0
ARG JENA_VERSION=4.7.0

# Internal, passed between stages.
ARG FUSEKI_DIR=/fuseki
ARG FUSEKI_JAR=jena-fuseki-server-${JENA_VERSION}.jar
ARG JAVA_MINIMAL=/opt/java-minimal

## ---- Stage: Download and build java.
FROM openjdk:${OPENJDK_VERSION}-alpine AS base

ARG JAVA_MINIMAL
ARG JENA_VERSION
ARG FUSEKI_DIR
ARG FUSEKI_JAR
ARG REPO=https://repo1.maven.org/maven2
ARG JAR_URL=${REPO}/org/apache/jena/jena-fuseki-server/${JENA_VERSION}/${FUSEKI_JAR}

RUN [ "${JENA_VERSION}" != "" ] || { echo -e '\n**** Set JENA_VERSION ****\n' ; exit 1 ; }
RUN echo && echo "==== Docker build for Apache Jena Fuseki ${JENA_VERSION} ====" && echo

# Alpine: For objcopy used in jlink
RUN apk add --no-cache curl binutils

## -- Fuseki installed and runs in /fuseki.
WORKDIR $FUSEKI_DIR

## -- Download the jar file.
COPY ./docker/fuseki/download.sh .
RUN chmod a+x ./download.sh

# Download, with check of the SHA1 checksum.
RUN ./download.sh --chksum sha1 "$JAR_URL"

# Get binary distribution libraries
RUN wget https://dlcdn.apache.org/jena/binaries/apache-jena-${JENA_VERSION}.tar.gz
RUN tar xvf apache-jena-${JENA_VERSION}.tar.gz --strip-components=1 && rm apache-jena-${JENA_VERSION}.tar.gz

## -- Alternatives to download : copy already downloaded.
## COPY ${FUSEKI_JAR} .

## Use Docker ADD - does not retry, does not check checksum, and may run every build.
## ADD "$JAR_URL"

## -- Make reduced Java JDK

ARG JDEPS_EXTRA="jdk.crypto.cryptoki,jdk.crypto.ec"
RUN \
  JDEPS="$(jdeps --multi-release base --print-module-deps --ignore-missing-deps ${FUSEKI_JAR})"  && \
  jlink \
        --compress 2 --strip-debug --no-header-files --no-man-pages \
        --output "${JAVA_MINIMAL}" \
        --add-modules "${JDEPS},${JDEPS_EXTRA}"

ADD ./docker/fuseki/entrypoint.sh .
ADD ./docker/fuseki/log4j2.properties .
ADD ./docker/fuseki/ex.sparql .
ADD ./docker/fuseki/db_init.sh ./scripts/db_init.sh
ADD ./docker/fuseki/config.ttl ./configuration/config.ttl
ADD ./src/municipal_info_api/municipal_info_api.rdf /fuseki/rdf/initial.rdf


# Run as this user
# -H : no home directorry
# -D : no password

RUN adduser -H -D fuseki fuseki

## ---- Stage: Build runtime
FROM alpine:${ALPINE_VERSION}

## Import ARGs
ARG JENA_VERSION
ARG JAVA_MINIMAL
ARG FUSEKI_DIR
ARG FUSEKI_JAR

COPY --from=base /opt/java-minimal /opt/java-minimal
COPY --from=base /fuseki /fuseki
COPY --from=base /etc/passwd /etc/passwd

WORKDIR $FUSEKI_DIR

ARG LOGS=${FUSEKI_DIR}/logs
ARG DATA=${FUSEKI_DIR}/databases

RUN \
    mkdir -p $LOGS && \
    mkdir -p $DATA && \
    chown -R fuseki ${FUSEKI_DIR} && \
    chmod a+x ./entrypoint.sh

## Default environment variables.
ENV \
    JAVA_HOME=${JAVA_MINIMAL}           \
    JAVA_OPTIONS="-Xmx2048m -Xms2048m"  \
    JENA_VERSION=${JENA_VERSION}        \
    FUSEKI_JAR="${FUSEKI_JAR}"          \
    FUSEKI_BASE="${FUSEKI_DIR}"         \
    FUSEKI_DIR="${FUSEKI_DIR}"

USER fuseki

# This prepolulates the database with the initial.rdf file inside databases/DB2
# This can be overwritten by mounting a volume to /fuseki/databases/DB2
RUN \
    sh /fuseki/scripts/db_init.sh /fuseki/rdf/initial.rdf

EXPOSE 3030

# simple configuration
#ENTRYPOINT ["./entrypoint.sh", "--loc=databases/DB2", "--update", "/ds" ]

# configuration with config file
ENTRYPOINT ["ash", "-c", "echo $JAVA_OPTIONS && ./entrypoint.sh --conf=configuration/config.ttl"]
