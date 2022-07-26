import time


def startbot(info):
    # Dummy bot
    i = 0    
    while True:
        time.sleep(0.1)
        print("waiting", info["turn"])
        if not info["turn"]["playerTurn"]:
            print("=========State of Game=========")
            print("---------State of Objects---------")
            for object_id, value in info["objList"].items():
                print(f"Name: {value['name']}")
                print(f"Object_id in TDW: {object_id}")
                print(f"Status: {value['status']}")
                print(f"Game_id: {value['game_id']}")
                print(f"Pos: {value['position']}")

            print("---------State of Bowls for Player1---------")
            for pos1 in info["placePos1"][:2]:
                print(f"Name: {pos1['name']}")
                print(f"Pos: {pos1['pos']}")
                print(f"Bin_id: {pos1['bin_id']}")
            
            print("---------State of Bowls for Player2---------")
            for pos2 in info["placePos2"][:2]:
                print(f"Name: {pos2['name']}")
                print(f"Pos: {pos2['pos']}")
                print(f"Bin_id: {pos2['bin_id']}")
            
            print("---------State of SharePlace---------")
            for pos in info["placePos1"][2:]:
                print(f"Name: {pos['name']}")
                print(f"Pos: {pos['pos']}")
            
            # time.sleep(5)
            
            t = info["task"]["player2"][i]
            info["shareInfo"].append({"player":"bot", "info":t["task"]})
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

        
