# rep-score-portal

TBD on a better description for this repo... 😬

<img width="1178" alt="Screen Shot 2022-06-05 at 11 59 31 PM" src="https://user-images.githubusercontent.com/31417712/172097833-b8b1f34f-79cb-439d-ac6d-6dc726d0ff7c.png">

## Installation
### Local Installation
```bash

# build the image
docker build --build-arg CODEARTIFACT_AUTH_TOKEN -t rep_score_portal .

# run the container in interactive mode, leaving port ``8501`` open for the Streamlit app
docker run \
    -it \
    --rm \
    -v "${PWD}:/rep_score_portal" \
    -v ${HOME}/.aws/config:/root/.aws/config \
    -v ${HOME}/.aws/cli/cache:/root/.aws/cli/cache \
    -v ${HOME}/.aws/sso/cache:/root/.aws/sso/cache \
    -e AWS_PROFILE="datascience" \
    -p 8501:8501 \
    rep_score_portal
```

## Launch the Tool
Once the Docker image is running, you can access the tool locally at [localhost:8501](http://localhost:8501/) (note that if you are running the tool on an EC2 instance, you'll need to replace `localhost` with your instance's public IP address).

You can log in with credentials:

**Username**: `user`

**Password**: `test`
