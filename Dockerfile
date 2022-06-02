FROM python:3.9
MAINTAINER data-science@themomproject.com

RUN apt-get update \
    && apt-get install -y vim \
    && apt-get install -y libpq-dev \
    && apt-get install -y gcc \
    && apt-get clean

USER root
WORKDIR /nerds_qa

# copy files to container
COPY requirements.txt ./

ARG CODEARTIFACT_AUTH_TOKEN

# install libraries
RUN \
  pip3 install -U pip && \
  pip3 config set global.index-url "https://aws:$CODEARTIFACT_AUTH_TOKEN@datascience-670623442388.d.codeartifact.us-east-1.amazonaws.com/pypi/ds_libraries/simple/" && \
  pip3 install -r requirements.txt

# copy the rest of the files over
COPY . .

CMD streamlit run app.py
