"""REST API for posts."""
import flask
import tdweb
from tdweb import metadata as metadata
import random


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


def db_get_chats():
    connection = tdweb.model.get_db()
    cur1 = connection.execute(
        "SELECT *" +
        "FROM chats C " +
        "ORDER BY C.chatid DESC;"
    ).fetchall()
    chats = []
    for res in cur1:
        chats.append({"chatid":res["chatid"],"owner":res["owner"],"text":res["text"],"created":res["created"]})
    return {"chats":chats, "num":len(chats)}



@tdweb.app.route('/api/v1/chats/', methods=['GET'])
def get_chats_pos():
    # get chats from database
    context = db_get_chats()
    
    player = flask.request.args.get("player")
    # get positions & status
    if player is not None:
        context["positions"] = []
        if player in ["player1", "player_bot"]:
            context["status"] = metadata["status1"]
            for tmp in metadata["placePos"].values():
                if tmp["player"] in ["player1", "shared"]:
                    context["positions"].append(tmp)
        elif player == "player2":
            context["status"] = metadata["status2"]
            for tmp in metadata["placePos"].values():
                if tmp["player"] in ["player2", "shared"]:
                    context["positions"].append(tmp)
        else:
            raise RuntimeError(f"Error: wrong playerid {player}")

    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/tasks/', methods=['GET'])
def get_tasks():
    player = flask.request.args.get("player")
    if not player in ["player1","player2","player_bot"]:
        raise RuntimeError("Error: wrong playerid")
    if player == "player_bot":
        player = "player1"
    context = {}
    context["tasks"] = metadata["task"][player]
    return flask.jsonify(**context), 200



@tdweb.app.route('/api/v1/addchats/', methods=['POST'])
def add_chats():
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
    context = db_get_chats()
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/objlist/', methods=['GET'])
def get_obj():    
    context = {"obj":[]}
    player = flask.request.args.get("player")
    for obj_id, res in metadata["objList"].items():
        tmp = {}
        tmp["objectId"] = obj_id
        tmp["objectName"] = res["name"]
        if player in ["player1", "player_bot"]:
            tmp["reachable"] = res["reachable1"]
            context["obj"].append(tmp)
        elif player == "player2":
            tmp["reachable"] = res["reachable2"]
            context["obj"].append(tmp)
        else:
            raise RuntimeError(f"Error: wrong playerid {player}")
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/shareInfo/', methods=['GET'])
def get_shareInfo():
    context = {}
    context["shareInfo"] = metadata["shareInfo"]
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/addInfo/', methods=['POST'])
def add_shareInfo():
    task = flask.request.json.get('task')
    objects = flask.request.json.get('objects')
    relation = flask.request.json.get('relation')
    player = flask.request.json.get('player')
    if task is None or objects is None or relation is None or not player == 'player_bot':
        flask.abort(404)
    player = 'player1'
    shareInfo = {"player":player, "task":task, "objects":objects, "relation":relation}
    for tk in metadata["task"][player]:
        if tk["task"] == task:
            if not tk["shared"]:
                tk["shared"] = True
                metadata["shareInfo"].append(shareInfo)
                metadata["turn"]["canShare"] = False
    context = {}
    return flask.jsonify(**context), 200



@tdweb.app.route('/api/v1/sendcmd/',methods=['POST'])
def send_control():
    print("sending type")
    args = flask.request.json.get('args')
    player = flask.request.json.get('player')
    cmd = flask.request.json.get('cmd')
    print(cmd, args)
    if cmd is None or args is None or player is None:
        flask.abort(404)
    command = {"type": cmd, "args": args}
    if player in ["player1", "player_bot"]:
        metadata["cmds1"].append(command)
        if player == "player_bot":
            if cmd == "pick":
                metadata["turn"]["canPick"] = False
            elif cmd == "drop":
                metadata["turn"]["canDrop"] = False
    elif player == "player2":
        metadata["cmds2"].append(command)
    else:
        flask.abort(404)
    
    context = {}
    return flask.jsonify(**context), 200




@tdweb.app.route('/api/v1/turn/',methods=['GET'])
def get_turn():
    context = {}
    for k, status in metadata["turn"].items():
        context[k] = status
    return flask.jsonify(**context), 200


@tdweb.app.route('/api/v1/changeturn/',methods=['PUT'])
def change_turn():
    context = {}
    metadata["turn"]["playerTurn"] = False
    metadata["turn"]["canPick"] = False
    metadata["turn"]["canDrop"] = False
    metadata["turn"]["canShare"] = False
    return flask.jsonify(**context), 200