from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from tdw.librarian import ModelLibrarian
from tdweb.views.imagecapture import ImgCaptureModified
from tdw.add_ons.object_manager import ObjectManager

import numpy as np
import numpy
import cv2

import time
from typing import List, Dict
from enum import Enum
import threading

class State(Enum):
    """
    The state of a Magnebot
    """
    initializing = 0
    grasp = 1
    grasp_back = 2
    drop = 3
    drop_back = 4
    reset = 5


class PDRobot(Magnebot):
    """
    This is a sub-class of Magnebot controlled by player to pick item and drop into the bowl
    """

    def __init__(self, objupdated_,robot_id: int = 0,
            position: Dict[str, float] = None, 
            rotation: Dict[str, float] = None,
            posBowl: Dict[str, float] = None,
            cmds: List[int] = None):
        # We're not using images in this simulation.
        super().__init__(robot_id=robot_id, position=position, rotation=rotation)
        # This will be set within self.update()

        self.state = State.initializing
        self.id = robot_id
        self.objList = cmds
        self.posBowl = posBowl
        self.objID = None
        self.objupdated_ = objupdated_
    
    def on_send(self, resp: List[bytes]) -> None:
        """
        Pick object based on objectID and drop into bowl (posBowl)
        """
        super().on_send(resp=resp)
        print("====State==== ",self.state)
        if self.state == State.initializing and len(self.objList) > 0:
            self.objID = self.objList.pop(0)
            self.grasp(self.objID,Arm.right)
            self.state = State.grasp
            self.objupdated_[0] = False
        elif self.state == State.grasp and self.action.done:
            #TO BE FIXED: hard coded 
            self.reach_for(target={"x": -0.22, "y": 1.25, "z": -1}, arm=Arm.right)            
            self.state = State.grasp_back
            self.objupdated_[0] = False
        elif self.state == State.grasp_back and self.action.done:
            self.drop(self.objID,Arm.right)
            self.state = State.drop
        elif self.state == State.drop and self.action.done:
            #TO BE FIXED: hard coded 
            self.reach_for(target={"x": 0, "y": 1.2, "z": -1}, arm=Arm.right)
            self.state = State.drop_back
            self.objupdated_[0] = False
        elif self.state == State.drop_back and self.action.done:
            self.reset_arm(arm=Arm.right)
            self.state = State.reset
        elif self.state == State.reset and self.action.done:
            self.state = State.initializing

        """
        DUMMY ACTION
        """
        # if self.state == State.initializing and len(self.objList) > 0:
        #     self.objID = self.objList.pop(0)
        #     self.move_by(self.objID)
        #     self.state = State.grasp
        # elif self.state == State.grasp and self.action.done:
        #     self.move_by(-self.objID)
        #     self.state = State.grasp_back
        # elif self.state == State.grasp_back and self.action.done:
        #     self.state = State.initializing




