FROM debian:11-slim@sha256:d5dd14ffead88f6e0cdc4d9b5e8ce7b748e5e0ee9294aa0e566f39f2e85bc55e AS build
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

FROM gcr.io/distroless/python3-debian11:nonroot@sha256:1f3d3b5d5cc11a3695349f30bc8064e7b25d2ff11854c99aff8200c6d2f72d7d

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
