"""REST API for posts."""
import flask
import tdweb
from tdweb import metadata as metadata


class InvalidUsage(Exception):
    """Solve invalid case."""
    def __init__(self, message, status_code):
        """Solve initialize."""
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """Solve to dict method."""
        msg = {}
        msg['message'] = self.message
        msg['status_code'] = self.status_code
        return msg


@tdweb.app.route('/api/v1/chats/', methods=['GET','POST'])
def get_chats():
    if flask.request.method == 'POST':
        owner = flask.request.json.get("owner")
        if owner is None or len(owner) == 0:
            raise InvalidUsage('Bad Request', status_code=400)

        text = flask.request.json.get("text")
        if text is None or len(owner) == 0:
            raise InvalidUsage('Bad Request', status_code=400)

        connection = tdweb.model.get_db()
        connection.execute(
            'INSERT INTO chats(owner, text) VALUES (?,?);',
            (owner,text)
        )
        # print(f"insert {owner} {text}")
    
    connection = tdweb.model.get_db()
    cur1 = connection.execute(
        "SELECT *" +
        "FROM chats C " +
        "ORDER BY C.chatid DESC;"
    ).fetchall()
    chats = []
    for res in cur1:
        chats.append({"chatid":res["chatid"],"owner":res["owner"],"text":res["text"],"created":res["created"]})
    context = {"chats":chats, "num":len(chats)}
    # print(context)
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/objlist/', methods=['GET'])
def get_obj():    
    context = {"obj":[]}
    player = flask.request.args.get("player")
    for objectid,res in metadata["objList"].items():
        tmp = {}
        tmp["objectId"] = objectid
        tmp["objectName"] = res["name"]
        tmp["x"] = res["position"][0]
        tmp["y"] = res["position"][1]
        tmp["z"] = res["position"][2]
        if player == "player1":
            tmp["reachable"] = res["reachable1"]
            context["obj"].append(tmp)
        elif player == "player2":
            tmp["reachable"] = res["reachable2"]
            context["obj"].append(tmp)
        else:
            raise RuntimeError("Error: wrong playerid")
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/poslist/', methods=['GET'])
def get_pos():    
    context = {"positions":[]}
    player = flask.request.args.get("player")
    if player == "player1":
        for tmp in metadata["placePos1"]:
            context["pos"].append(tmp)
    elif player == "player2":
        for tmp in metadata["placePos2"]:
            context["pos"].append(tmp)
    else:
        raise RuntimeError("Error: wrong playerid")
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/sendcmd/',methods=['POST'])
def send_control():
    args = flask.request.form.get('args')
    player = flask.request.form.get('player')
    cmd = flask.request.form.get('cmd')
    if cmd is None or args is None or player is None:
        flask.abort(404)
    command = {"type": cmd, "args": args}
    if player == "player1":
        metadata["cmds1"].append(command)
        # metadata["cmds1"].append({"type": "drop", "args": {"x": -0.3, "y": 0.85, "z": -1}})
    elif player == "player2":
        metadata["cmds2"].append(command)
    else:
        flask.abort(404)
    return flask.redirect(flask.url_for(f"show_{player}"))