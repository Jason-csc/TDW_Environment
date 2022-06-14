from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from tdw.librarian import ModelLibrarian
from tdweb.tdwHandler.imagecapture import ImgCaptureModified
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.step_physics import StepPhysics

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
            cmds: List[int] = None,
            status = None):
        super().__init__(robot_id=robot_id, position=position, rotation=rotation)
        self.cmd = None
        self.state = State.initializing
        self.id = robot_id
        self.cmdList = cmds
        self.posBowl = posBowl
        self.objID = None
        self.objupdated_ = objupdated_
        self.status = status
    
    def on_send(self, resp: List[bytes]) -> None:
        """
        Pick object based on objectID and drop into bowl (posBowl)
        """
        super().on_send(resp=resp)
        # print(f"====State {self.id} {self.state} ====")
        # print(self.status)
        # print(self.cmdList)
        if self.cmd is None and len(self.cmdList) > 0:
            self.cmd = self.cmdList.pop(0)
            if self.cmd["type"][0] == "p":
                self.objID = int(self.cmd["args"])
                self.grasp(self.objID, Arm.right)
                self.state = State.grasp
                self.status[0] = "DROP"
            elif self.cmd["type"][0] == "d":
                drop_pos = self.cmd["args"]
                self.reach_for(target={
                                "x": drop_pos["x"], 
                                "y": drop_pos["y"]+0.45, 
                                "z": drop_pos["z"]
                                }, 
                                arm=Arm.right)       
                self.state = State.grasp_back
                self.status[0] = "PICK"
            self.objupdated_[0] = False
        elif not self.cmd is None:
            if self.cmd["type"][0] == "p": # 'pick' cmd
                if self.state == State.grasp and self.action.done:
                    self.state = State.initializing
                    self.cmd = None
            elif self.cmd["type"][0] == "d": # 'drop' cmd
                if self.state == State.grasp_back and self.action.done:
                    drop_pos = self.cmd["args"]
                    self.reach_for(target={
                                "x": drop_pos["x"], 
                                "y": drop_pos["y"]+0.03, 
                                "z": drop_pos["z"]
                                }, 
                                arm=Arm.right)
                    self.state = State.drop
                elif self.state == State.drop and self.action.done:
                    #TO BE FIXED: hard coded
                    self.drop(self.objID,Arm.right)
                    self.state = State.drop_back
                    self.objupdated_[0] = False
                elif self.state == State.drop_back and self.action.done:
                    self.reset_arm(arm=Arm.right)
                    self.state = State.reset
                elif self.state == State.reset and self.action.done:
                    self.state = State.initializing
                    self.objID = None
                    self.cmd = None





