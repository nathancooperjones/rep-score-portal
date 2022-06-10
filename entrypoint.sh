#!/bin/bash

# start the proxy service in the background
sh ssl-proxy.sh &

cd rep_score_portal

streamlit run app.py
