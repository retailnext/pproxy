FROM debian:12-slim@sha256:1371f816c47921a144436ca5a420122a30de85f95401752fd464d9d4e1e08271 AS build
RUN apt-get update \
&& apt-get install --no-install-suggests --no-install-recommends --yes \
gcc \
libpython3-dev \
libssl-dev \
python3-venv \
&& rm -rf /usr/local \
&& python3 -m venv /usr/local

COPY requirements.txt /requirements.txt

RUN /usr/local/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot@sha256:498e3cb48826d99bad1301994da60caa126b25c0ce03dc4e6a47a7c10fe02493

COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/usr/local/bin/pproxy"]