class MultiMagnebot(Controller):
    def __init__(self, info: Dict, port: int = 1071, check_version: bool = True, launch_build: bool = False):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.info = info
        self.DONE = False
        self.objupdated = [True]
        # Create two robots with corresponding commands
        self.magnebot1 = PDRobot(position={"x": 0, "y": 0, "z": -1.67}, 
                                rotation={"x": 0, "y": 0, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds1"],
                                objupdated_=self.objupdated)
        self.magnebot2 = PDRobot(position={"x": 0, "y": 0, "z": 1.67}, 
                                rotation={"x": 0, "y": 180, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds2"],
                                objupdated_=self.objupdated)
        # Create a camera and enable image capture.
        self.camera1 = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": -1.55},
                                rotation={"x": 30, "y": 0, "z": 0},
                                field_of_view = 100,
                                avatar_id="a")
        self.camera2 = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": 1.55},
                                rotation={"x": 30, "y": 180, "z": 0},
                                field_of_view = 100,
                                avatar_id="b")
        # Create object manager to get objects for each frame                  
        self.objManager = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
        #Create capture to send images into camera1 and camera2
        self.capture = ImgCaptureModified(avatar_ids=["a","b"],png=False,image_q1=self.info["camera1"],image_q2=self.info["camera2"])
        # Note the order of add-ons. The Magnebot must be added first so that the camera can look at it.
        self.add_ons.extend([self.magnebot1, self.magnebot2, self.objManager, self.camera1,self.camera2, self.capture])
        
        commands = self.setUp()
        self.communicate(commands)
        
        #Initialize object db
        self.getOBJ()
        self.info["prepared"] = True
        self.info["objNeedUpdate"] = True

        thread = threading.Thread(target=self.updateOBJ,args=())
        thread.start()

    def run(self):
        print("Starting TDW...")
        while not self.DONE:
            self.communicate([])
            time.sleep(0.1)
        self.communicate({"$type": "terminate"})
    

    def getOBJ(self):
        for object_id,objt in self.objManager.objects_static.items():
            tmp = {}
            tmp["name"] = objt.name
            tmp["position"] = self.objManager.transforms[object_id].position
            tmp["reachable1"] = True
            tmp["reachable2"] = True
            # TO BE FIXED: hard coded for reachable
            self.info["objList"][object_id] = tmp



    def updateOBJ(self):
        while not self.DONE:
            if not self.objupdated[0]:
                self.getOBJ()               
                self.objupdated[0] = True
                self.info["objNeedUpdate"] = True
                print("=====UpdateOBJ thread: need to update objdb!!!===")
                print(5*"=\n")
            time.sleep(0.1)
                
                


    def setUp(self):
        print("Setting Up Scene...")
        '''Set up scene'''
        commands = [{"$type": "set_screen_size",
                        "width": 350,
                        "height": 350}]
        # commands.extend([{"$type": "set_render_quality", "render_quality": 5}])
        commands.extend([TDWUtils.create_empty_room(12, 12)])
        commands.extend(self.get_add_physics_object(model_name='quatre_dining_table',
                                            #  library="models_core.json",
                                                position={"x": 0, "y": 0, "z": 0},
                                                object_id=self.get_unique_id()))

        bowl_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name='serving_bowl',
                                            library="models_core.json",
                                                position={"x": -0.3, "y": 0.85, "z": -1},
                                                rotation={"x":0,"y":120,"z":0},
                                                mass = 3,
                                                bounciness=1,
                                                static_friction = 1,
                                                object_id=bowl_id,
                                                ))

        apple_id = self.get_unique_id()
        apple_id = 999 # TO BE DELETED
        commands.extend(self.get_add_physics_object(model_name='apple',
                                            library="models_core.json",
                                                position={"x": 0.2, "y": 0.8682562, "z": -1.1},
                                                mass = 3,
                                                bounciness=1,
                                                object_id=apple_id))


        # orange_id = self.get_unique_id()
        # commands.extend(self.get_add_physics_object(model_name='b04_orange_00',
        #                                     library="models_core.json",
        #                                         position={"x": 0.10, "y": 0.8682562, "z": -0.9},
        #                                         mass = 3,
        #                                         bounciness=1,
        #                                         object_id=orange_id))


        # banana_id = self.get_unique_id()
        # commands.extend(self.get_add_physics_object(model_name='b04_banana',
        #                                     library="models_core.json",
        #                                         position={"x": 0, "y": 0.8682562, "z": -0.4},
        #                                         mass = 3,
        #                                         bounciness=1,
        #                                         object_id=banana_id))

        # banana2_id = self.get_unique_id()
        # commands.extend(self.get_add_physics_object(model_name='b04_banana',
        #                                     library="models_core.json",
        #                                         position={"x": 0.24, "y": 0.8682562, "z": 0.4},
        #                                         mass = 3,
        #                                         bounciness=1,
        #                                         object_id=banana2_id))


        # apple2_id = self.get_unique_id()
        # commands.extend(self.get_add_physics_object(model_name='apple',
        #                                     library="models_core.json",
        #                                         position={"x": -0.17, "y": 0.8682562, "z": 0.25},
        #                                         mass = 3,
        #                                         bounciness=1,
        #                                         object_id=apple2_id))
        return commands



def startMultiTDW(info):
    info["start"] = True
    c = MultiMagnebot(info=info)
    c.run()