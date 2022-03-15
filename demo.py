'''
Demo for magnet robot in TDW
'''


from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from magnebot import Magnebot, ActionStatus, Arm
from tdw.librarian import ModelLibrarian


# # show all the objects in TDW
# librarian = ModelLibrarian()
# for record in librarian.records:
#     print(record.name)


c = Controller()
magnebot = Magnebot(position={"x": 0, "y": 0, "z": -1.7}, rotation={"x": 0, "y": 0, "z": 0})
# Create a camera and enable image capture.
camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": -1.6},
                           rotation={"x": 30, "y": 0, "z": 0},
                           field_of_view = 100,
                           avatar_id="a")
# path: directory to store images
path = "image_dir"
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Note the order of add-ons. The Magnebot must be added first so that the camera can look at it.
c.add_ons.extend([magnebot, camera, capture])
# c.add_ons.extend([magnebot])


'''Set up scene'''
commands = [{"$type": "set_screen_size",
                "width": 1024,
                "height": 1024}]
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
                                        static_friction = 1,
                                        object_id=bowl_id,
                                        ))

apple_id = c.get_unique_id()
commands.extend(c.get_add_physics_object(model_name='apple',
                                     library="models_core.json",
                                        position={"x": 0.2, "y": 0.8682562, "z": -1.1},
                                        bounciness=0,
                                        object_id=apple_id))


commands.extend(c.get_add_physics_object(model_name='b04_banana',
                                     library="models_core.json",
                                        position={"x": 0.1, "y": 0.8682562, "z": -0.7},
                                        object_id=c.get_unique_id()))

resp = c.communicate(commands)



'''Control the robot by pick/drop'''
while True:
    cmd = input("input command: ")
    if cmd == "pick":
        magnebot.grasp(apple_id,Arm.right)
        while magnebot.action.status == ActionStatus.ongoing:
            c.communicate([])
        c.communicate([])
        print(magnebot.action.status)
        magnebot.reach_for(target={"x": 0.1, "y": 1.3, "z": -1}, arm=Arm.right)
        while magnebot.action.status == ActionStatus.ongoing:
            c.communicate([])
        c.communicate([])
        print(magnebot.action.status)
    elif cmd == "drop":
        magnebot.reach_for(target={"x": -0.23, "y": 1.3, "z": -1}, arm=Arm.right)
        while magnebot.action.status == ActionStatus.ongoing:
            c.communicate([])
        c.communicate([])
        magnebot.drop(apple_id,Arm.right)
        while magnebot.action.status == ActionStatus.ongoing:
            c.communicate([])
        c.communicate([])
        print(magnebot.action.status)
        magnebot.reach_for(target={"x": 0, "y": 1, "z": -1}, arm=Arm.right)
        while magnebot.action.status == ActionStatus.ongoing:
            c.communicate([])
        c.communicate([])
        print(magnebot.action.status)

    else:
        c.communicate({"$type": "terminate"})
        break


