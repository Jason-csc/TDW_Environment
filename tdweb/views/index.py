"""
tdwebindex (main) view.
URLs include:
/
"""
from crypt import methods
from queue import Queue
import flask
from flask import Flask,render_template,Response
import tdweb
import threading
import numpy as np
import time

from tdweb.tdwHandler.MultiTDW import startMultiTDW
from tdweb import metadata as info

import cv2


prev1 = None
prev2 = None



# import random
# def dummy_addcmds1(info):
#     #TO BE FIXED: call by buttom to add cmds
#     print("INPUTTING PICK APPLE ")
#     time.sleep(10)
#     info["cmds1"].append(999)
        
    
# def dummy_addcmds2(info):
#     return 0
#     # while True:
#     #     # if len(info["cmds2"]) == 0:
#     #     #     info["cmds2"].append(random.choice((1,2,1.5)))
#     #     # time.sleep(10)




@tdweb.app.route('/player1/',methods=['GET'])
def show_player1():
    """Display / route."""
    if not info["start"]:
        thread = threading.Thread(target=startMultiTDW,args=(info,))
        thread.start()
        # TO be fixed: DUMMY ADD CMD
    while True:
        if info["prepared"]:
            break
        time.sleep(0.1)
    context = {}
    return flask.render_template("index1.html", **context)


@tdweb.app.route('/player2/',methods=['GET'])
def show_player2():
    """Display / route."""
    while True:
        if info["prepared"]:
            break
        time.sleep(0.1)
    context = {}
    return flask.render_template("index2.html", **context)



def generate_frames1():
    global prev1
    while True:
        ## read the camera frame1
        if len(info["camera1"]) == 0:
            frame = prev1
        else:
            frame=info["camera1"].pop(0)
            tmp = frame[:,:,0].copy()
            frame[:,:,0] = frame[:,:,2]
            frame[:,:,2] = tmp
            prev1 = frame
        
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def generate_frames2():
    global prev2
    while True:
        ## read the camera frame2
        if len(info["camera2"]) == 0:
            frame = prev2
        else:
            frame=info["camera2"].pop(0)
            tmp = frame[:,:,0].copy()
            frame[:,:,0] = frame[:,:,2]
            frame[:,:,2] = tmp
            prev2 = frame
        
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@tdweb.app.route('/video1')
def video1():
    return Response(generate_frames1(),mimetype='multipart/x-mixed-replace; boundary=frame')


@tdweb.app.route('/video2')
def video2():
    return Response(generate_frames2(),mimetype='multipart/x-mixed-replace; boundary=frame')



# @tdweb.app.route('/control/<player>/',methods=['POST'])
# def send_control(player):
#     objectid = flask.request.form.get('objectid')
#     if objectid is None:
#         flask.abort(404)
#     objectid = int(objectid)
#     if player == "player1":
#         print("="*10)
#         print("SENDDING ",objectid)
#         print("="*10)
#         info["cmds1"].append(objectid)
#     elif player == "player2":
#         info["cmds2"].append(objectid)
#     else:
#         flask.abort(404)
#     return flask.redirect(flask.url_for(f"show_{player}"))