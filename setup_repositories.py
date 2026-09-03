#!/usr/bin/env python3
import subprocess
import shutil
import argparse
import sys
from pathlib import Path

REPOS_FILE = "repos.txt"
OVERVIEW_GENERATOR = Path("overview_files/gen_overview.py")

def run(cmd, cwd=None):
    """Run a shell command cross-platform and print output."""
    print(f"$ {' '.join(cmd)} (cwd={cwd})")
    result = subprocess.run(cmd, cwd=cwd, check=True)
    return result.returncode

def sync_repo(url, branch="main", ignore_merge_error=False):
    """Clone or pull the repo."""
    name = Path(url).stem
    repo_path = Path(name)
    if repo_path.exists() and (repo_path / ".git").exists():
        print(f"Updating {name}...")
        run(["git", "fetch", "origin"], cwd=name)
        run(["git", "checkout", branch], cwd=name)
        try:
            run(["git", "pull"], cwd=name)
        except subprocess.CalledProcessError:
            if ignore_merge_error:
                print(
                    f"Warning: merge conflict or pull error in {name}. Skipping this repo."
                )
                return
            raise
    else:
        print(f"Cloning {name}...")
        run(["git", "clone", "--branch", branch, url])


def run_overview_generator():
    """Regenerate overview HTML from CSV after sync."""
    if not OVERVIEW_GENERATOR.exists():
        print(f"Skipping overview generation: {OVERVIEW_GENERATOR} not found")
        return

    print(f"Running {OVERVIEW_GENERATOR}...")
    # Reuse the active interpreter (e.g. `uv run`) so project deps are available.
    run([sys.executable, str(OVERVIEW_GENERATOR)])

def main():
    parser = argparse.ArgumentParser(description="Sync git repositories from repos.txt")
    parser.add_argument(
        "--ignore-merge-error",
        action="store_true",
        help="Skip a repo if git pull results in a merge conflict or pull error.",
    )
    args = parser.parse_args()

    if shutil.which("git") is None:
        print("Git is not installed or not available in PATH. Please install Git and try again.")
        return

    if not Path(REPOS_FILE).exists():
        print(f"{REPOS_FILE} not found!")
        return

    with open(REPOS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            url = parts[0]
            branch = parts[1] if len(parts) > 1 else "main"
            sync_repo(url, branch, ignore_merge_error=args.ignore_merge_error)

    run_overview_generator()

if __name__ == "__main__":
    main()
