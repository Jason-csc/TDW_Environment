# TDWEB - TDW Web Interface for Interaction Collection
Simulated Environment for human-robot interaction using ThreeDWorld ([TDW](https://github.com/threedworld-mit/tdw)). On the Web Page:
- Players can control the robot from the first perspective
- Click objects listed to pick the item and place in the bowl
- Chat with partner for collaborative tasks

## Set up
Python tools and third party packages Installation: 
```bash
./bin/tdweb_install
```

* Make sure to activate virtual environment:  
```bash
source env/bin/activate
```

Database Management through: 
```bash
./bin/tdweb_db (create|destroy|reset|dump)
```


## Interactive Website
Open one terminal and run: 
```bash
./bin/tdweb_run
```

*Refer [Install TDW on a remote Linux server](https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/setup/install.md#install-tdw-on-a-remote-linux-server) and modify `DISPLAY` in `bin/tdweb_display`*. Open another terminal:
```bash
./bin/tdweb_display
```