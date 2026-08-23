FROM nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356

LABEL org.opencontainers.image.base.name="nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04"
LABEL org.opencontainers.image.base.digest="sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"

ARG PYTHON_VERSION=3.12.11
ARG PYTHON_SHA256=7b8d59af8216044d2313de8120bfc2cc00a9bd2e542f15795e1d616c51faf3d6
ENV VAL_CONTAINER_IMAGE_DIGEST="sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
ENV PATH="/opt/val/.venv/bin:/opt/python/bin:${PATH}"

RUN test -n "${PYTHON_SHA256}" \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        build-essential ca-certificates curl libbz2-dev libffi-dev libgdbm-dev \
        liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev \
        tk-dev uuid-dev xz-utils zlib1g-dev \
    && curl --fail --location --proto '=https' --tlsv1.2 \
        "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
        --output /tmp/python.tgz \
    && echo "${PYTHON_SHA256}  /tmp/python.tgz" | sha256sum --check --strict \
    && mkdir /tmp/python-source \
    && tar --extract --gzip --file /tmp/python.tgz --directory /tmp/python-source --strip-components=1 \
    && cd /tmp/python-source \
    && ./configure --prefix=/opt/python --with-ensurepip=install \
    && make --jobs="$(nproc)" \
    && make install \
    && /opt/python/bin/python3.12 -m pip install --no-cache-dir uv==0.11.18 \
    && apt-get purge --yes --auto-remove build-essential curl \
    && rm -rf /var/lib/apt/lists/* /tmp/python-source /tmp/python.tgz

WORKDIR /opt/val
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY configs ./configs
RUN uv sync --frozen --no-dev

ENTRYPOINT ["val"]
