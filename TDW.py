'''
Demo for magnet robot in TDW
'''


from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from tdw.librarian import ModelLibrarian
from imagecapture import ImgCaptureModified

import numpy
import cv2



# # show all the objects in TDW
# librarian = ModelLibrarian()
# for record in librarian.records:
#     print(record.name)

def startTDW(imgQueue):
    c = Controller()
    magnebot = Magnebot(position={"x": 0, "y": 0, "z": -1.67}, rotation={"x": 0, "y": 0, "z": 0},robot_id=c.get_unique_id())
    magnebot2 = Magnebot(position={"x": 0, "y": 0, "z": 1.67}, rotation={"x": 0, "y": 180, "z": 0},robot_id=c.get_unique_id())
    # Create a camera and enable image capture.
    camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": -1.55},
                            rotation={"x": 30, "y": 0, "z": 0},
                            field_of_view = 100,
                            avatar_id="a")
    # path: directory to store images

    capture = ImgCaptureModified(avatar_ids=["a"],png=True,image_q=imgQueue)
    # Note the order of add-ons. The Magnebot must be added first so that the camera can look at it.
    c.add_ons.extend([magnebot, magnebot2, camera, capture])
    # c.add_ons.extend([magnebot])


    print("Setting Up Scene...")
    '''Set up scene'''
    commands = [{"$type": "set_screen_size",
                    "width": 500,
                    "height": 500}]
    commands.extend([TDWUtils.create_empty_room(12, 12)])
    commands.extend(c.get_add_physics_object(model_name='quatre_dining_table',
                                        #  library="models_core.json",
                                            position={"x": 0, "y": 0, "z": 0},
                                            object_id=c.get_unique_id()))

    bowl_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='serving_bowl',
                                        library="models_core.json",
                                            position={"x": -0.3, "y": 0.85, "z": -1},
                                            rotation={"x":0,"y":120,"z":0},
                                            mass = 3,
                                            bounciness=1,
                                            static_friction = 1,
                                            object_id=bowl_id,
                                            ))

    apple_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='apple',
                                        library="models_core.json",
                                            position={"x": 0.2, "y": 0.8682562, "z": -1.1},
                                            mass = 3,
                                            bounciness=1,
                                            object_id=apple_id))


    orange_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='b04_orange_00',
                                        library="models_core.json",
                                            position={"x": 0.10, "y": 0.8682562, "z": -0.9},
                                            mass = 3,
                                            bounciness=1,
                                            object_id=orange_id))


    banana_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='b04_banana',
                                        library="models_core.json",
                                            position={"x": 0, "y": 0.8682562, "z": -0.4},
                                            mass = 3,
                                            bounciness=1,
                                            object_id=banana_id))

    banana2_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='b04_banana',
                                        library="models_core.json",
                                            position={"x": 0.24, "y": 0.8682562, "z": 0.4},
                                            mass = 3,
                                            bounciness=1,
                                            object_id=banana2_id))


    apple2_id = c.get_unique_id()
    commands.extend(c.get_add_physics_object(model_name='apple',
                                        library="models_core.json",
                                            position={"x": -0.17, "y": 0.8682562, "z": 0.25},
                                            mass = 3,
                                            bounciness=1,
                                            object_id=apple2_id))

    resp = c.communicate(commands)



    print("Starting TDW...")

    '''Control the robot by pick/drop'''
    while True:
        cmd = input(">>Input Command: ")
        if cmd == "pick apple":
            magnebot.grasp(apple_id,Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            # print(magnebot.action.status)
            magnebot.reach_for(target={"x": 0.1, "y": 1.3, "z": -1}, arm=Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            print(magnebot.action.status)
        elif cmd == "drop":
            magnebot.reach_for(target={"x": -0.22, "y": 1.25, "z": -1}, arm=Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            magnebot.drop(apple_id,Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            # print(magnebot.action.status)
            magnebot.reach_for(target={"x": 0, "y": 1.2, "z": -1}, arm=Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            # print(magnebot.action.status)
            magnebot.reset_arm(arm=Arm.right)
            while magnebot.action.status == ActionStatus.ongoing:
                c.communicate([])
            c.communicate([])
            print(magnebot.action.status)
        else:
            c.communicate({"$type": "terminate"})
            break


