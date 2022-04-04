"""
tdwENVindex (main) view.
URLs include:
/
"""
from queue import Queue
import flask
from flask import Flask,render_template,Response
import tdwENV
import threading
import numpy as np
import time

import cv2

camera=[]
prev = None

@tdwENV.app.route('/')
def show_index():
    """Display / route."""
    context = {}
    thread = threading.Thread(target=out,args=(camera,))
    thread.start()

    return flask.render_template("index.html", **context)



def out(c):
    i = 0
    while True:
        i += 1
        img= (np.random.randint(0,255,(1000,1000,3))).astype(np.uint8)
        c.append(img)
        if i > 100:
            time.sleep(2)
            i = i // 2


def generate_frames():
    while True:
        ## read the camera frame
        success = len(camera) > 0
        if not success:
            frame = prev
        else:
            frame=camera.pop(0)
            prev = frame
        ret,buffer=cv2.imencode('.png',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')


@tdwENV.app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')