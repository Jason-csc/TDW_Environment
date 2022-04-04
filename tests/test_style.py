"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import pathlib
import shutil
import collections
from urllib.parse import urlparse
import subprocess
import bs4
import utils

# CrawlURL is a named tuple that holds (url, source) where url
# is the url being crawled and source is the source page where
# we found the url.
CrawlURL = collections.namedtuple('CrawlURL', ['url', 'source'])


def test_pycodestyle():
    """Run pycodestyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run(["pycodestyle", "setup.py", "insta485"], check=True)


def test_pydocstyle():
    """Run pydocstyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run(["pydocstyle", "setup.py", "insta485"], check=True)


def test_pylint():
    """Run pylint."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    subprocess.run([
        "pylint",
        "--rcfile", utils.TEST_DIR/"testdata/pylintrc",
        "--disable=cyclic-import",
        "--disable=assigning-non-slot",
        "--unsafe-load-any-extension=y",
        "setup.py",
        "insta485",
    ], check=True)


def test_html(client):
    """Validate generated HTML5 in insta485/templates/ ."""
    # Log in as awdeorio
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Clean up
    if os.path.exists("tmp/localhost"):
        shutil.rmtree("tmp/localhost")

    # Render all pages and download HTML to ./tmp/localhost/
    crawl(
        client=client,
        outputdir="tmp/localhost",
        todo=collections.deque([CrawlURL(url='/', source='/')]),
        done=set(),
    )

    # Verify downloaded pages HTML5 compliances using html5validator
    print("html5validator --root tmp/localhost")
    subprocess.run([
        "html5validator",
        "--root", "tmp/localhost",
        "--ignore", "JAVA_TOOL_OPTIONS",
    ], check=True)


def assert_no_prohibited_terms(*terms):
    """Check for prohibited terms before testing style."""
    for term in terms:
        completed_process = subprocess.run(
            [
                "grep",
                "-r",
                "-n",
                term,
                "--include=*.py",
                "--include=*.jsx",
                "--include=*.js",
                "--exclude=__init__.py",
                "--exclude=setup.py",
                "--exclude=bundle.js",
                "--exclude=*node_modules/*",
                "insta485",
            ],
            check=False,  # We'll check the return code manually
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        # Grep exit code should be non-zero, indicating that the prohibited
        # term was not found.  If the exit code is zero, crash and print a
        # helpful error message with a filename and line number.
        assert completed_process.returncode != 0, (
            f"The term '{term}' is prohibited.\n{completed_process.stdout}"
        )


def crawl(client, outputdir, todo, done):
    """Recursively render every page provided by 'client', saving to file."""
    if not todo:
        return
    # Pop a URL off the head of the queue and parse it
    url_pair = todo.popleft()
    hostname = urlparse(url_pair.url).hostname
    path = urlparse(url_pair.url).path

    # Ignore links outside localhost
    if hostname and hostname not in ["localhost", "127.0.01"]:
        done.add(path)
        crawl(client, outputdir, todo, done)
        return

    # Ignore links already visited
    if path in done:
        done.add(path)
        crawl(client, outputdir, todo, done)
        return

    # Ignore logout route
    if "logout" in path:
        done.add(path)
        crawl(client, outputdir, todo, done)
        return

    # Download
    print("GET", path, "FROM", url_pair.source)
    response = client.get(path)

    # redirect routes should return 302 status
    redirect_routes = ["/accounts/create/"]
    if path in redirect_routes:
        assert response.status_code == 302
    else:
        assert response.status_code == 200

    # Save
    assert path.endswith("/"),\
        f"Error: path does not end in slash: '{path}'"
    outputdir = pathlib.Path(outputdir)
    dirname = outputdir/"localhost"/path.lstrip("/")
    dirname.mkdir(parents=True, exist_ok=True)
    filename = dirname/"index.html"
    html = response.data.decode(response.charset)
    filename.write_text(html)

    # Update visited list
    done.add(path)

    # Extract links and add to todo list
    soup = bs4.BeautifulSoup(html, "html.parser")
    for link_elt in soup.find_all("a"):
        link = link_elt.get("href")
        if link in done:
            continue
        todo.append(CrawlURL(url=link, source=path))

    # Recurse
    crawl(client, outputdir, todo, done)
