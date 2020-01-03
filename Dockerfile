# ========== BUILD CONTAINER ===========
FROM ubuntu:18.04 as conjur-cli-builder

ENV INSTALL_DIR=/opt/conjur-api-python3

RUN apt-get update && \
    apt-get install -y bash \
                       binutils \
                       build-essential \
                       git \
                       libffi-dev \
                       libssl-dev \
                       python3 \
                       python3-dev \
                       python3-pip

RUN mkdir -p $INSTALL_DIR
WORKDIR $INSTALL_DIR

COPY requirements.txt $INSTALL_DIR/
RUN pip3 install -r requirements.txt

COPY . $INSTALL_DIR

RUN pyinstaller --onefile pkg_bin/conjur-cli


# ========== MAIN CONTAINER ===========
FROM ubuntu:18.04 as conjur-python-cli

ENTRYPOINT [ "/usr/local/bin/conjur-cli" ]

COPY --from=conjur-cli-builder "/opt/conjur-api-python3/dist/conjur-cli" \
                               /usr/local/bin/conjur-cli
