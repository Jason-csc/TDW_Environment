"""tdweb package initializer."""
import flask

app = flask.Flask(__name__)  # pylint: disable=invalid-name

app.config.from_object('tdweb.config')

app.config.from_envvar('tdweb_SETTINGS', silent=True)

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import tdweb.views  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.model  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.api # noqa: E402  pylint: disable=wrong-import-position