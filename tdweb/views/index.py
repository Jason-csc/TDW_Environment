"""
tdwebindex (main) view.
URLs include:
/
"""
from curses import meta
import flask
from flask import Flask,render_template,Response
import tdweb
import threading
import numpy as np
import time
import numpy 

from tdweb.tdwHandler.bot import startbot
from tdweb.tdwHandler.MultiTDW_cv2 import startGame
from tdweb import metadata as metadata

import cv2


prev1 = None
prev2 = None


@tdweb.app.route('/player1/',methods=['GET'])
def show_player1():
    """Display / route."""
    if not metadata["start"]:
        thread = threading.Thread(target=startGame,args=(metadata,))
        thread.start()
    while True:
        if metadata["prepared"]:
            break
    context = {}
    return flask.render_template("index1.html", **context)


@tdweb.app.route('/player2/',methods=['GET'])
def show_player2():
    """Display / route."""
    while True:
        if metadata["prepared"]:
            break
    context = {}
    return flask.render_template("index2.html", **context)


@tdweb.app.route('/player_bot/',methods=['GET'])
def show_player_bot():
    """Display / route."""
    if not metadata["start"]:
        thread = threading.Thread(target=startGame,args=(metadata,))
        thread.start()
    while True:
        if metadata["prepared"]:
            break
    thread_bot = threading.Thread(target=startbot, args=(metadata,))
    thread_bot.start()
    context = {}
    return flask.render_template("index3.html", **context)


def generate_frames1():
    global prev1
    while True:
        ## read the camera frame1
        if len(metadata["camera1"]) == 0:
            frame = prev1
            if prev1 is None:
                continue
        else:
            frame=metadata["camera1"].pop(0)
            frame = numpy.array(frame)[:,:,::-1]
            prev1 = frame
        
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def generate_frames2():
    global prev2
    while True:
        ## read the camera frame2
        if len(metadata["camera2"]) == 0:
            if prev2 is None:
                continue
            frame = prev2
        else:
            frame=metadata["camera2"].pop(0)
            frame = numpy.array(frame)[:,:,::-1]
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

