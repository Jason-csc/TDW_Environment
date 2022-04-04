"""
Test /posts/<postid_url_slug/ URLs.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import re
from urllib.parse import urlparse, urlencode

import bs4
import insta485


def test_postid_1(client):
    """Check default content at /posts/1/ URL."""
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

    # Load and parse /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    buttons = [submit.get("name") for button in soup.find_all('form')
               for submit in button.find_all("input") if submit]

    # Verify links in header are present
    assert "/" in links
    assert "/explore/" in links
    assert "/users/awdeorio/" in links

    # Verify no unexpected links to users are present
    assert "/users/michjc/" not in links
    assert "/users/jag/" not in links

    # Verify images present of Drew, postid 1
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" in srcs
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" in srcs

    # Verify that none of the other user images are present
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" not in srcs
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" not in srcs

    # Verify that none of the other post's images are present
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" not in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" not in srcs
    assert "/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg" not in srcs

    # Verify expected content is in text on generated HTML page
    assert text.count("awdeorio") == 3
    assert "3 likes" in text
    assert "Walking the plank #chickensofinstagram" in text
    assert "This was after trying to teach them to do a #crossword" in text
    assert "jflinn" in text

    # Verify unexpected content is not in text on generated HTML page
    assert "michjc" not in text
    assert "jag" not in text
    assert "I <3 chickens" not in text
    assert "Cute overload!" not in text
    assert "Sick #crossword" not in text
    assert "Saw this on the diag yesterday!" not in text

    # Verify expected buttons (based on their name) are present in the page
    assert "commentid" in buttons
    assert "uncomment" in buttons
    assert "postid" in buttons
    assert "unlike" in buttons
    assert "text" in buttons
    assert "comment" in buttons
    assert "delete" in buttons

    # Verify unexpected buttons are not present in the page
    assert "like" not in buttons
    assert "follow" not in buttons
    assert "unfollow" not in buttons


def test_postid_2(client):
    """Check default content at /posts/2/ URL."""
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

    # Load and parse /posts/2/ page
    response = client.get("/posts/2/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    links = [x.get("href") for x in soup.find_all("a")]
    srcs = [x.get("src") for x in soup.find_all('img')]
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    buttons = []
    for button in soup.find_all('form'):
        for submit in button.find_all("input"):
            if submit:
                buttons.append(submit.get("name"))

    # Verify links in header are present
    assert "/" in links
    assert "/explore/" in links
    assert "/users/awdeorio/" in links

    # Verify expected links to users are present
    assert "/users/jflinn/" in links

    # Verify no unexpected links to users are present
    assert "/users/michjc/" not in links
    assert "/users/jag/" not in links

    # Verify images present of Jason, postid 2
    assert "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg" in srcs
    assert "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg" in srcs

    # Verify that none of the other user images are present
    assert "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg" not in srcs
    assert "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg" not in srcs
    assert "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg" not in srcs

    # Verify that none of the other post's images are present
    assert "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg" not in srcs
    assert "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg" not in srcs
    assert "/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg" not in srcs

    # Verify expected content is in text on generated HTML page
    assert text.count("awdeorio") == 2
    assert "2 likes" in text
    assert "jflinn" in text
    assert "Sick #crossword" in text

    # Verify unexpected content is not in text on generated HTML page
    assert "michjc" not in text
    assert "jag" not in text
    assert "Walking the plank #chickensofinstagram" not in text
    assert "This was after trying to teach them to do a #crossword" not in text
    assert "I <3 chickens" not in text
    assert "Cute overload!" not in text
    assert "Saw this on the diag yesterday!" not in text

    # Verify expected buttons (based on their name) are present in the page
    assert "commentid" in buttons
    assert "uncomment" in buttons
    assert "postid" in buttons
    assert "unlike" in buttons
    assert "text" in buttons
    assert "comment" in buttons

    # Verify unexpected buttons are not present in the page
    assert "delete" not in buttons
    assert "like" not in buttons
    assert "follow" not in buttons
    assert "unfollow" not in buttons


def test_zero_likes_english(client):
    """Check zero likes english at /posts/4/ URL."""
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

    # Load and parse /posts/4/ page
    response = client.get("/posts/4/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Check for proper plural text
    assert "0 likes" in text
    assert "0 like " not in text


def test_delete_comment(client):
    """Delete comment and verify that it dissapears here and at index."""
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

    # Load /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200

    # Delete comment made by awdeorio
    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/comments/?{query_string}",
        data={"commentid": "6", "operation": "delete"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/posts/1/"


def test_like_unlike(client):
    """Like and dislike post."""
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

    response = client.get("/posts/1/")
    assert response.status_code == 200

    # Unlike and like the post
    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "unlike"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/posts/1/"

    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "like"}
    )
    assert response.status_code == 302


def test_duplicate_like_unlike(client):
    """Like and dislike post multiple times."""
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

    response = client.get("/posts/1/")
    assert response.status_code == 200

    # Try to like and unlike the post twice
    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "like"}
    )
    assert response.status_code == 409

    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "unlike"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/posts/1/"

    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "unlike"}
    )
    assert response.status_code == 409

    query_string = urlencode({"target": "/posts/1/"})
    response = client.post(
        f"/likes/?{query_string}",
        data={"postid": "1", "operation": "like"}
    )
    assert response.status_code == 302


def test_comment(client):
    """Comment on a post.  Make sure comments are present."""
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

    # Add a comment to postid 1
    response = client.post(
        "/comments/",
        data={"postid": "1", "text": "Test comment", "operation": "create"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/"

    # Load and parse /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify previous comments and new comment is in text
    assert "3 likes" in text
    assert "Walking the plank #chickensofinstagram" in text
    assert "jflinn" in text
    assert "This was after trying to teach them to do a #crossword" in text
    assert "awdeorio" in text
    assert "Test comment" in text

    # Verify no unexpected cpmment is in text
    assert "michjc" not in text
    assert "jag" not in text
    assert "I <3 chickens" not in text
    assert "Cute overload!" not in text
    assert "Sick #crossword" not in text
    assert "Saw this on the diag yesterday!" not in text


def test_delete_post(client):
    """Delete post.  Make sure comments are gone and photo deleted."""
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

    # Delete the post owned by awdeorio and redirect to user page
    response = client.post(
        "/posts/",
        data={"postid": "1", "operation": "delete"}
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/users/awdeorio/"

    # Verify postid=1 is not in database
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT * from posts WHERE postid=1")
    results = cur.fetchall()
    assert not results

    # Verify comments on postid=1 are not in database
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT * from comments WHERE postid=1")
    results = cur.fetchall()
    assert not results

    # Verify likes on postid=1 are not in database
    cur = connection.execute("SELECT * from likes WHERE postid=1")
    results = cur.fetchall()
    assert not results

    # Verify image is deleted
    response = client.get(
        "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    )
    assert response.status_code == 404
    assert not os.path.exists(
        "var/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
    )
