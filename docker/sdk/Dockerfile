FROM rasa/rasa-sdk:3.4.0
USER root
RUN pip install --upgrade pip
RUN pip install --no-cache-dir rdflib==6.1.1
RUN pip install --no-cache-dir --default-timeout=100 islenska==0.4.5
RUN mkdir -p /app/src
COPY src/ /app/src
COPY data/offices_staff.rdf /app/offices_staff.rdf
COPY actions/actions.py /app/actions/actions.py

ENV PYTHONPATH "${PYTHONPATH}:/app/src/municipal_info_api"

WORKDIR /app

EXPOSE 5055

# Switch back to non-root to run code
USER 1001

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]
