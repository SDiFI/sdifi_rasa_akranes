FROM rasa/rasa-sdk:3.0.6
USER root
RUN pip install rdflib==6.1.1
RUN pip install islenska==0.4.3
RUN mkdir -p /app/actions
RUN mkdir -p /app/src
COPY src/ /app/src
COPY offices_staff.rdf /app/offices_staff.rdf
COPY actions /app

ENV PYTHONPATH "${PYTHONPATH}:/app/src/akranes_info_api"

WORKDIR /app

EXPOSE 5005

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions"]
