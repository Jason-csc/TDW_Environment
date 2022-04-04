"""
Test student-created utility scripts.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import subprocess
import sqlite3
import threading
import pathlib
import time
import socket
import pytest

# Set default timeout and long timeout for tests
#
# We'll need longer wait times on slow machines like the autograder.
if pathlib.Path("/home/autograder/working_dir").exists():
    TIMEOUT = 30
else:
    TIMEOUT = 10

PORT_NUM = 8000

# This pylint warning is endemic to pytest.
# pylint: disable=unused-argument


@pytest.fixture(name="setup_teardown")
def setup_teardown_fixture():
    """Set up the test and cleanup after."""
    # Setup: make sure no stale processes are running
    assert not pgrep("flask"), \
        "Found running flask process.  Try 'pkill -f flask'"

    # Transfer control to testcase
    yield None

    # Teardown: kill any stale processes
    pkill("flask")
    assert wait_for_stop()


def test_insta485db_destroy():
    """Verify insta485db destroy removes DB file."""
    assert_is_shell_script("bin/insta485db")
    subprocess.run(["bin/insta485db", "destroy"], check=True)
    assert not os.path.exists("var/insta485.sqlite3")
    assert not os.path.exists("var/uploads")


def test_insta485db_create():
    """Verify insta485db create populates DB with default data."""
    assert_is_shell_script("bin/insta485db")

    # Destroy, then create database
    subprocess.run(["bin/insta485db", "destroy"], check=True)
    subprocess.run(["bin/insta485db", "create"], check=True)

    # Verify files were created
    assert os.path.exists("var/insta485.sqlite3")
    assert os.path.exists(
        "var/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg")
    assert os.path.exists(
        "var/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg")
    assert os.path.exists(
        "var/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg")
    assert os.path.exists(
        "var/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg")
    assert os.path.exists(
        "var/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg")
    assert os.path.exists(
        "var/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg")
    assert os.path.exists(
        "var/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg")
    assert os.path.exists(
        "var/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg")

    # Connect to the database
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")

    # There should be 4 rows in the 'users' table
    cur = connection.execute("SELECT count(*) FROM users")
    num_rows = cur.fetchone()[0]
    assert num_rows == 4


def test_insta485db_reset():
    """Verify insta485db reset does a destroy and a create."""
    # Create a "stale" database file
    dbfile = pathlib.Path("var/insta485.sqlite3")
    dbfile.write_text("this should be overwritten")

    # Reset the database
    subprocess.run(["bin/insta485db", "reset"], check=True)

    # Verify database file was overwritten.  Note that we have to open the file
    # in binary mode because sqlite3 format is not plain text.
    content = dbfile.read_bytes()
    assert b"this should be overwritten" not in content


def test_insta485db_dump():
    """Spot check insta485db dump for a few data points."""
    assert_is_shell_script("bin/insta485db")
    subprocess.run(["bin/insta485db", "reset"], check=True)
    output = subprocess.run(
        ["bin/insta485db", "dump"],
        check=True, stdout=subprocess.PIPE, universal_newlines=True,
    ).stdout
    assert "awdeorio" in output
    assert "73ab33bd357c3fd42292487b825880958c595655.jpg" in output
    assert "Walking the plank" in output


def test_insta485run(setup_teardown, client):
    """Verify insta485run script behavior."""
    assert not port_in_use(PORT_NUM), \
        f'Found running process on port {PORT_NUM}.'

    # Destroy database
    subprocess.run(["bin/insta485db", "destroy"], check=True)

    # Execute student run script in a concurrent thread.  Don't check the
    # return code because test cleanup will kill the process
    assert_is_shell_script("bin/insta485run")
    thread = threading.Thread(
        target=subprocess.run,
        args=(["bin/insta485run"],),
        kwargs={"check": False},
    )
    thread.start()

    # Wait for server to start
    assert wait_for_start()

    # Verify that database is now created
    assert os.path.exists("var/insta485.sqlite3")

    # Verify that server correctly serves content
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    response = client.get("/")
    assert response.status_code == 200


def test_insta485test():
    """Verify insta485test script contains correct commands."""
    assert_is_shell_script("bin/insta485test")
    lines = pathlib.Path("bin/insta485test")\
        .read_text(encoding='utf-8').splitlines()
    assert any(line.startswith("pycodestyle") for line in lines)
    assert any(line.startswith("pydocstyle") for line in lines)
    assert any(line.startswith("pylint") for line in lines)
    assert any(line.startswith("pytest") for line in lines)


def assert_is_shell_script(path):
    """Assert path is an executable shell script."""
    assert os.path.isfile(path)
    output = subprocess.run(
        ["file", path],
        check=True, stdout=subprocess.PIPE, universal_newlines=True,
    ).stdout
    assert "shell script" in output
    assert "executable" in output


def pgrep(pattern):
    """Return True if process matching pattern is running."""
    completed_process = subprocess.run(
        ["pgrep", "-f", pattern],
        check=False,  # We'll check the return code manually
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    return completed_process.returncode == 0


def pkill(pattern):
    """Issue a "pkill -f pattern" command, ignoring the exit code."""
    subprocess.run(["pkill", "-f", pattern], check=False)


def wait_for_start():
    """Wait for Flask process to start running."""
    for _ in range(TIMEOUT):
        if pgrep("flask"):
            return True
        time.sleep(1)
    return False


def wait_for_stop():
    """Wait for Flask process to stop running."""
    for _ in range(TIMEOUT):
        if not pgrep("flask"):
            return True
        time.sleep(1)
    return False


def port_in_use(port):
    """Check if port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0
