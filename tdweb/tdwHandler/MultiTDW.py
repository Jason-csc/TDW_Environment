from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from magnebot.ik.target_orientation import TargetOrientation
from magnebot.ik.orientation_mode import OrientationMode
from tdw.librarian import ModelLibrarian
from tdweb.tdwHandler.imagecapture import ImgCaptureModified
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.step_physics import StepPhysics

import random
import json
import numpy as np
import random
import itertools
from collections import defaultdict
import time
from typing import List, Dict
from enum import Enum
import threading

from tdweb.tdwHandler.random_game_generator import generate_game


class State(Enum):
    """
    The state of a Magnebot
    """
    initializing = 0
    grasp = 1
    grasp_back = 2
    drop = 3
    drop_back = 4
    reset_arm = 5


class PDRobot(Magnebot):
    """
    This is a sub-class of Magnebot controlled by player to pick item and drop into the bowl
    """

    def __init__(self, objupdated_,robot_id: int = 0,
            position: Dict[str, float] = None, 
            rotation: Dict[str, float] = None,
            cmds: List[int] = None,
            table_top: Dict[str, float] = None,
            status = None):
        super().__init__(robot_id=robot_id, position=position, rotation=rotation)
        self.position = position
        self.cmd = None
        self.arm = None
        self.arm_switch = None
        self.state = State.initializing
        self.id = robot_id
        self.cmdList = cmds
        self.objID = None
        self.table_top = table_top
        self.objupdated_ = objupdated_
        self.status = status
        self.reset = 0
    
    def on_send(self, resp: List[bytes]) -> None:
        """
        Pick object based on objectID and drop into bowl (posBowl)
        """
        super().on_send(resp=resp)
        print(f"====State {self.id} {self.state} {self.objID} {self.arm} {self.reset}====")
        print(self.status)
        print(self.cmdList)
        if self.cmd is None and len(self.cmdList) > 0:
            self.cmd = self.cmdList.pop(0)
            if self.cmd["type"] == "pick":
                objID, obj_x = self.cmd["args"]
                self.objID = int(objID)
                delta_z = 0.27 if self.position["z"] > 0 else -0.27
                if self.position["z"]*obj_x >  0:
                    self.arm = Arm.left
                else:
                    self.arm = Arm.right
                self.reach_for(target={
                                "x": self.table_top["x"], 
                                "y": self.table_top["y"]+0.46, 
                                "z": self.table_top["z"]+delta_z
                                }, 
                                arm=self.arm)
                self.state = State.grasp
            elif self.cmd["type"] == "drop":
                drop_pos = self.cmd["args"]
                self.reach_for(target={
                                "x": drop_pos["x"], 
                                "y": drop_pos["y"]+0.46, 
                                "z": drop_pos["z"]
                                }, 
                                arm=self.arm,
                                arrived_at = 0.11,
                                target_orientation=TargetOrientation.none, 
                                orientation_mode=OrientationMode.none)      
                self.state = State.grasp_back
                self.status[0] = "PICK"
            self.objupdated_[0] = False
        elif not self.cmd is None:
            if self.cmd["type"] == "pick": # 'pick' cmd
                if self.state == State.grasp:
                    self.reset = 0
                    self.grasp(self.objID, self.arm)
                    self.state = State.grasp_back
                    self.status[0] = "DROP"
                elif self.state == State.grasp_back and self.action.done:
                    self.reset = 0
                    delta_z = 0.27 if self.position["z"] > 0 else -0.27
                    self.reach_for(target={
                                    "x": self.table_top["x"], 
                                    "y": self.table_top["y"]+0.3, 
                                    "z": self.table_top["z"]+delta_z
                                    }, 
                                    arm=self.arm,
                                    arrived_at = 0.11,
                                    target_orientation=TargetOrientation.none, 
                                    orientation_mode=OrientationMode.none) 
                    self.state = State.drop
                elif self.state == State.drop and self.action.done:
                    self.reset = 0
                    self.state = State.initializing
                    self.cmd = None
            elif self.cmd["type"] == "drop": # 'drop' cmd
                if self.state == State.grasp_back and self.action.done:
                    self.reset = 0
                    drop_pos = self.cmd["args"]
                    self.reach_for(target={
                                "x": drop_pos["x"]*(1+random.uniform(-0.01,0.01)),
                                "y": self.table_top["y"]+0.03,
                                "z": drop_pos["z"]*(1+random.uniform(-0.01,0.01))
                                }, 
                                arm=self.arm,
                                arrived_at = 0.1,
                                target_orientation=TargetOrientation.none, 
                                orientation_mode=OrientationMode.none)
                    self.state = State.drop
                elif self.state == State.drop and self.action.done:
                    self.reset = 0
                    self.drop(self.objID,self.arm)
                    self.state = State.drop_back
                    self.objupdated_[0] = False
                elif self.state == State.drop_back and self.action.done:
                    self.reset = 0
                    self.reset_arm(arm=self.arm)
                    self.state = State.reset_arm
                elif self.state == State.reset_arm and self.action.done:
                    self.reset = 0
                    self.state = State.initializing
                    self.objID = None
                    self.cmd = None
                # if not self.action.done:
                #     if self.reset > 100:
                #         self.drop(self.objID,self.arm)
                #         self.state = State.drop
                #         self.reset = 0
                #     else:
                #         self.reset += 1





