# from tdw.controller import Controller
# from tdw.tdw_utils import TDWUtils
# from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from magnebot import Magnebot, ActionStatus
# import threading

# from enum import Enum
# from typing import List, Dict
# import numpy as np
# from tdw.controller import Controller
# from tdw.tdw_utils import TDWUtils
# from tdw.add_ons.object_manager import ObjectManager
# from tdw.add_ons.step_physics import StepPhysics
# from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.output_data import OutputData, Transforms, Robot
# from magnebot import Magnebot, Arm, ImageFrequency, ActionStatus

# c = Controller(launch_build=False)
# # Create a camera.
# camera = ThirdPersonCamera(position={"x": 2, "y": 6, "z": -1.5},
#                            look_at={"x": 0, "y": 0.5, "z": 0},
#                            avatar_id="a")
# # Add two Magnebots.
# # magnebot_0 = Magnebot(position={"x": -2, "y": 0, "z": 0},
# #                       robot_id=c.get_unique_id())
# # magnebot_1 = Magnebot(position={"x": 2, "y": 0, "z": 0},
# #                       robot_id=c.get_unique_id())
# class Navigator(Magnebot):
#     def __init__(self, robot_id = 0, position  = None):
#         # We're not using images in this simulation.
#         super().__init__(robot_id=robot_id, position=position, image_frequency=ImageFrequency.never)
#         # This will be set within self.update()
#         # If True, the Magnebot is done and won't update its state.
#         self.done: bool = False
#         self.state = 0
#         self.id = robot_id

#     def on_send(self, resp: List[bytes]) -> None:
#         super().on_send(resp=resp)
#         if self.done:
#             return
#         if self.state == 0:
#             self.move_by(2)
#             while self.action.status == ActionStatus.ongoing:
#                 c.communicate([])
#                 print("a",self.id,self.action.status)
#             c.communicate([])
#             self.state = 1
#         elif self.state == 1:
#             self.move_by(-2)
#             while self.action.status == ActionStatus.ongoing:
#                 c.communicate([])
#                 print("b",self.id,self.action.status)
#             c.communicate([])
#             self.done = True

        
        
#         # while self.action.status == ActionStatus.ongoing:
#         #     c.communicate([])
#         # c.communicate([])
        

# magnebot_0 = Navigator(c.get_unique_id(),position={"x": -2, "y": 0, "z": 0})
# magnebot_1 = Navigator(c.get_unique_id(),position={"x": 2, "y": 0, "z": 0})


# c.add_ons.extend([camera, magnebot_0, magnebot_1])
# # Load the scene.
# c.communicate([{"$type": "load_scene",
#                 "scene_name": "ProcGenScene"},
#                TDWUtils.create_empty_room(12, 12)])
# # Move the Magnebots.






# # thread = threading.Thread(target=move,args=(magnebot_0,-2,))
# # thread.start()


# # thread = threading.Thread(target=move,args=(magnebot_1,4,))
# # thread.start()

# # magnebot_0.move_by(-2)
# # magnebot_1.move_by(4)
# # while magnebot_0.action.status == ActionStatus.ongoing:
# #     c.communicate([])
# # c.communicate([])

# while not magnebot_0.done or not magnebot_1.done:
#     c.communicate([])
# c.communicate({"$type": "terminate"})






from enum import Enum
from typing import List, Dict
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.step_physics import StepPhysics
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.output_data import OutputData, Transforms, Robot
from magnebot import Magnebot, Arm, ImageFrequency, ActionStatus



xs1 = [1]
xs2 = [0.5]



