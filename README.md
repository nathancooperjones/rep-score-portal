# rep-score-portal

TBD on a better description for this repo... 😬

<img width="1178" alt="Screen Shot 2022-06-05 at 11 59 31 PM" src="https://user-images.githubusercontent.com/31417712/172097833-b8b1f34f-79cb-439d-ac6d-6dc726d0ff7c.png">

## Building and Running the PRD Container
On the EC2 instance with the SSL credentials available, you can run the following command to build both the Streamlit and NGINX containers.

```bash
# to just run the image normally...
sudo docker-compose up

# ... or to rebuild the image and start over, essentially
sudo docker-compose up --build --force-recreate --no-deps --remove-orphans
```

Once the Docker image is running, you can access the tool online at [repscoreportal.org](https://repscoreportal.org/).

## Building and Running the Local Container
Running the container locally, you'll want to avoid using the ``repscoreportal.org`` URL and just use ``localhost``. To do this, we'll just manually build and run the Streamlit Docker container only:

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

Once the Docker image is running, you can access the tool locally at [localhost:8501](http://localhost:8501/).

For now, you can log in with credentials:

**Username**: `user`

**Password**: `test`
