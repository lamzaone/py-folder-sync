import socket
import os
import time

PORT = 8080
BUFFER = 1024
REMOTE_FOLDER = os.path.dirname(os.path.abspath(__file__)) # the folder where the files are stored on the server machine (remote) 
SLEEP_TIME = 5 # seconds

def removeDeletedFiles(folder, clientFiles, client_socket):
    for file in os.listdir(folder):
        if file == os.path.basename(__file__): # skip the current file
            continue
        if file not in clientFiles: 
            os.remove(os.path.join(folder, file))
            client_socket.sendall(file.encode())
            confirmation = client_socket.recv(BUFFER).decode()
            if confirmation != 'received':
                print("Error:", confirmation)
    client_socket.sendall('EOL'.encode()) # send a message to the client to let it know that the end of the list is reached
            

def recieveFile(client_socket, file, file_size):
    #TODO: receive the filesize before receiving the file to make sure that the file is received completely after EOF.
    #      send a confirmation message to the client to make sure that the file is received completely after EOF.
    
    with open(os.path.join(REMOTE_FOLDER, file), 'wb') as f: # open the file in binary writing mode
        data = client_socket.recv(BUFFER) # receive the first chunk of data
        while data: # loop to write in file and receive the rest of the data
            if data.decode() == "EOF": # if the end of the file is reached, break
                break 
            f.write(data) # write the data to the file
            client_socket.sendall('OK'.encode()) # send a confirmation message to the client
            data = client_socket.recv(BUFFER) # receive the next chunk of data

    if os.path.getsize(os.path.join(REMOTE_FOLDER, file)) == int(file_size): # check if the file is received completely
        print("File", file, "received completely")
        client_socket.sendall('received'.encode()) # send a confirmation message to the client
    else:
        print("Error:", "File", file, "is not received completely")
        client_socket.sendall('not-received'.encode()) # send an error message to the client



def synchroniseFiles(client_socket, folder):
    global clientFiles
    clientFiles = []
    while True:
        message = client_socket.recv(BUFFER).decode() # receive the name of the file
        try:
            file, modified_time, file_size = message.split(';')
        except:
            break
        print("File:", file) # print the name of the file
        if file not in os.listdir(folder): # check if the file is not in the folder
            client_socket.sendall('not found'.encode()) # send a message to the client to let it know that the file is not found on the server, so it should send it
            recieveFile(client_socket, file, file_size) # receive the file
        else:
            if os.path.getmtime(os.path.join(folder, file)) < float(modified_time): # check if the file is modified
                print("File", file, "is modified", time.ctime(os.path.getmtime(os.path.join(folder, file))), "vs", time.ctime(float(modified_time)))
                client_socket.sendall('outdated'.encode())
                recieveFile(client_socket, file)
            else:
                client_socket.sendall('found'.encode()) # send a message to the client to let it know that the file is found on the server, so it should not send it
        clientFiles.append(file)






clientFiles = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET: IPv4, SOCK_STREAM: TCP
def main():
    global s    


    try:
        s.bind(('', PORT)) # '' means all available interfaces on the host machine (server)
        s.listen(5) # 5 is the maximum number of queued connections
        client_socket, client_address = s.accept()
        print('Connected to', client_address)
        while client_socket:
            synchroniseFiles(client_socket, REMOTE_FOLDER)
            removeDeletedFiles(REMOTE_FOLDER, clientFiles, client_socket)
            print("Waiting for" , SLEEP_TIME, "seconds...")
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("Closing the connection...")
        client_socket.close()
        exit()
    except Exception as e:
        print("Error:", e)
        exit()

    s.close()

if __name__ == "__main__": 
    main()