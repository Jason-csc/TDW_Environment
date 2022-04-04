"""
Test log in and log out.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
from urllib.parse import urlparse
import bs4


def test_index_redirect(client):
    """GET / redirects to /accounts/login/ when user is not logged in.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    response = client.get("/")
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/login/"


def test_login_page_content(client):
    """Verify links and form on /accounts/login/ page.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]
    links = [urlparse(x).path for x in links]  # just the path part of URL
    form_inputs = [submit.get("name") for button in soup.find_all('form')
                   for submit in button.find_all("input") if submit]
    assert "/accounts/create/" in links
    assert "username" in form_inputs
    assert "password" in form_inputs


def test_login(client):
    """Login awdeorio.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/"


def test_logout(client):
    """Logout after log in.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Login
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/"

    # Should be able to load the index page
    response = client.get("/")
    assert response.status_code == 200

    # Log out
    response = client.post("/accounts/logout/")
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/login/"

    # Index should redirect to login
    response = client.get("/")
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/login/"
