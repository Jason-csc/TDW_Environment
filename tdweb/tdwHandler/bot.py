import time


def startbot(info):
    # Dummy bot
    i = 0    
    while True:
        if not info["turn"]["playerTurn"]:
            print("=========State of Game=========")
            print("---------State of Objects---------")
            for obj_id, value in info["objList"].items():
                print(f"Name: {value['name']}")
                print(f"Obj_id: {obj_id}")
                print(f"Pos: {value['pos']}")

            print("---------State of Places---------")
            for pos1, value in info["placePos"].items():
                print(f"Name: {value['name']}")
                print(f"Owner: {value['player']}")
                print(f"Bin_id: {value['bin_id']}")
            
            
            time.sleep(2)
            
            t = info["task"]["player2"][i].copy()
            t["player"] = "bot"
            info["shareInfo"].append(t)
            i+=1
            
            """
            Give turn to player after actions      
            """
            info["turn"]["canPick"] = True
            info["turn"]["canDrop"] = True
            info["turn"]["canShare"] = True
            info["turn"]["playerTurn"] = True

        """
        Command Usage:
        Pick: info["cmds2"].append(
            {"player":"player2", "cmd":"pick", "args": [object_id, x, y, z]}
            )
        Drop: info["cmds2"].append(
            {"player":"player2", "cmd":"drop", "args": [pos, name]}
            )
        Share Task:
            for t in info["task"]["player2"]:
                info["shareInfo"].append({"player":"bot", "info":t["task"]})
        """

        
