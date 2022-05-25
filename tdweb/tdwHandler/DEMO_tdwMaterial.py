'''
Demo for magnet robot in TDW
'''


from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
# from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from tdw.librarian import ModelLibrarian
from tdw.add_ons.object_manager import ObjectManager


import numpy as np
import numpy
import cv2

import time

# # show all the objects in TDW
# librarian = ModelLibrarian()
# for record in librarian.records:
#     print(record.name)


def startTDW():
    c = Controller(launch_build=False)
    camera1 = ThirdPersonCamera(position={"x": 0, "y": 3, "z": 0},
                            rotation={"x": 90, "y": 0, "z": 0},
                            field_of_view = 130,
                            avatar_id="a")
    c.add_ons.extend([camera1])

    print("Setting Up Scene...")
    '''Set up scene'''
    commands = [{"$type": "set_screen_size",
                    "width": 512,
                    "height": 512}]
    # commands.extend([{"$type": "set_render_quality", "render_quality": 5}])
    commands.extend([TDWUtils.create_empty_room(10, 10)])
    
    # "dining_room_table","quatre_dining_table","b05_table_new"
    # "table_square","willisau_varion_w3_table","chista_slice_of_teak_table"
    # ["plate05","plate06","plate07","b04_bowl_smooth","serving_bowl"]
    for i, n in enumerate(["dining_room_table","quatre_dining_table","b05_table_new"]):
        commands.extend(c.get_add_physics_object(model_name=n,
                                            library="models_core.json",
                                                position={"x": i*1.5, "y":0, "z": i*1.5},
                                                object_id=c.get_unique_id(),
                                                ))

    

    resp = c.communicate(commands)




def main():
    startTDW()

if __name__ == "__main__":
    main()