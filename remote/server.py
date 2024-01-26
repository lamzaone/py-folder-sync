import socket
import os
from time import sleep

PORT = 8080
BUFFER = 1024
REMOTE_FOLDER = os.getcwd() # the folder where the files are stored on the server machine (remote), current folder in this case 
SLEEP_TIME = 5 # seconds


def recieveFile(client_socket, file):
    with open(file, 'wb') as f: 
        data = client_socket.recv(BUFFER)
        while data:
            print(data)
            if data.decode() == "EOF":
                break
            f.write(data)
            client_socket.sendall('OK'.encode())
            data = client_socket.recv(BUFFER)
    print("File", file, "recieved")
    client_socket.sendall('received'.encode())


def synchroniseFiles(client_socket, folder):
    while True:
        file = client_socket.recv(BUFFER).decode()
        if file == 'EOL':
            break
        print("File:", file)
        if file not in os.listdir(folder):
            client_socket.sendall('not found'.encode())
            recieveFile(client_socket, file)
            continue
        else:
            client_socket.sendall('found'.encode())







s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET: IPv4, SOCK_STREAM: TCP
s.bind(('', PORT)) # '' means all available interfaces on the host machine (server)
s.listen(5) # 5 is the maximum number of queued connections
client_socket, client_address = s.accept()
print('Connected to', client_address)

while client_socket:
    synchroniseFiles(client_socket, REMOTE_FOLDER)
    print("Waiting for" , SLEEP_TIME, "seconds...")
    sleep(SLEEP_TIME)  

s.close()
