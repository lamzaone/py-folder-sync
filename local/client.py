from time import sleep
import socket
import os


PORT = 8080     # the port number on which the server is listening
BUFFER = 1024   # the size of the buffer (1 KB)
LOCAL_FOLDER = os.path.dirname(os.path.abspath(__file__))   # the folder where the files are stored on the server machine (remote) 
SLEEP_TIME = 5  # seconds





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
    else:  
        print("Error:", message)

def synchroniseFiles(s, folder):
    # send the list of files in the folder
    files = os.listdir(folder)      # get the list of files in the folder
    for file in files:
        print("File:", file)
        if file == 'client.py':     # skip this file
            continue                # skip the rest of the code in the loop and go to the next iteration
        s.sendall(file.encode())        # send the name of the file
        response = s.recv(BUFFER).decode()      # wait for a response from the server
        if response == 'not found':     # if the file is not found on the server, send it
            sendFile(s, file)
        elif response == 'found':       # if the file is found on the server, skip it
            continue
        else:
            print("Error:", response)
            break
    s.sendall('EOL'.encode())      # send a message to the server to let it know that the end of the list is reached





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