class Navigator(Magnebot):
    """
    This is a sub-class of Magnebot that uses "state machines" for basic navigation.
    The state machine flags are evaluated per frame via `on_send(resp)`.
    Note that this is a VERY primitive navigation system!
    Image capture has been totally disabled.
    The Magnebots rely on scene-state data to navigate.
    """

    ORIGIN: np.array = np.array([0, 0, 0])

    def __init__(self, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,xs = []):
        # We're not using images in this simulation.
        super().__init__(robot_id=robot_id, position=position, rotation=rotation, image_frequency=ImageFrequency.never)
        # This will be set within self.update()
        
        self.done: bool = False
        self.state = -1
        self.id = robot_id
        self.xs = xs
        self.x = None

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        if self.state == -1 and len(self.xs) > 0:
            self.x = self.xs.pop(0)
            print("NOW ",self.id,self.x)
            self.move_by(self.x)
            self.state = 0
        elif self.state == 0 and self.action.done:
            self.move_by(-self.x)
            self.state = 1
        elif self.state == 1 and self.action.done:
            self.state = -1


class MultiMagnebot(Controller):
    """
    This is a basic example of a multi-agent Magnebot simulation.
    In the scene, there are two Mangebots and two objects.
    Each Magnebot needs to go to an object, pick it up, and bring it to the center of the room.
    Magnebot agents are handled in a new class, "Navigator", which navigates using a basic state machine system.
    This is commonly used in video games to yield basic agent behavior.
    It is inflexible and unsophisticated; robust Magnebot AI requires true navigation planning.
    This controller isn't an example of how to train multiple Magnebot agents.
    Rather, it's an example of how to structure your controller code for a multi-agent Magnebot simulation.
    """

    TARGET_OBJECTS: List[str] = ["vase_02", "jug04", "jug05"]

    def __init__(self, xs1,xs2,port: int = 1071, check_version: bool = True, launch_build: bool = False, random_seed: int = 0):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        global RNG
        RNG = np.random.RandomState(random_seed)

        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the objects.
        commands.extend(self.get_add_physics_object(model_name=RNG.choice(self.TARGET_OBJECTS),
                                                    position={"x": RNG.uniform(-0.2, 0.2), "y": 0, "z": RNG.uniform(-3, -3.3)},
                                                    rotation={"x": 0, "y": RNG.uniform(-360, 360), "z": 0},
                                                    object_id=self.get_unique_id()))
        commands.extend(self.get_add_physics_object(model_name=RNG.choice(self.TARGET_OBJECTS),
                                                    position={"x": RNG.uniform(-0.2, 0.2), "y": 0, "z": RNG.uniform(3, 3.3)},
                                                    rotation={"x": 0, "y": RNG.uniform(-360, 360), "z": 0},
                                                    object_id=self.get_unique_id()))
        # Add an object manager.
        self.object_manager: ObjectManager = ObjectManager()
        # Skip physics frames.
        step_physics: StepPhysics = StepPhysics(num_frames=10)
        # Add the Magnebots.
        self.m0: Navigator = Navigator(position={"x": 0, "y": 0, "z": -1.5},
                                       robot_id=0,
                                       xs=xs1)
        self.m1: Navigator = Navigator(position={"x": 0, "y": 0, "z": 1},
                                       rotation={"x": 0, "y": 180, "z": 0},
                                       robot_id=1,
                                       xs=xs2)
        # Add a camera.
        camera: ThirdPersonCamera = ThirdPersonCamera(position={"x": -2, "y": 9, "z": -6},
                                                      avatar_id="a",
                                                      look_at=self.m1.robot_id)
        self.add_ons.extend([self.object_manager, step_physics, self.m0, self.m1, camera])
        self.communicate(commands)


    def run(self) -> None:
        """
        Iterate through the simulation until the Magnebots are done.
        """

        while True:
            self.communicate([])
            time.sleep(0.1)
        self.communicate({"$type": "terminate"})


def f(xs1,xs2):
    c = MultiMagnebot(xs1=xs1,xs2=xs2)
    c.run()



import threading
thread = threading.Thread(target=f,args=(xs1,xs2,))
thread.start()


import random
import time

def f1():
    while True:
        xs1.append(random.choice((1,2,1.5)))
        time.sleep(0.1)


def f2():
    while True:
        xs2.append(random.choice((0.5,0.7,0.2)))
        time.sleep(0.1)


thread1 = threading.Thread(target=f1,args=())
thread1.start()

thread2 = threading.Thread(target=f2,args=())
thread2.start()

