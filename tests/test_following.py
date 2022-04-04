"""
Test /users/<user_url_slug/following/ URLs.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
from urllib.parse import urlparse, urlencode


import bs4


def test_awdeorio(client):
    """Check default content at /users/awdeorio/following/ URL."""
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

    # Load and parse following page
    response = client.get("/users/awdeorio/following/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Verify text
    assert text.lower().count("following") == 3
    assert "not following" not in text.lower()

    # Verify images: Mike, Jason, Jag
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs

    # Verify links
    assert "/users/jflinn/" in links
    assert "/users/michjc/" in links
    assert "/users/jag/" not in links


def test_unfollow(client):
    """Click unfollow.  Verify user is removed."""
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

    query_string = urlencode({
            "target": "/users/awdeorio/following/"
        })
    response = client.post(
        f"/following/?{query_string}",
        data={"operation": "unfollow", "username": "jflinn"}
    )
    assert response.status_code == 302

    response = client.get("/users/awdeorio/following/")

    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]

    # Verify text
    assert "not following" not in text.lower()
    assert text.lower().count("following") == 2

    # Verify images: Mike, Jason, Jag
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs

    # Verify links
    assert "/users/michjc/" in links
    assert "/users/jflinn/" not in links
    assert "/users/jag/" not in links


def test_not_following(client):
    """User can like/comment on posts by people they are not following."""
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

    # Awdeorio is not following jag. Add a like to jag's post
    query_string = urlencode({"target": "/posts/4/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "4", "operation": "like"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/posts/4/"

    # Comment on jag's post
    response = client.post(
        "/comments/",
        data={"postid": "4", "text": "Success!", "operation": "create"}
    )
    assert response.status_code == 302

    # Verify the like and comment show up on post 4
    response = client.get("/posts/4/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    assert "1 like" in text
    assert "Success!" in text
