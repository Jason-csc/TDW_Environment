"""
Check index page at / URL.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
import bs4


def test_images(client):
    """Verify all images are present in / URL.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse index page
    response = client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Verify images present of Flinn, DeOrio, postid 1, postid 2, postid 3
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" in srcs
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" in srcs


def test_links(client):
    """Verify expected links present in / URL.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse index page
    response = client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]

    # Verify links are present
    assert "/" in links
    assert "/users/awdeorio/" in links
    assert "/users/jflinn/" in links
    assert "/users/michjc/" in links
    assert "/posts/1/" in links
    assert "/posts/2/" in links
    assert "/posts/3/" in links

    # Verify links are not present
    assert "/users/jag/" not in links
    assert "/posts/4/" not in links


def test_likes(client):
    """Verify expected "likes" are present in / URL.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse index page
    response = client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Add a space to the end.  This will ensure that we catch a string that's
    # not supposed to be there even it's at the end of the string, e.g,
    # '2 like'.
    text += " "

    # Verify expected content is in text on generated HTML page
    assert "1 like" in text
    assert "2 likes" in text
    assert "3 likes" in text

    # Verify unexpected content is not in text on generated HTML page
    assert "1 likes" not in text
    assert "2 like " not in text
    assert "3 like " not in text
    assert "4 likes" not in text
    assert "0 likes" not in text


def test_timestamps(client):
    """Verify expected timestamps are present in / URL.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse index page
    response = client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content: once for each post
    assert text.lower().count("just now") == 3


def test_comments(client):
    """Verify expected comments are present in / URL.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse index page
    response = client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert "awdeorio #chickensofinstagram" in text
    assert "jflinn I <3 chickens" in text
    assert "michjc Cute overload!" in text
    assert "awdeorio Sick #crossword" in text
    assert "jflinn Walking the plank #chickensofinstagram" in text
    assert "awdeorio This was after trying to teach them to do a #crossword" \
        in text
    assert "Saw this on the diag yesterday!" not in text
