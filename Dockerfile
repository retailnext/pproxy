FROM debian:11-slim@sha256:0d4827050fc382d8acc8462138244b417eaa73978f48597fe1d6741554db5689 AS build
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

FROM gcr.io/distroless/python3-debian11:nonroot@sha256:f3331305dc14092a6df5a23733b3afc5806da8bab8089e63f441221ebcdb7cfb

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