class MultiMagnebot(Controller):
    def __init__(self, info: Dict, port: int = 1071, check_version: bool = True, launch_build: bool = False):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.info = info
        self.DONE = False
        self.objupdated = [True]
        # Create two robots with corresponding commands
        self.magnebot1 = PDRobot(position={"x": 0, "y": 0.45, "z": -0.84}, 
                                rotation={"x": 0, "y": 0, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds1"],
                                status=self.info["status1"],
                                objupdated_=self.objupdated)
        self.magnebot2 = PDRobot(position={"x": 0, "y": 0.45, "z": 0.84}, 
                                rotation={"x": 0, "y": 180, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds2"],
                                status=self.info["status2"],
                                objupdated_=self.objupdated)
        # Create a camera and enable image capture.
        self.camera1 = ThirdPersonCamera(position={"x": 0, "y": 1.4, "z": -0.74},
                                rotation={"x": 26, "y": 0, "z": 0},
                                field_of_view = 95,
                                avatar_id="a")
        self.camera2 = ThirdPersonCamera(position={"x": 0, "y": 1.4, "z": 0.74},
                                rotation={"x": 26, "y": 180, "z": 0},
                                field_of_view = 95,
                                avatar_id="b")
        # Create object manager to get objects for each frame                  
        self.objManager = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
        #Create capture to send images into camera1 and camera2
        self.capture = ImgCaptureModified(avatar_ids=["a","b"],png=False,image_q1=self.info["camera1"],image_q2=self.info["camera2"])
        # Note the order of add-ons. The Magnebot must be added first so that the camera can look at it.
        self.add_ons.extend([self.magnebot1, self.magnebot2, self.objManager, self.camera1,self.camera2, self.capture, StepPhysics(num_frames=20)])
        # self.add_ons.extend([self.magnebot1, self.magnebot2, self.objManager,self.camera1,self.camera2])
        
        commands = self.setUp()
        self.communicate(commands)
        print("finish communicate")
        
        #Initialize object db
        self.getOBJ()
        print("finish get obj")
        self.info["prepared"] = True

        thread = threading.Thread(target=self.updateOBJ,args=())
        thread.start()

    def run(self):
        print("Starting TDW...")
        while not self.DONE:
            self.communicate([])
        self.communicate({"$type": "terminate"})
    

    def getOBJ(self):
        for object_id,objt in self.objManager.objects_static.items():
            if "bowl" in objt.name or "box" in objt.name or "table" in objt.name:
                continue
            tmp = {}
            tmp["name"] = objt.name
            # update
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
            time.sleep(0.1)
                
                


    def setUp(self):
        print("Setting Up Scene...")
        '''Set up scene'''
        commands = [{"$type": "set_screen_size",
                        "width": 800,
                        "height": 600},
                    {"$type": "set_render_quality", "render_quality": 5}
                    ]
        

        commands.extend([TDWUtils.create_empty_room(6, 6)])
        commands.extend(self.get_add_physics_object(model_name='b05_table_new',
                                                position={"x": 0, "y": 0, "z": 0},
                                                rotation = {"x":0,"y":0,"z":0},
                                                object_id=self.get_unique_id()))

        table_top = {"x":-1.49850675e-05,  "y":6.51243031e-01, "z":-1.47134961e-06}                                       
        
        bowl1_id1 = self.get_unique_id()
        bowl1_pos1 = {"x": table_top['x']+0.46, "y": table_top['y'], "z":table_top['z']-0.24}
        commands.extend(self.get_add_physics_object(model_name='round_bowl_small_beech',
                                        library="models_core.json",
                                            position=bowl1_pos1,
                                            rotation={"x":0,"y":0,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=bowl1_id1,
                                            ))
        commands.extend([{"$type": "scale_object", "id": bowl1_id1, "scale_factor": {"x": 0.4, "y": 0.2, "z": 0.4}}])
        commands.extend([{"$type": "set_color", "color": {"r": 0, "g": 0.5, "b": 1, "a": 1}, "id": bowl1_id1}])

        bowl1_id2 = self.get_unique_id()
        bowl1_pos2 = {"x": table_top['x']-0.46, "y": table_top['y'], "z":table_top['z']-0.24}
        commands.extend(self.get_add_physics_object(model_name='box_tapered_white_mesh',
                                        library="models_core.json",
                                            position=bowl1_pos2,
                                            rotation={"x":0,"y":90,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=bowl1_id2,
                                            ))
        commands.extend([{"$type": "scale_object", "id": bowl1_id2, "scale_factor": {"x": 0.3, "y": 0.1, "z": 0.3}}])
        commands.extend([{"$type": "set_color", "color": {"r": 1, "g": 0.5, "b": 0, "a": 1}, "id": bowl1_id2}])

        bowl2_id1 = self.get_unique_id()
        bowl2_pos1 = {"x": table_top['x']+0.46, "y": table_top['y'], "z":table_top['z']+0.24}
        commands.extend(self.get_add_physics_object(model_name='b04_bowl_smooth',
                                        library="models_core.json",
                                            position=bowl2_pos1,
                                            rotation={"x":0,"y":120,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=bowl2_id1,
                                            ))

        bowl2_id2 = self.get_unique_id()
        bowl2_pos2 = {"x": table_top['x']-0.46, "y": table_top['y'], "z":table_top['z']+0.24}
        commands.extend(self.get_add_physics_object(model_name='b04_bowl_smooth',
                                        library="models_core.json",
                                            position=bowl2_pos2,
                                            rotation={"x":0,"y":120,"z":0},
                                            bounciness=0,
                                            # scale_factor=0.7,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=bowl2_id2,
                                            ))



        apple_id = self.get_unique_id()
        apple_pos = table_top
        commands.extend(self.get_add_physics_object(model_name='apple',
                                        library="models_core.json",
                                            position=apple_pos,
                                            bounciness=0,
                                            # mass=9999,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=apple_id))
        
        
        commands.extend(self.get_add_physics_object(model_name='b04_orange_00',
                                        library="models_core.json",
                                            position={"x": table_top['x'], "y": table_top['y'], "z":table_top['z']+0.2},
                                            bounciness=0,
                                            # mass=9999,
                                            kinematic = True,
                                            static_friction = 1,
                                            dynamic_friction = 1,
                                            object_id=self.get_unique_id()))

        # TO BE FIXED
        share_pos = table_top
        self.info["placePos1"].append({"name":"bowl1_1","pos":bowl1_pos1})
        self.info["placePos1"].append({"name":"bowl1_2","pos":bowl1_pos2})
        self.info["placePos1"].append({"name":"sharePlace","pos":share_pos})

        
        self.info["placePos2"].append({"name":"bowl2_1","pos":bowl2_pos1})
        self.info["placePos2"].append({"name":"bowl2_2","pos":bowl2_pos2})
        self.info["placePos2"].append({"name":"sharePlace","pos":share_pos})



        return commands



def startMultiTDW(info):
    info["start"] = True
    c = MultiMagnebot(info=info)
    c.run()