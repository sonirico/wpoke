FROM python:3.7.4-alpine3.10 as build-python

RUN apk add --update --no-cache git g++ gcc make \
    libxml2-dev py3-lxml libxslt-dev libffi-dev openssl-dev \
    shared-mime-info

ARG VERSION="0.1.4"
ARG UVLOOP="0.13.0"

WORKDIR /
RUN git clone https://github.com/sonirico/wpoke.git
WORKDIR /wpoke/

RUN git checkout ${VERSION} \
    && pip install -U pip \
    && pip install uvloop==${UVLOOP} \
    && pip install --no-cache -r requirements.lock \
    && python setup.py install;

ENTRYPOINT ["python", "wpoke-cli.py"]
