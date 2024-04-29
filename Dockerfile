FROM debian:11-slim@sha256:715354035496a48b9c4c8f146a6f751de70449913773038776eb1f3d01c93989 AS build
RUN apt-get update \
&& apt-get install --no-install-suggests --no-install-recommends --yes \
gcc \
libpython3-dev \
libssl-dev \
python3-venv \
&& rm -rf /usr/local \
&& python3 -m venv /usr/local \
&& /usr/local/bin/pip install --upgrade pip setuptools wheel

COPY requirements.txt /requirements.txt

RUN /usr/local/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian11:nonroot@sha256:b3f703d85f101798a15e41a35cc6b1303f472225b7d02faef24c63e4806c5587

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
