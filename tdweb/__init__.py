"""tdweb package initializer."""
import flask

app = flask.Flask(__name__)  # pylint: disable=invalid-name

app.config.from_object('tdweb.config')

app.config.from_envvar('tdweb_SETTINGS', silent=True)


metadata = dict()
metadata["start"] = False
metadata["prepared"] = False
metadata["camera1"] = []
metadata["camera2"] = []
metadata["cmds1"] = []
metadata["cmds2"] = []
metadata["objList"] = {}
metadata["placePos1"] = []
metadata["placePos2"] = []
metadata["status1"] = ["PICK"]
metadata["status2"] = ["PICK"]



import tdweb.views  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.model  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.api # noqa: E402  pylint: disable=wrong-import-position
import tdweb.tdwHandler # noqa: E402  pylint: disable=wrong-import-position
