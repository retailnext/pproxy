import subprocess

# Install pip-tools for the pip-compile command
subprocess.check_call(["/usr/local/bin/pip", "install", "--disable-pip-version-check", "pip-tools"])

# Run pip-compile to generate requirements.txt
subprocess.check_call(["/usr/local/bin/pip-compile", "requirements.in"])


def needs_uvloop_restriction() -> bool:
    from pkg_resources import parse_requirements
    from packaging.version import parse as parse_version
    pproxy_upgraded = False
    uvloop_upgraded = False
    with open("requirements.txt") as requirements_txt:
        for requirement in parse_requirements(requirements_txt):
            match requirement.name:
                case "uvloop":
                    uvloop_upgraded = parse_version(requirement.specs[0][1]) \
                                      >= parse_version("0.22")
                case "pproxy":
                    pproxy_upgraded = parse_version(requirement.specs[0][1]) \
                                      > parse_version("2.7.9")
    return uvloop_upgraded and not pproxy_upgraded


if needs_uvloop_restriction():
    # If pproxy is still 2.7.9 which is known to not work with uvloop >=0.22,
    # restrict the version of uvloop and re-generate requirements.txt.
    # See https://github.com/qwj/python-proxy/pull/202
    import pathlib

    # Directly writing to the requirements.in file that was copied in results
    # in a permission error, so write to a new file to append the restriction.
    p = pathlib.Path("requirements.in")
    p_new = pathlib.Path("requirements.in.new")
    p_new.write_text(p.read_text() + "uvloop<0.22\n")
    p_new.rename(p)
    subprocess.check_call(["/usr/local/bin/pip-compile", "requirements.in"])
