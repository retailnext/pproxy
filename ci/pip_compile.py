import subprocess

# Install pip-tools for the pip-compile command
subprocess.check_call(["/usr/local/bin/pip", "install", "--disable-pip-version-check", "pip-tools"])

# Run pip-compile to generate requirements.txt
subprocess.check_call(["/usr/local/bin/pip-compile", "requirements.in"])
