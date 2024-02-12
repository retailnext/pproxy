FROM debian:11-slim@sha256:8481471cacd29779e7b6fe64a891f4b6771d8c3c7e57bb410542a3db10d1897a AS build
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

FROM gcr.io/distroless/python3-debian11:nonroot@sha256:3316bd4a55f3d10dee99bc06bf772e01aa6148805e9036a8ec5b4dbee984270b

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