class MultiMagnebot(Controller):
    def __init__(self, info: Dict, port: int = 1071, check_version: bool = True, launch_build: bool = False):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.info = info
        self.object_info = {} # key: game_id
        self.bowl_info = {} # key: bin_id
        self.DONE = False
        self.objupdated = [True]
        self.table_top = {"x":-1.49850675e-05,  "y":6.65e-01, "z":-1.47134961e-06}
        # Create two robots with corresponding commands
        self.magnebot1 = PDRobot(position={"x": 0, "y": 0.45, "z": -0.824}, 
                                rotation={"x": 0, "y": 0, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds1"],
                                status=self.info["status1"],
                                table_top = self.table_top,
                                objupdated_=self.objupdated)
        self.magnebot2 = PDRobot(position={"x": 0, "y": 0.45, "z": 0.824}, 
                                rotation={"x": 0, "y": 180, "z": 0},
                                robot_id=self.get_unique_id(),
                                cmds=self.info["cmds2"],
                                status=self.info["status2"],
                                table_top = self.table_top,
                                objupdated_=self.objupdated)
        # Create a camera and enable image capture.
        self.camera1 = ThirdPersonCamera(position={"x": 0, "y": 1.4, "z": -0.72},
                                rotation={"x": 26, "y": 0, "z": 0},
                                field_of_view = 95,
                                avatar_id="a")
        self.camera2 = ThirdPersonCamera(position={"x": 0, "y": 1.4, "z": 0.72},
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
        
        print(">>> Generating Game Configuration...")
        self.game_config = json.loads(generate_game())
        commands = self.setUp()
        self.communicate(commands)
        
        #Initialize object db
        self.getOBJ()
        self.generateTask()
        self.info["prepared"] = True

        thread = threading.Thread(target=self.updateOBJ,args=())
        thread.start()

    def run(self):
        print(">>> Starting TDW...")
        while not self.DONE:
            self.communicate([])
        self.communicate({"$type": "terminate"})
    

    def getOBJ(self):
        for objt in self.object_info.values():
            tmp = {}
            object_id = objt["object_id"]
            tmp["name"] = objt["name"]
            # update
            tmp["position"] = self.objManager.transforms[object_id].position
            tmp["reachable1"] = bool(tmp["position"][-1] < self.table_top["z"]+0.04)
            tmp["reachable2"] = bool(tmp["position"][-1] > self.table_top["z"]-0.04)
            # TO BE FIXED: hard coded for reachable
            self.info["objList"][object_id] = tmp



    def updateOBJ(self):
        while not self.DONE:
            if not self.objupdated[0]:
                self.getOBJ()               
                self.objupdated[0] = True
            time.sleep(0.01)
    

    def generateTask(self):
        print(">>> Generating Game Tasks...")
        tasks = defaultdict(list)
        for player, knowledge_list in self.game_config["knowledge"].items():
            for knowledge in knowledge_list:
                if knowledge[0] == "inBin":
                    obj_id, bin_id = knowledge[1:]
                    obj_name = self.object_info[obj_id]['name']
                    bin_name = self.bowl_info[bin_id]['name']
                    task = f"{obj_name} should be placed to {bin_name}"
                elif knowledge[1] == "bin":
                    idf, _, obj1_id, obj2_id = knowledge
                    if not idf == "same":
                        idf = "different"
                    obj1_name = self.object_info[obj1_id]['name']
                    obj2_name = self.object_info[obj2_id]['name']
                    task = f"Place {obj1_name} and {obj2_name} should be placed in the {idf} bowl"
                elif knowledge[0] in ["same", "opposite"]:
                    obj1_id, pos, obj2_id = knowledge[1:]
                    obj1_name = self.object_info[obj1_id]['name']
                    obj2_name = self.object_info[obj2_id]['name']
                    task = f"{obj1_name} and {obj2_name} should be placed in the bowl with {knowledge[0]} {pos}"
                else:
                    assert False, f"Wrong Game Knowledge: {knowledge}"
                tasks[player].append(task)
        
        self.info["task"] = tasks
    
              


    def setUp(self):
        print(">>> Setting Up Scene...")
        '''Set Up Screen'''
        commands = [{"$type": "set_screen_size",
                        "width": 800,
                        "height": 600},
                    {"$type": "set_render_quality", "render_quality": 5}
                    ]

        commands.extend([TDWUtils.create_empty_room(6, 6)])
        commands.extend(self.get_add_physics_object(model_name='b05_table_new',
                                                library="models_core.json",
                                                position={"x": 0, "y": 0, "z": 0},
                                                rotation = {"x":0,"y":0,"z":0},
                                                bounciness=0,
                                                kinematic = True,
                                                static_friction = 0,
                                                dynamic_friction = 0,
                                                object_id=self.get_unique_id()))                           
        # table_top = TDWUtils.array_to_vector3(self.objManager.bounds[table_id].top)

        '''Set Up Bowls'''
        # Bowl for player1 - 1
        bowl1_id1 = self.get_unique_id()
        bowl1_pos1 = {"x": self.table_top['x']+0.56, "y": self.table_top['y'], "z":self.table_top['z']-0.24}
        commands.extend(self.get_add_physics_object(model_name='round_bowl_small_beech',
                                        library="models_core.json",
                                            position=bowl1_pos1,
                                            rotation={"x":0,"y":0,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 0,
                                            dynamic_friction = 0,
                                            object_id=bowl1_id1,
                                            ))
        bowl1_info1 = {"name":"Black Bowl", "pos":bowl1_pos1, "object_id":bowl1_id1}
        commands.extend([{"$type": "scale_object", "id": bowl1_id1, "scale_factor": {"x": 0.45, "y": 0.18, "z": 0.45}}])
        commands.extend([{"$type": "set_color", "color": {"r": 0, "g": 0.5, "b": 1, "a": 1}, "id": bowl1_id1}])
        # Bowl for player1 - 2
        bowl1_id2 = self.get_unique_id()
        bowl1_pos2 = {"x": self.table_top['x']-0.56, "y": self.table_top['y'], "z":self.table_top['z']-0.24}
        commands.extend(self.get_add_physics_object(model_name='round_bowl_small_beech',
                                        library="models_core.json",
                                            position=bowl1_pos2,
                                            rotation={"x":0,"y":0,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 0,
                                            dynamic_friction = 0,
                                            object_id=bowl1_id2,
                                            ))
        bowl1_info2 = {"name":"Green Bowl","pos":bowl1_pos2, "object_id":bowl1_id2}
        commands.extend([{"$type": "scale_object", "id": bowl1_id2, "scale_factor": {"x": 0.45, "y": 0.18, "z": 0.45}}])
        commands.extend([{"$type": "set_color", "color": {"r": 0, "g": 1, "b": 0, "a": 1}, "id": bowl1_id2}])
        # Bowl for player2 - 1
        bowl2_id1 = self.get_unique_id()
        bowl2_pos1 = {"x": self.table_top['x']+0.56, "y": self.table_top['y'], "z":self.table_top['z']+0.24}
        commands.extend(self.get_add_physics_object(model_name='box_tapered_white_mesh',
                                        library="models_core.json",
                                            position=bowl2_pos1,
                                            rotation={"x":0,"y":0,"z":0},
                                            bounciness=0,
                                            kinematic = True,
                                            static_friction = 0,
                                            dynamic_friction = 0,
                                            object_id=bowl2_id1,
                                            ))
        commands.extend([{"$type": "scale_object", "id": bowl2_id1, "scale_factor": {"x": 0.32, "y": 0.1, "z": 0.32}}])
        commands.extend([{"$type": "set_color", "color": {"r": 1, "g": 0.5, "b": 0, "a": 1}, "id": bowl2_id1}])
        bowl2_info1 = {"name":"Orange Bowl", "pos":bowl2_pos1, "object_id":bowl2_id1}
        # Bowl for player2 - 2
        bowl2_id2 = self.get_unique_id()
        bowl2_pos2 = {"x": self.table_top['x']-0.56, "y": self.table_top['y'], "z":self.table_top['z']+0.24}
        commands.extend(self.get_add_physics_object(model_name='box_tapered_white_mesh',
                                        library="models_core.json",
                                            position=bowl2_pos2,
                                            rotation={"x":0,"y":0,"z":0},
                                            bounciness=0,
                                            # scale_factor=0.7,
                                            kinematic = True,
                                            static_friction = 0,
                                            dynamic_friction = 0,
                                            object_id=bowl2_id2,
                                            ))
        commands.extend([{"$type": "scale_object", "id": bowl2_id2, "scale_factor": {"x": 0.32, "y": 0.1, "z": 0.32}}])
        commands.extend([{"$type": "set_color", "color": {"r": 0, "g": 0.8, "b": 1.5, "a": 1}, "id": bowl2_id2}])
        bowl2_info2 = {"name":"Blue Bowl","pos":bowl2_pos2, "object_id":bowl2_id2}

        '''Generate Objects'''
        self.ObjectGenerator(commands)

        share_pos1 = self.table_top.copy()
        share_pos1["x"] -= 0.1
        share_pos1["z"] += 0.01
        self.info["placePos1"].append(bowl1_info1)
        self.info["placePos1"].append(bowl1_info2)
        self.info["placePos1"].append({"name":"sharePlace","pos":share_pos1})

        share_pos2 = self.table_top.copy()
        share_pos2["x"] -= 0.1
        share_pos2["z"] += -0.01
        self.info["placePos2"].append(bowl2_info1)
        self.info["placePos2"].append(bowl2_info2)
        self.info["placePos2"].append({"name":"sharePlace","pos":share_pos2})

        self.bowl_info["A"] = bowl1_info1
        self.bowl_info["B"] = bowl1_info2
        self.bowl_info["C"] = bowl2_info1
        self.bowl_info["D"] = bowl2_info2
        
        return commands


    def ObjectGenerator(self,commands):
        print(">>> Generating Objects according to Game Configuration...")
        category_shape = [
            ('Battery','9v_battery'), # cuboid  '9v_battery'
            ('Ball','b04_geosphere001'),   # sphere
            ('Pepper','pepper')     # cylinder 
        ]
        category_color = [
            ("Red",{"r": 1, "g": 0, "b": 0, "a": 1}),
            ("Green",{"r": 0, "g": 1.1, "b": 0, "a": 1}),
            ("Black",{"r": 0, "g": 0, "b": 0, "a": 1})
        ]
        # category_scale = [
        #     ("Small",{"x": 1.5, "y": 1.5, "z":1.5}),
        #     ("Medium",{"x": 1.9, "y": 1.9, "z": 1.9}),
        #     ("Big",{"x": 2.4, "y": 2.2, "z": 2.4}),
        # ]
        # total_num = len(category_shape) * len(category_color) * len(category_scale)

        total_objects = list(itertools.product(category_shape, category_color))
        # TO BE DELETED
        random.seed(8)

        obj_number = len(self.game_config["final_config"])
        assert obj_number%2 == 0
        assert len(self.game_config["start_config"]["player1"])*2 == obj_number
        assert len(self.game_config["start_config"]["player2"])*2 == obj_number

        objects = random.sample(total_objects, obj_number)
        object_pos1 = random.sample([0,2,3,4,5,6,7,8],obj_number//2)
        object_pos2 = random.sample([0,2,3,4,5,6,7,8],obj_number//2)
        """
            Split the place into 9 sections.
            Randomly place objects in the sections
            +-----+-----+-----+
            |  0  |     |  2  |
            +-----+-----+-----+
            |  3  |  4  |  5  |
            +-----+-----+-----+
            |  6  |  7  |  8  |
            +-----+-----+-----+      
        """
        for i, obj in enumerate(objects):
            shape, rgb = obj
            if i in self.game_config["start_config"]["player1"]:
                owner = "player1"
                tmp = object_pos1.pop()
                tmp_x = tmp%3
                tmp_z = tmp//3
                pos_x = - 0.4 + (tmp_x*2+1)*0.82/6
                pos_z = - (tmp_z*2+1)*0.32/6 - 0.04              
            else:
                owner = "player2"
                tmp = object_pos2.pop()
                tmp_x = tmp%3
                tmp_z = tmp//3
                pos_x = - 0.4 + (tmp_x*2+1)*0.82/6
                pos_z = (tmp_z*2+1)*0.32/6 + 0.04
            delta_x = random.uniform(-0.82/6*0.55, 0.82/6*0.55)
            delta_z = random.uniform(-0.32/6*0.45, 0.32/6*0.45)
            pos = {
                    "x": self.table_top["x"] + pos_x + delta_x,
                    "y": self.table_top["y"],
                    "z": self.table_top["z"] + pos_z + delta_z
                }
            object_id = self.get_unique_id()
            self.object_info[i] = {"object_id":object_id ,"name": f"{rgb[0]} {shape[0]}", "owner":owner}
            commands.extend(self.get_add_physics_object(model_name=shape[1],
                                        library="models_core.json",
                                            position=pos,
                                            rotation={"x": 0, "y": random.randint(0,180), "z": 0},
                                            # mass=9999,
                                            bounciness=0,
                                            kinematic = True,
                                            # gravity = False,
                                            static_friction = 0,
                                            dynamic_friction = 0,
                                            object_id=object_id))
            if shape[0] == "Battery":
                scale = {"x": 2.1, "y": 2.1, "z": 2.1}
            elif shape[0] == "Ball":
                scale = {"x": 1.8, "y": 1.8, "z": 1.8}
            else:
                scale = {"x": 1.2, "y": 1.1, "z": 1.2}
            commands.extend([{"$type": "scale_object", "id": object_id, "scale_factor": scale}])
            commands.extend([{"$type": "set_color", "color": rgb[1], "id": object_id}])

        

def startMultiTDW(info):
    info["start"] = True
    c = MultiMagnebot(info=info, check_version=False, launch_build=True)
    c.run()