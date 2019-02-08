FROM python:3.7-alpine

ENV INSTALL_DIR=/opt/conjur-api-python3

RUN mkdir -p $INSTALL_DIR
WORKDIR $INSTALL_DIR

COPY requirements.txt $INSTALL_DIR/
RUN pip install -r requirements.txt

COPY . $INSTALL_DIR
