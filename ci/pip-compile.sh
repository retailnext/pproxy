#!/bin/sh
set -eu
/usr/local/bin/pip install --disable-pip-version-check pip-tools
/usr/local/bin/pip-compile requirements.in
