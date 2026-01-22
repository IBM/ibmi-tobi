"""This script generates the spec file by replacing ${version} and ${changelog}
in the template file."""
import pathlib
import re
import sys
import textwrap

here = pathlib.Path(__file__).parent
template_file = here / "tobi.spec.template"


def replace_version(template: str, version: str) -> str:
    """Replace ${version} with the given version string in the given template string.

    Args:
        template (str): The template string.
        version (str): The version string to replace ${version} with.

    Returns:
        str: The modified template string.
    """
    return re.sub(r"\${VERSION}", version, template)


def replace_changelog(template: str,
                      changelog_file: pathlib.Path) -> str:
    """Replace ${changelog} with the contents of the given
     changelog file in the given template string.

    Args:
        template (str): The template string.
        changelog_file (pathlib.Path): The path to the changelog file.

    Returns:
        str: The modified template string.
    """
    changelog = changelog_file.read_text()

    lines = changelog.split("\n")
    formatted_lines = []
    for line in lines:
        chunks = textwrap.wrap(line, width=80, subsequent_indent=" " * 2)
        formatted_lines.extend(chunks)
    changelog = "\n".join(formatted_lines)

    return re.sub(r"\${CHANGELOG}", changelog, template)


def generate_spec(version: str, changelog_file: pathlib.Path, fetch_source: bool) -> str:
    """Generate the spec file by replacing ${VERSION} and ${CHANGELOG} in the given template string.

    Args:
        template (str): The template string.
        version (str): The version string to replace ${VERSION} with.
        changelog_file (pathlib.Path): The path to the changelog file to replace ${CHANGELOG} with.

    Returns:
        str: The modified spec file.
    """
    if fetch_source:
        template = "%undefine _disable_source_fetch\n"
    else:
        template = ""
    template = template + template_file.read_text()
    template = replace_version(template, version)
    template = replace_changelog(template, changelog_file)
    return template


def main():
    """Generate the spec file by replacing ${VERSION} and ${CHANGELOG} in the template file."""
    if len(sys.argv) != 4:
        print("Usage: generate_spec.py VERSION CHANGELOG_FILE FETCH_SOURCE")
        sys.exit(1)
    version = sys.argv[1]
    changelog_file = pathlib.Path(sys.argv[2])
    fetch_source = sys.argv[3] == "True"


    if not changelog_file.exists():
        print(f"Changelog file {changelog_file} does not exist")
        sys.exit(1)

    spec = generate_spec(version, changelog_file, fetch_source)
    with open("tobi.spec", "w", encoding="utf-8") as out_file:
        out_file.write(spec)


if __name__ == "__main__":
    main()
