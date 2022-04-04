"""tdwENV package initializer."""
import flask

app = flask.Flask(__name__)  # pylint: disable=invalid-name

app.config.from_object('tdwENV.config')

app.config.from_envvar('tdwENV_SETTINGS', silent=True)

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import tdwENV.views  # noqa: E402  pylint: disable=wrong-import-position
import tdwENV.model  # noqa: E402  pylint: disable=wrong-import-position