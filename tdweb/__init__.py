"""tdweb package initializer."""
import flask

app = flask.Flask(__name__)  # pylint: disable=invalid-name

app.config.from_object('tdweb.config')

app.config.from_envvar('tdweb_SETTINGS', silent=True)


metadata = dict()
metadata["start"] = False
metadata["prepared"] = False
'''
rendered images queue
'''
metadata["camera1"] = []
metadata["camera2"] = []

metadata["cmds1"] = []
metadata["cmds2"] = []

'''
obj info  "obj_id": {
                    "pos":
                    "name":
                    "owner":
                    "obj_id":
                    "reachable1":
                    "reachable2":
                }
'''
metadata["objList"] = {}

'''
bin positions  "bin_id": {
                    "name": 
                    "player": "player1" or "player2"
                    "bin_id":
                }
'''
metadata["placePos"] = {}


metadata["status1"] = ["PICK"]
metadata["status2"] = ["PICK"]



metadata["task"] = {"player1":[], "player2":[]}
metadata["shareInfo"] = []
metadata["turn"] = {"canPick": True, "canDrop": True, "canShare": True, "playerTurn":True}


import tdweb.views  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.model  # noqa: E402  pylint: disable=wrong-import-position
import tdweb.api # noqa: E402  pylint: disable=wrong-import-position
import tdweb.tdwHandler # noqa: E402  pylint: disable=wrong-import-position
