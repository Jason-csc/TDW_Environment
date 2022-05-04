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

camera1=[]
camera2=[]
prepared = [False,False]
commands = []
prev = None


def dummy_TDW(camera1,camera2,prepared,commands):
    prepared[1] = True
    time.sleep(10)
    print("READY")
    prepared[0] = True
    while True:
        img= (np.random.randint(100,255,(100,100,3))).astype(np.uint8)
        camera1.append(img)
        img= (np.random.randint(0,120,(100,100,3))).astype(np.uint8)
        camera2.append(img)



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
    if not prepared[1]:
        thread = threading.Thread(target=dummy_TDW,args=(camera1,camera2,prepared,commands))
        thread.start()
    while True:
        if prepared[0]:
            break
        time.sleep(0.1)
    context = {}
    return flask.render_template("index1.html", **context)


@tdweb.app.route('/player2/',methods=['GET'])
def show_player2():
    """Display / route."""
    while True:
        if prepared[0]:
            break
        time.sleep(0.1)
    context = {}
    return flask.render_template("index2.html", **context)



def generate_frames1():
    while True:
        ## read the camera frame
        success = len(camera1) > 0
        if not success:
            frame = prev
        else:
            frame=camera1.pop(0)
            tmp = frame[:,:,0].copy()
            frame[:,:,0] = frame[:,:,2]
            frame[:,:,2] = tmp
            prev = frame
        
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def generate_frames2():
    while True:
        ## read the camera frame
        success = len(camera2) > 0
        if not success:
            frame = prev
        else:
            frame=camera2.pop(0)
            tmp = frame[:,:,0].copy()
            frame[:,:,0] = frame[:,:,2]
            frame[:,:,2] = tmp
            prev = frame
        
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



