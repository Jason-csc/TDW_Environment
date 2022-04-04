"""
Test /users/<user_url_slug/ URLs.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""

import re
from urllib.parse import urlparse

import bs4
import utils


def test_awdeorio(client):
    """Check default content at /users/awdeorio/ URL."""
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 302

    # Load and parse user page
    response = client.get("/users/awdeorio/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    srcs = [x.get("src") for x in soup.find_all('img')]
    links = [x.get("href") for x in soup.find_all("a")]
    buttons = [submit.get("name") for button in soup.find_all('form')
               for submit in button.find_all("input") if submit]

    # Verify links in header
    assert "/" in links
    assert "/explore/" in links
    assert "/users/awdeorio/" in links

    # Links specific to /users/awdeorio/followers/
    assert "/users/awdeorio/followers/" in links
    assert "/users/awdeorio/following/" in links
    assert "/posts/1/" in links
    assert "/posts/3/" in links
    assert "/users/jflinn/followers/" not in links
    assert "/users/jflinn/following/" not in links
    assert "/users/michjc/followers/" not in links
    assert "/users/michjc/following/" not in links
    assert "/users/jag/followers/" not in links
    assert "/users/jag/following/" not in links
    assert "/posts/2/" not in links
    assert "/posts/4/" not in links

    # Verify images: post 1,2,3,4
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" not in srcs
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" in srcs
    assert "/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg" not in srcs

    # Verify text
    assert "2 posts" in text
    assert "2 followers" in text.lower()
    assert "2 following" in text.lower()
    assert "Andrew DeOrio" in text
    assert "Edit profile" in text
    assert "not following" not in text.lower()
    assert "login" not in text
    assert text.count("awdeorio") == 2
    assert text.lower().count("following") == 1

    # Verify buttons
    assert "file" in buttons
    assert "create_post" in buttons
    assert "delete_post" not in buttons
    assert "delete" not in buttons
    assert "logout" in buttons


def test_upload(client):
    """Upload a new post verify that it shows up."""
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

    # Load and parse user page
    response = client.get("/users/awdeorio/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    srcs_before = [x.get("src") for x in soup.find_all('img')]

    # Upload a new post
    pic_path = utils.TEST_DIR/'testdata/fox.jpg'
    with pic_path.open("rb") as pic:
        response = client.post(
            "/posts/",
            data={"file": pic, "create_post": "upload new post", "operation":
                  "create"}
        )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/users/awdeorio/"

    # Load and parse user page
    response = client.get("/users/awdeorio/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    srcs_after = [x.get("src") for x in soup.find_all('img')]

    # Number of image sources after should be greater
    assert len(srcs_after) == len(srcs_before) + 1
