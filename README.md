# rep-score-portal

TBD on a better description for this repo... 😬

<img width="1178" alt="Screen Shot 2022-06-05 at 11 59 31 PM" src="https://user-images.githubusercontent.com/31417712/172097833-b8b1f34f-79cb-439d-ac6d-6dc726d0ff7c.png">

## Building and Running the PRD Container
```bash
sudo bash init-letsencrypt.sh

sudo docker-compose up
```

## Installation
### Local Installation
```bash

# build the image
docker build -t rep_score_portal .

# run the container in interactive mode, leaving port ``80`` open for the Streamlit app
docker run \
    -it \
    --rm \
    --shm-size 16G \
    -v "${PWD}:/rep_score_portal" \
    -p 80:80 \
    rep_score_portal
```

## Launch the Tool
Once the Docker image is running, you can access the tool locally at [localhost:85](http://localhost/) (note that if you are running the tool on an EC2 instance, you'll need to replace `localhost` with your instance's public IP address).

You can log in with credentials:

**Username**: `user`

**Password**: `test`
