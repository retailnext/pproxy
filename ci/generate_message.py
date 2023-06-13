import pathlib
import pkg_resources


def load_requirements(name: str):
    with pathlib.Path(name).open() as f:
        reqs = {}
        for req in pkg_resources.parse_requirements(f):
            if len(req.specs) == 1 and len(req.specs[0]) == 2 and req.specs[0][0] == "==":
                reqs[req.project_name] = req.specs[0][1]
            else:
                reqs[req.project_name] = "Unknown"
        return reqs


def compare(old_versions: dict[str, str], new_versions: dict[str, str]):
    added = []
    updated = []
    removed = []
    for name in old_versions:
        if name not in new_versions:
            removed.append(name)
        elif old_versions[name] != new_versions[name]:
            updated.append((name, old_versions[name], new_versions[name]))
    for name in new_versions:
        if name not in old_versions:
            added.append(name)
    added.sort()
    updated.sort()
    removed.sort()
    return added, updated, removed


def format_differences(added: list[str], updated: list[tuple[str, str, str]], removed: list[str]):
    first = True
    if added:
        first = False
        print("Added:")
        for name in added:
            print("*   `{}`".format(name))
    if updated:
        if first:
            print("")
        first = False
        print("Updated:")
        for item in updated:
            print("*   `{}`: `{}` -> `{}`".format(item[0], item[1], item[2]))
    if removed:
        if first:
            print("")
        first = False
        print("Removed:")
        for name in removed:
            print("*   `{}`".format(name))


if __name__ == "__main__":
    oldR = load_requirements("requirements.txt.orig")
    newR = load_requirements("requirements.txt")
    a, u, r = compare(oldR, newR)
    format_differences(a, u, r)
