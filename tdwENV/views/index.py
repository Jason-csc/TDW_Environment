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

from tdwENV.views.TDW import startTDW


import cv2

camera=[]
prepared = [False]
prev = None

@tdwENV.app.route('/')
def show_index():
    """Display / route."""
    context = {}
    thread = threading.Thread(target=startTDW,args=(camera,prepared,))
    thread.start()

    while True:
        if prepared[0]:
            break
        time.sleep(0.1)

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
            prev = frame
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@tdwENV.app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')