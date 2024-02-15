# Python remote folder sync
A simple python client-server directory synchronization app using sockets.
The app synchronizes the files from the local directory (  client.py location ) to the remote directory ( server.py location ), uploading, updating and removing files automatically and logging each action taken.

Made this as a cross platform alternative for https://github.com/lamzaone/cpp-folder-sync which only works on UNIX based systems.


HOW TO USE?:
- Clone the repository
- Place client.py and sever.py anywhere on your disk (separate locations) or on separate devices connected on LAN
- run both of them at the same time using the following commands
  ```bash
  python3 client.py
  python3 server.py
  ```


TODOs:
- ~~Update existing files~~
- ~~Delete files~~
- ~~Implement changelog.txt~~
- Sync subfolders
