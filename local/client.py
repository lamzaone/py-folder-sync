import time
from time import sleep
import socket
import os


PORT = 8080     # the port number on which the server is listening
BUFFER = 1024   # the size of the buffer (1 KB)
LOCAL_FOLDER = os.path.dirname(os.path.abspath(__file__))   # the folder where the files are stored on the server machine (remote) 
SLEEP_TIME = 5  # seconds



def removeDeletedFiles(s):
    with open( os.path.join(LOCAL_FOLDER, "logs.txt"), "a") as f:
        while True:
            message = s.recv(BUFFER).decode()
            if message == 'EOL':
                break
            f.write(f"[{time.time()}] Deleted file: {message}\n")
            s.sendall('received'.encode())

def sendFile(s, file):

    with open(os.path.join(LOCAL_FOLDER, file), 'rb') as f:  # open the file in binary reading mode
        data = f.read(BUFFER)    # read the first BUFFER sized chunk of data
        while data:     # loop to read the rest of the data and send it 
            s.sendall(data)     # send the data
            if s.recv(BUFFER).decode() != 'OK':      # wait for a confirmation message from the server, to make sure that the data is received
                print("Error:", s.recv(BUFFER).decode())    # if the confirmation message is not received, print the error message
                break 
            data = f.read(BUFFER)   #  read the next chunk of data, f.read() returns an empty string after reading the whole file
    s.sendall("EOF".encode())       # send a message to the server to let it know that the end of the file is reached
    message = s.recv(BUFFER).decode()       # wait for a confirmation message from the server, to make sure that the file is received
    if message == 'received':
        print("File", file, "sent")
    elif message == 'not-received':
        sendFile(s, file)
        print("Error:", "File", file, "is not received completely")
        print("Resending the file...")
    else:  
        print("Error:", message)

def synchroniseFiles(s, folder):

    #TODO: access subfolders and send files recursilvely
    
    # send the list of files in the folder
    files = os.listdir(folder)      # get the list of files in the folder
    with open(os.path.join(LOCAL_FOLDER, "logs.txt"), "a") as f:    # open the logs file in append mode
        for file in files:
            if file == 'client.py' or file == "logs.txt":     # skip this file
                continue                # skip the rest of the code in the loop and go to the next iteration
            modified_time = os.path.getmtime(os.path.join(folder, file)) # getmtime() returns the time of last modification of the file
            file_size = os.path.getsize(os.path.join(folder, file)) # getsize() returns the size of the file in bytes
            s.sendall(f"{file};{modified_time};{file_size}".encode())        # send the name of the file in filename;modified_time format
            response = s.recv(BUFFER).decode()      # wait for a response from the server
            if response == 'not found':
                f.write(f"[{modified_time}] New file: {file}\n")
                sendFile(s, file)       # send the file
            elif response == 'outdated':     # if the file is not found on the server, send it
                f.write(f"[{modified_time}] Updated file: {file}\n")
                sendFile(s, file)       # send the file
            elif response == 'found':       # if the file is found on the server, skip it
                continue
            else:
                print("Error:", response)
                break
        s.sendall('EOL'.encode())      # send a message to the server to let it know that the end of the list is reached
    f.close()       # close the logs file





def connect(try_number = 1):
    global s
    try:
        s.connect(('localhost', PORT)) # connect to the server
        if s is not None: # if the connection is successful, print the address of the server
            print('Connected to', s.getpeername()) # getpeername() returns the address of the remote endpoint
    except ConnectionRefusedError: # if the connection is refused, try again
        if try_number > 5: # if the connection is refused 5 times, exit the application
            print("Connection failed, closing application...")
            exit()
        print(f"[{try_number}/5] Connection refused, trying again...") # print the number of tries
        connect(try_number + 1) # try again and increment the number of tries




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET: IPv4, SOCK_STREAM: TCP

def main():
    global s
    connect() # connect to the server using the connect() function defined above

    try:
        while True:
            synchroniseFiles(s, LOCAL_FOLDER)
            removeDeletedFiles(s)
            print('Waiting', SLEEP_TIME, 'seconds...')
            sleep(SLEEP_TIME)
    except ConnectionAbortedError:
        print("Connection aborted")
    except ConnectionResetError:
        print("Connection reset")
        connect()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
    except Exception as e:
        print("Error:", e)
        exit()

    print("Closing connection...")
    s.close()


if __name__ == "__main__":
    main()
