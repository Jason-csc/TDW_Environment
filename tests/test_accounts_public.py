"""
Test /users/accounts/ URLs.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import uuid
import sqlite3
from urllib.parse import urlparse, urlencode
import utils


def test_accounts_create(client):
    """Create an account and verify that we've got a new empty user.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Connect to the database
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")

    # Number of posts and users before adding a user
    cur = connection.execute("SELECT COUNT(*) from users")
    num_users_before = cur.fetchone()[0]
    cur = connection.execute("SELECT COUNT(*) from posts")
    num_posts_before = cur.fetchone()[0]

    # Add a user
    avatar_path = utils.TEST_DIR/"testdata/fox.jpg"
    with avatar_path.open('rb') as avatar:
        query_string = urlencode({"target": "/"})
        response = client.post(
            f"/accounts/?{query_string}",
            data={
                "username": "fakeuser", "fullname": "Fake User",
                "email": "fakeuser@umich.edu",
                "password": "password",
                "file": avatar,
                "operation": "create"
            }
        )

    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/"

    # HACK: Work around to ensure database commit.  The post request above
    # modifies the database.  The modification won't be written until the
    # sqlite3 commit() function is called.  The commit() function is called by
    # model.py::close_db().  The close_db() function runs automatically at the
    # end of a request.  For testing, we temporarily keep the last request
    # open.  This allows us to do things like inspecting the request object.
    # However, in this test, the temporarily open request prevents the database
    # from being written out.
    #
    # The work around is to make a dummy request, which causes the previous
    # request to close and commit() is called automatically.
    #
    # Flask docs:
    # https://flask.palletsprojects.com/en/1.1.x/reqcontext/#teardown-callbacks
    response = client.get("/")
    assert response.status_code == 200

    # Number of posts and users after adding a user
    cur = connection.execute("SELECT COUNT(*) from users")
    num_users_after = cur.fetchone()[0]
    cur = connection.execute("SELECT COUNT(*) from posts")
    num_posts_after = cur.fetchone()[0]

    # Number of posts should be the same, number of users bigger
    assert num_posts_after == num_posts_before
    assert num_users_after == num_users_before + 1


def test_accounts_edit(client, mocker):
    """Change name, email and photo.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html

    Note: 'mocker' is a fixture function provided the the pytest-mock package.
    This fixture lets us override a library function with a temporary fake
    function that returns a hardcoded value while testing.
    """
    # Fake the uuid4() function to return a hardcoded UUID.  We need a
    # predictable value for testing, not a randomly generated value.
    mocker.patch(
        "uuid.uuid4",
        return_value=uuid.UUID("00000000000000000000000000000000"),
    )

    # Log in
    response = client.post(
        "/accounts/",
        data={"username": "awdeorio",
              "password": "password",
              "operation": "login"},
    )
    assert response.status_code == 302

    # Change name, email and photo
    avatar_path = utils.TEST_DIR/"testdata/fox.jpg"
    with avatar_path.open('rb') as avatar:
        query_string = urlencode({"target": "/accounts/edit/"})
        response = client.post(
            f"/accounts/?{query_string}",
            data={
                "fullname": "New Name",
                "email": "newemail@umich.edu",
                "file": avatar,
                "update": "submit",
                "operation": "edit_account"
            },
        )

    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/edit/"

    # HACK: Work around to ensure database commit.  The post request above
    # modifies the database.  The modification won't be written until the
    # sqlite3 commit() function is called.  The commit() function is called by
    # model.py::close_db().  The close_db() function runs automatically at the
    # end of a request.  For testing, we temporarily keep the last request
    # open.  This allows us to do things like inspecting the request object.
    # However, in this test, the temporarily open request prevents the database
    # from being written out.
    #
    # The work around is to make a dummy request, which causes the previous
    # request to close and commit() is called automatically.
    #
    # Flask docs:
    # https://flask.palletsprojects.com/en/1.1.x/reqcontext/#teardown-callbacks
    response = client.get("/")
    assert response.status_code == 200

    # Look up new users in the database
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    cur = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username='awdeorio'"
    )
    users = cur.fetchall()

    # Verify new database entry
    assert users == [(
        "awdeorio",
        "New Name",
        "newemail@umich.edu",
        "00000000000000000000000000000000.jpg",
    )]


def test_accounts_password(client):
    """Change password.  Logout and login again.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    response = client.post(
        "/accounts/",
        data={"username": "awdeorio",
              "password": "password",
              "operation": "login"},
    )
    assert response.status_code == 302

    # Change password
    query_string = urlencode({"target": "/accounts/edit/"})
    response = client.post(
        f"/accounts/?{query_string}",
        data={
            "password": "password",
            "new_password1": "newpassword",
            "new_password2": "newpassword",
            "update_password": "submit",
            "operation": "update_password"
        }
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/edit/"

    # Log out
    response = client.post("/accounts/logout/")
    assert response.status_code == 302

    # Log in with old password password fails
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 403

    # Log in with new password works
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "newpassword",
            "operation": "login"
        },
    )
    assert response.status_code == 302


def test_accounts_delete(client):
    """Delete account and verify that everything is gone.

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

    # Delete account
    query_string = urlencode({"target": "/accounts/create/"})
    response = client.post(
        f"/accounts/?{query_string}",
        data={
            "delete": "confirm delete account",
            "operation": "delete"
        }
    )
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/create/"

    # User can no longer access post 1, should be redirected to login
    response = client.get("/posts/1/")
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/login/"

    # User can no longer access post 3, should be redirected to login
    response = client.get("/posts/3/")
    assert response.status_code == 302
    urlpath = urlparse(response.location).path
    assert urlpath == "/accounts/login/"

    # Log in should fail
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "password",
            "operation": "login"
        },
    )
    assert response.status_code == 403

    # User pages should be gone
    response = client.get("/users/awdeorio/")
    assert response.status_code == 302
    response = client.get("/users/awdeorio/following/")
    assert response.status_code == 302
    response = client.get("/users/awdeorio/followers/")
    assert response.status_code == 302

    # Log in as user jag
    response = client.post(
        "/accounts/",
        data={
            "username": "jag",
            "password": "password",
            "operation": "login"
        },
    )
    # Verify awdeorio's images were deleted
    response = client.get(
        "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    )
    assert response.status_code == 404
    response = client.get(
        "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
    )
    assert response.status_code == 404


def test_accounts_uploads_permission(client):
    """Verify that only authenticated users can see uploads.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    response = client.get(
        "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    )
    assert response.status_code == 403
    response = client.get(
        "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
    )
    assert response.status_code == 403

    # Log in as user jag
    response = client.post(
        "/accounts/",
        data={
            "username": "jag",
            "password": "password",
            "operation": "login"
        },
    )

    # Images are visible now
    response = client.get(
        "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
    )
    assert response.status_code == 200
    response = client.get(
        "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
    )
    assert response.status_code == 200
