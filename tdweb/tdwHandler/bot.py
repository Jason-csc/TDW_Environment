import time


def startbot(info):
    # Dummy bot
    time.sleep(20)
    for t in info["task"]["player2"]:
        info["shareInfo"].append({"player":"bot", "info":t})
        print("=========add task by bot==========")
        print(t)
        time.sleep(20)