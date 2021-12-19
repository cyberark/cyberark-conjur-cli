# ========== BUILD CONTAINER ===========
FROM ubuntu:18.04 as conjur-cli-builder

ENV INSTALL_DIR=/opt/conjur-api-python3

RUN apt-get update && \
  apt-get install -y bash \
                    binutils \
                    build-essential \
                    curl \
                    git \
                    libffi-dev \
                    libssl-dev \
                    python3-dev \
                    zlib1g-dev

RUN mkdir -p $INSTALL_DIR
WORKDIR $INSTALL_DIR

# Install Python 3.10.1 using pyenv, wheel and required libs
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

COPY requirements.txt $INSTALL_DIR/
RUN curl -L -s https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
    && eval "$(pyenv init --path)" \
    && env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.1 \
    && pyenv global 3.10.1 \
    && pip install wheel \
    && pip install -r requirements.txt

COPY . $INSTALL_DIR

RUN pyinstaller --onefile pkg_bin/conjur


# ========== MAIN CONTAINER ===========
FROM ubuntu:18.04 as conjur-python-cli

ENTRYPOINT [ "/usr/local/bin/conjur" ]

COPY --from=conjur-cli-builder "/opt/conjur-api-python3/dist/conjur" \
                               /usr/local/bin/conjur
