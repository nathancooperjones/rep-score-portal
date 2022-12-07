# rep-score-portal

Portal to upload, track, and view assets' Representation Score, built entirely in Streamlit.

[![CI](https://github.com/nathancooperjones/rep-score-portal/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/nathancooperjones/rep-score-portal/actions/workflows/ci.yaml)

![Screenshot of the Rep Score Portal UI](https://user-images.githubusercontent.com/31417712/173125041-68d320c3-3df6-47f7-9d06-3ac5c81ee85a.png)

## Building and Running the PRD Container

A simple one-liner that builds and runs the container without mounting any local volumes into the container. This way, if we update any file with a change we don't want to be deployed yet (while the application is running), the application will not auto-update with this new file (which is the current behavior of this Streamlit application).

```bash
# to just run the image normally...
sudo docker-compose up

# ... or to rebuild the image and start over, essentially
sudo docker-compose up --build --force-recreate --no-deps --remove-orphans
```

Once the Docker image is running, you can access the tool online at [repscoreportal.org](https://repscoreportal.org/).

## Building and Running the Local Container

Running the container locally, we'll likely want to have a bit more control over running the Docker image to do things such as mounting our local folder, experimenting more with the ports opened, etc. To do this, you can manually build and run the Docker image with the following commands:

```bash
# build the image
docker build -t rep_score_portal .

# run the container in interactive mode, opening port ``8501``
docker run \
    -it \
    --rm \
    -v "${PWD}:/rep_score_portal" \
    -p 8501:8501 \
    rep_score_portal
```

Once the Docker image is running, you can access the tool locally at [localhost:8501](http://localhost:8501/).
