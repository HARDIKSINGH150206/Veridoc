"""Check the repo folder tree against docs/ARCHITECTURE.md and .github/CODEOWNERS.

Dev helper. Run from anywhere: python3 scripts/check_folder_tree.py
Exit code 0 if everything matches, 1 otherwise.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def tree_paths(md: str) -> list[str]:
    found = re.search(r"```\n(Veridoc/\n.*?)```", md, re.S)
    if found is None:
        raise SystemExit("could not find the Veridoc/ tree block in ARCHITECTURE.md")
    block = found.group(1)
    stack: list[tuple[int, str]] = []
    out: list[str] = []
    for line in block.splitlines()[1:]:
        m = re.match(r"^([│ ]*)(?:├──|└──) (\S+)", line)
        if not m:
            continue
        depth = len(m.group(1)) // 4
        name = m.group(2)
        stack = stack[:depth]
        parent = "/".join(n for _, n in stack)
        full = f"{parent}/{name}".lstrip("/") if parent else name
        stack.append((depth, name.rstrip("/")))
        out.append(full)
    return out


def expand(path: str, line_text: str) -> list[str]:
    if path.endswith("screens/"):
        return [path] + [f"{path}s{i}-*" for i in range(1, 13)]
    return [path]


def exists(path: str) -> bool:
    p = path.rstrip("/")
    return bool(list(ROOT.glob(p))) if "*" in p else (ROOT / p).exists()


arch = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
paths = tree_paths(arch)
checked = 0
for raw in paths:
    if raw.startswith("pyproject.toml"):
        continue  # dependency files are created together with the code
    for p in expand(raw, ""):
        checked += 1
        if not exists(p):
            errors.append(f"in ARCHITECTURE tree but missing on disk: {p}")

# every top-level entry on disk should appear in the tree
top_in_tree = {p.split("/")[0] for p in paths}
top_in_tree |= {"pyproject.toml", "uv.lock", ".git"}


def git_ignored(name: str) -> bool:
    return (
        subprocess.run(
            ["git", "check-ignore", "-q", name], cwd=ROOT, capture_output=True
        ).returncode
        == 0
    )


for entry in sorted(ROOT.iterdir()):
    if git_ignored(entry.name):
        continue  # caches and virtual environments are not part of the tree
    if entry.name not in top_in_tree and entry.name not in {"CONTRIBUTING.md", "SECURITY.md"}:
        errors.append(f"on disk but not in ARCHITECTURE tree: {entry.name}")

# CODEOWNERS paths exist and are covered by the tree
co = [
    line.split()[0]
    for line in (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
]
tree_set = {p.rstrip("/") for p in paths}
for c in co:
    rel = c.lstrip("/").rstrip("/")
    if rel in {"pyproject.toml", "uv.lock"}:
        continue
    checked += 1
    if not exists(rel):
        errors.append(f"in CODEOWNERS but missing on disk: {c}")
    if rel not in tree_set and not any(t.startswith(rel + "/") for t in tree_set):
        errors.append(f"in CODEOWNERS but not in ARCHITECTURE tree: {c}")


# ownership tables must list the same paths in every document
def owned(path: str) -> dict[str, set[str]]:
    res: dict[str, set[str]] = {}
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (\d)\. [^|]+\|([^|]+)\|", line)
        if m:
            res[m.group(1)] = set(re.findall(r"`([^`]+)`", m.group(2)))
    return res


ref = owned("docs/ARCHITECTURE.md")
if len(ref) != 4:
    errors.append("could not read 4 ownership rows in ARCHITECTURE.md")
for doc in ("docs/TEAM_GUIDE.md", "docs/ONBOARDING.md", "CLAUDE.md", "AGENTS.md"):
    got = owned(doc)
    if got != ref:
        errors.append(f"ownership table in {doc} differs from ARCHITECTURE.md")

# CODEOWNERS must cover every owned path
co_norm = {c.lstrip("/").rstrip("/") for c in co}
for area, items in ref.items():
    for it in items:
        if it.rstrip("/") not in co_norm:
            errors.append(f"area {area} owns {it} but CODEOWNERS has no matching line")

print(f"checked {checked} paths")
for e in errors:
    print("MISMATCH:", e)
print("OK" if not errors else f"{len(errors)} mismatch(es)")
sys.exit(1 if errors else 0)
