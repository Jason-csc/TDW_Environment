"""
tdwebindex (main) view.
URLs include:
/
"""
from queue import Queue
import flask
from flask import Flask,render_template,Response
import tdweb
import threading
import numpy as np
import time

from tdweb.views.TDW import startTDW


import cv2

camera=[]
prepared = [False]
commands = []
prev = None

# @tdweb.app.route('/',methods=['GET','POST'])
# def show_index():
#     """Display / route."""
#     context = {}
#     # target = flask.request.args.get("target",default=None)
#     # if target is None:       
        
#     #     thread = threading.Thread(target=startTDW,args=(camera,prepared,commands))
#     #     thread.start()

#     #     while True:
#     #         if prepared[0]:
#     #             break
#     #         time.sleep(0.1)
#     # else:
#     #     command = flask.request.form['text']
#     #     print("get command",command)
#     #     commands.append(command)

#     return flask.render_template("index.html", **context)


@tdweb.app.route('/player1/',methods=['GET'])
def show_player1():
    """Display / route."""
    context = {}
    context["player"] = "player1"
    return flask.render_template("index.html", **context)


@tdweb.app.route('/player2/',methods=['GET'])
def show_player2():
    """Display / route."""
    context = {}
    context["player"] = "player2"
    return flask.render_template("index.html", **context)


# def out(c):
#     i = 0
#     while True:
#         i += 1
#         img= (np.random.randint(0,255,(500,20,3))).astype(np.uint8)
#         c.append(img)


def generate_frames():
    while True:
        ## read the camera frame
        success = len(camera) > 0
        if not success:
            frame = prev
        else:
            frame=camera.pop(0)
            tmp = frame[:,:,0].copy()
            frame[:,:,0] = frame[:,:,2]
            frame[:,:,2] = tmp
            prev = frame
        
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@tdweb.app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

