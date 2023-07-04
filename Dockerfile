FROM debian:11-slim@sha256:3460d74bec6b88496cd183d7731930be55234c094f581f7dbdd96f56c1fc34d8 AS build
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

FROM gcr.io/distroless/python3-debian11:nonroot@sha256:cc7021d6bd5aae9cdd976ae4b185cc59d5792b18aa5e18345dbf9b34d6b3f5a0

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
