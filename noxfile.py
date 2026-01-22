import argparse
import os
from pathlib import Path
from typing import Tuple

import nox

nox.options.sessions = ["lint", "test"]  # Sessions other than 'dev'

REQUIREMENTS = {
    "tests": "tests/requirements.txt",
    "tools": "tools/requirements.txt",
}

PYTHONPATH = f"{Path(__file__).parent}/src:{Path(__file__).parent}/tests:{Path(__file__).parent}/tools"


@nox.session
def lint(session):
    session.env['PYTHONPATH'] = PYTHONPATH
    session.install("flake8")
    session.run("flake8", "src", "tests", "noxfile.py")


@nox.session
def test(session: nox.Session):
    # Install test dependencies
    session.install("-r", REQUIREMENTS["tests"])

    # Parallelize tests as much as possible, by default.
    session.env['PYTHONPATH'] = PYTHONPATH
    print(session.env['PYTHONPATH'])
    session.run("pytest", "./tests/unit/local", env={"LC_CTYPE": "en_US.UTF-8"})


VENV_DIR = Path('./.venv').resolve()


@nox.session
def dev(session: nox.Session) -> None:
    """
    Sets up a python development environment for the project.

    This session will:
    - Create a python virtualenv for the session
    - Install the `virtualenv` cli tool into this environment
    - Use `virtualenv` to create a global project virtual environment
    - Invoke the python interpreter from the global project environment to install
      the project and all it's development dependencies.
    """

    session.install("virtualenv")
    # the VENV_DIR constant is explained above
    session.run("virtualenv", os.fsdecode(VENV_DIR), silent=True)

    python = os.fsdecode(VENV_DIR.joinpath("bin/python"))

    # Use the venv's interpreter to install the project along with
    # all it's dev dependencies, this ensures it's installed in the right way
    session.run(python, "-m", "pip", "install", "-r", REQUIREMENTS["tests"], external=True)
    session.run(python, "-m", "pip", "install", "-r", REQUIREMENTS["tools"], external=True)


def check_changelog_version(new_version: str) -> bool:
    """Returns True if the new version is in the changelog, False otherwise."""
    changelog = Path("CHANGELOG").read_text(encoding="utf-8")
    first_line = changelog.splitlines()[0]
    return new_version in first_line


def _get_version(session: nox.Session, part: str = "build") -> Tuple[str, str]:
    """Returns the current version and the next version."""
    version_info = session.run("bump2version", "--dry-run", "--list", part,
                               silent=True, env={"LC_CTYPE": "en_US.UTF-8"})
    current_version = [line for line in version_info.splitlines()
                       if "current_version" in line][0].split("=")[1]
    new_version = [line for line in version_info.splitlines()
                   if "new_version" in line][0].split("=")[1]
    return current_version, new_version


@nox.session
def release(session: nox.Session) -> None:
    """
    Kicks off an automated release process by creating and pushing a new tag.

    Invokes bump2version with the posarg setting the version.

    Usage:
    $ nox -s release -- [major|minor|patch]
    """
    session.env['PYTHONPATH'] = PYTHONPATH
    session.install("-r", REQUIREMENTS["tools"])
    parser = argparse.ArgumentParser(description="Release a semver version.")
    parser.add_argument(
        "version",
        type=str,
        nargs=1,
        help="The type of semver release to make.",
        choices={"major", "minor", "patch", "build"},
    )
    args: argparse.Namespace = parser.parse_args(args=session.posargs)
    version: str = args.version.pop()

    current_version, new_version = _get_version(session, version)

    # If we get here, we should be good to go
    # Let's do a final check for safety
    confirm = input(
        f"You are about to bump from v{current_version} to v{new_version}. "
        "This will create a new tag and push it to the remote. Continue? [y/N] "
    )

    # Abort on anything other than 'y'
    if confirm.lower().strip() != "y":
        session.error(f"You said no when prompted to bump the {version!r} version.")

    if not check_changelog_version(new_version):
        session.error(
            f"Could not find {new_version} in CHANGELOG. "
            "Please make sure the latest version is at the top of the changelog.")

    session.log(f"Bumping the {version!r} version")
    session.run("bump2version", version)

    session.log("Pushing the new tag")
    session.run("git", "push", external=True)
    session.run("git", "push", "--tags", external=True)
    session.log("Done!")
    session.log("A new release should be available on GitHub and the rpm repo shortly.")


@nox.session
def publish(session: nox.Session) -> None:
    """
    Generate and publishes the spec file to the rpm repo.
    """
    session.env['PYTHONPATH'] = PYTHONPATH
    session.install("-r", REQUIREMENTS["tools"])

    # Get the current version
    current_version, _ = _get_version(session)

    changelog_file = Path("CHANGELOG").resolve()
    spec_file = Path("tobi.spec").resolve()

    session.log(f"Generating the spec file for v{current_version}")

    session.run("python", "tools/release/generate_spec.py", current_version, os.fsdecode(changelog_file), "False")

    session.log(f"Publishing the spec file for v{current_version}")
    session.run("python", "tools/release/publish_spec.py", current_version, os.fsdecode(spec_file))
