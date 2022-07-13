FROM rasa/rasa:3.0.7-full
USER root
RUN pip install torch==1.10.0
RUN pip install transformers==4.12.5
# Patch this bug in sanic 21.9.3: https://github.com/sanic-org/sanic/issues/2272
RUN sed -i 's/subprotocols=Optional\[Sequence\[str\]\]/subprotocols: Optional[Sequence[str]] = None/' \
    /opt/venv/lib/python3.8/site-packages/sanic/server/protocols/websocket_protocol.py
COPY registry.py /opt/venv/lib/python3.8/site-packages/rasa/nlu/utils/hugging_face/registry.py
COPY lm_featurizer.py /opt/venv/lib/python3.8/site-packages/rasa/nlu/featurizers/dense_featurizer/lm_featurizer.py
COPY modeling_utils.py /opt/venv/lib/python3.8/site-packages/transformers/modeling_utils.py
