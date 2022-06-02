FROM python:3.9
LABEL maintainer nathancooperjones@gmail.com

RUN apt-get update \
    && apt-get install -y vim \
    && apt-get install -y libpq-dev \
    && apt-get install -y gcc \
    && apt-get clean

USER root
WORKDIR /rep_score_portal

# copy files to container
COPY requirements.txt ./

# install libraries
RUN \
  pip3 install -U pip && \
  pip3 install -r requirements.txt

# copy the rest of the files over
COPY . .

CMD streamlit run app.py
