import subprocess
import sys

# Check that python hasn't been unexpectedly upgraded
#
# If python has been upgraded, we need to make sure it's in sync with the
# build step and the constraint in renovate.json
if sys.version_info.major != 3 or sys.version_info.minor != 11:
    sys.exit(sys.version_info)

# Check that pycrypto isn't broken
import cryptography.hazmat.backends.openssl.backend

if not cryptography.hazmat.backends.openssl.backend:
    sys.exit('cryptography is not okay')

# Check that pproxy can be started
subprocess.check_call(["/usr/local/bin/pproxy", "--version"])
