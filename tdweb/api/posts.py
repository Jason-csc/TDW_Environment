"""REST API for posts."""
import flask
import tdweb


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

