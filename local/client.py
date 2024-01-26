from time import sleep
import socket
import os


PORT = 8080
BUFFER = 1024
LOCAL_FOLDER = os.getcwd() # the folder where the files are stored on the client machine (remote), current folder in this case
SLEEP_TIME = 5 # seconds





def sendFile(s, file):
    with open(file, 'rb') as f:
        data = f.read(BUFFER)
        while data:            
            print(data) 
            s.sendall(data)
            if s.recv(BUFFER).decode() != 'OK':
                print("Error:", s.recv(BUFFER).decode())
                break
            data = f.read(BUFFER)
    s.sendall("EOF".encode())
    message = s.recv(BUFFER).decode()
    if message == 'received':
        print("File", file, "sent")
    else:  
        print("Error:", message)

def synchroniseFiles(s, folder):
    # send the list of files in the folder
    files = os.listdir(folder)
    for file in files:
        print("File:", file)
        if file == 'client.py':
            continue
        s.sendall(file.encode())
        response = s.recv(BUFFER).decode()
        if response == 'not found':
            sendFile(s, file)
        elif response == 'found':
            continue
        else:
            print("Error:", response)
            break
    s.sendall('EOL'.encode())










# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET: IPv4, SOCK_STREAM: TCP
# connect to the server
s.connect(('localhost', PORT))
if s is not None:
    print('Connected to', s.getpeername())

while s is not None:
    synchroniseFiles(s, LOCAL_FOLDER)
    print('Waiting', SLEEP_TIME, 'seconds...')
    sleep(SLEEP_TIME)

# close the socket
s.close()
