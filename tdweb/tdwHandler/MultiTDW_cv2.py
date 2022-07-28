import cv2
import numpy as np
from typing import List
import json
from collections import defaultdict
import random
import itertools
import threading
import time


from tdweb.tdwHandler.random_game_generator import generate_game


class Game:
    def __init__(self, info):
        self.info = info
        self.canvas = None
        self.pick_objid1 = None
        self.drop_binid1 = None
        self.pick_objid2 = None
        self.drop_binid2 = None
        self.bin_cpoints = {
            "A":(155,181), # 0: bin0
            "B":(869,181), # 1: bin1
            "C":(155,843), # 2: bin2
            "D":(869,843), # 3: bin3
            "E":(512,512), # 4: sharePlace
            "F":(512,843), # 5: player1
            "G":(512,181), # 6: player2
        }
        self.bin_colors = [
                ("Orange Bin", (209, 81, 45)), 
                ("Blue Bin", (129, 202, 207)),
                ("Black Bin", (10, 10, 10)),
                ("Green Bin", (95, 208, 104))
        ]
        self.object_shape = [ 'Circle', 'Rectangle']
        self.object_color = {
            "Red": (153, 0, 0),
            "Purple": (84, 22, 144),
            "Green": (43, 122, 11),
            "Yellow": (249, 217, 35),
        }
        
        self.game_config = json.loads(generate_game())
        self.intialObj()
        self.setPos()
        self.generateTask()
        
        self.info["prepared"] = True


    def generateTask(self):
        print(">>> Generating Game Tasks...")
        tasks = defaultdict(list)
        for player, knowledge_list in self.game_config["knowledge"].items():
            # shuffle the knowledge list
            random.shuffle(knowledge_list)
            for knowledge in knowledge_list:
                task = {}
                task["shared"] = False
                if knowledge[0] == "inBin":
                    obj_id, bin_id = knowledge[1:]
                    obj_name = self.info["objList"][obj_id]['name']
                    bin_name = self.info["placePos"][bin_id]['name']
                    task["task"] = f"{obj_name} should be placed to {bin_name}"
                    task["objects"] = [obj_name]
                    task["relation"] = bin_name
                elif knowledge[1] == "bin":
                    idf, _, obj1_id, obj2_id = knowledge
                    if not idf == "same":
                        idf = "different"
                    obj1_name = self.info["objList"][obj1_id]['name']
                    obj2_name = self.info["objList"][obj2_id]['name']
                    task["task"] = f"Place {obj1_name} and {obj2_name} should be placed in the {idf} bin"
                    task["objects"] = [obj1_name,obj2_name]
                    task["relation"] = f"{idf} bin"
                elif knowledge[0] in ["same", "opposite"]:
                    obj1_id, pos, obj2_id = knowledge[1:]
                    obj1_name = self.info["objList"][obj1_id]['name']
                    obj2_name = self.info["objList"][obj2_id]['name']
                    task["task"] = f"{obj1_name} and {obj2_name} should be placed in the bin with {knowledge[0]} {pos}"
                    task["objects"] = [obj1_name,obj2_name]
                    task["relation"] = f"{knowledge[0]} {pos}"
                else:
                    assert False, f"Wrong Game Knowledge: {knowledge}"
                tasks[player].append(task)
        self.info["task"] = tasks
    

    def intialObj(self):
        total_objects = list(itertools.product(self.object_shape, self.object_color))

        obj_number = len(self.game_config["final_config"])
        assert obj_number%2 == 0
        assert len(self.game_config["start_config"]["player1"])*2 == obj_number
        assert len(self.game_config["start_config"]["player2"])*2 == obj_number

        objects = random.sample(total_objects, obj_number)

        for obj_id, obj in enumerate(objects):
            shape, color = obj
            if obj_id in self.game_config["start_config"]["player1"]:
                owner = "player1"
                pos = "F"
            else:
                owner = "player2"
                pos = "G"
            object = {
                "pos": pos, 
                "name": f"{color} {shape}", 
                "owner": owner, 
                "obj_id": obj_id,
                "reachable1": owner == "player1",
                "reachable2": owner == "player2"
            }
            self.info["objList"][obj_id] = object


    def getObjCord(self, obj_id, pos):
        """Return the point based on obj_id and pos"""
        res = None
        center = self.bin_cpoints[pos]
        if pos == "E":
            row = obj_id//4
            column = obj_id%4
            res = (
                center[0] - 1024/8*3 + column*(1024/4),
                center[1] - 300/4 + row*(300/2)
            )
        else:
            row = obj_id//3
            column = obj_id%3
            if pos in ["F","G"]:
                res = (
                    center[0] - 399/3 + column*(300/3),
                    center[1] - 354/3 + row*(354/3)
                )
            else:
                res = (
                    center[0] - 300/3 + column*(300/3),
                    center[1] - 354/3 + row*(354/3)
                )
        return (int(res[0]),int(res[1]))


    def setPos(self):
        for color, bin_id in zip( self.bin_colors, ["A","B","C","D"]):
            cx, cy = self.bin_cpoints[bin_id]
            name, rgb = color
            self.info["placePos"][bin_id]  = {
                "bin_id": bin_id, 
                "name": name, 
                "player": "player1" if cy > 1024/2 else "player2"
            }
        self.info["placePos"]["E"]  = {
            "bin_id": "E", 
            "name": "sharePlace", 
            "player": "shared"
        }

    def drawBins(self):
        for color, bin_id in zip( self.bin_colors, ["A","B","C","D"]):
            cx, cy = self.bin_cpoints[bin_id]
            name, rgb = color
            start_point = (cx-130, cy-135)
            end_point = (cx+130, cy+135)
            thickness = -1
            self.canvas = cv2.rectangle(self.canvas, start_point, end_point, rgb, thickness)
            r,g,b = rgb
            thickness = 10
            self.canvas = cv2.rectangle(self.canvas, start_point, end_point, (r+30,g+30,b+30), thickness)


    def drawObj(self):
        radius = 30
        for obj in self.info["objList"].values():
            color, shape = obj["name"].split(' ')
            rgb = self.object_color[color]
            obj_id = obj["obj_id"]
            pos = obj["pos"]
            center_coordinates = self.getObjCord(obj_id,pos)
            if shape == "Circle":
                self.canvas = cv2.circle(self.canvas, center_coordinates, radius=radius, color=rgb, thickness=-1)
            else:
                cx, cy = center_coordinates
                start_point = (cx-radius, cy-radius)
                end_point = (cx+radius, cy+radius)
                self.canvas = cv2.rectangle(self.canvas, start_point, end_point, color=rgb, thickness=-1)


    def renderObj(self):
        while True:
            self.canvas = np.zeros((1024, 1024, 3), np.uint8)
            self.canvas[:] = 180
            self.canvas[362:662,:,:] = 200
            self.drawBins()
            self.drawObj()
            self.info["camera1"].append(self.canvas.copy())
            self.info["camera2"].append(cv2.flip(self.canvas.copy(), 0))
            time.sleep(0.1)

    

    def HandleCmd(self):
        while True:
            if len(self.info["cmds1"]) > 0:
                cmd = self.info["cmds1"].pop(0)
                if cmd["type"] == "pick":
                    self.pick_objid1 = cmd["args"]
                    self.info["status1"][0] = "Drop"
                else:
                    self.drop_binid1 = cmd["args"]
                    self.info["objList"][self.pick_objid1]["pos"] = self.drop_binid1
                    self.info["objList"][self.pick_objid1]["reachable1"] = self.drop_binid1 in ["E","C","D"]
                    self.info["objList"][self.pick_objid1]["reachable2"] = self.drop_binid1 in ["E","A","B"]
                    self.info["status1"][0] = "PICK"
            if len(self.info["cmds2"]) > 0:
                cmd = self.info["cmds2"].pop(0)
                if cmd["type"] == "pick":
                    self.pick_objid2 = cmd["args"]
                    self.info["status2"][0] = "Drop"
                else:
                    self.drop_binid2 = cmd["args"]
                    self.info["objList"][self.pick_objid2]["pos"] = self.drop_binid2
                    self.info["objList"][self.pick_objid2]["reachable1"] = self.drop_binid2 in ["E","C","D"]
                    self.info["objList"][self.pick_objid2]["reachable2"] = self.drop_binid2 in ["E","A","B"]
                    self.info["status2"][0] = "PICK"
            time.sleep(0.1)


    
    def run(self):
        thread1 = threading.Thread(target=self.renderObj,args=())
        thread1.start()
        thread2 = threading.Thread(target=self.HandleCmd,args=())
        thread2.start()



    


def startGame(info):
    info["start"] = True
    c = Game(info=info)
    c.run()