import socket
import select
import sys
from chatClasses import User, Room, Lobby
import chatClasses

if len(sys.argv) < 2:
    print("Run as follows: python3 chatClient.py hostname (where hostname is an IP)")
    exit()
else:
    serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverConnection.connect((sys.argv[1], chatClasses.PORT))

connectionList = [sys.stdin, serverConnection]
first = False
while 1:
    readables, _, _ = select.select(connectionList, [], [])
    for notified_socket in readables:
        if notified_socket is serverConnection: # new msg
            msg = notified_socket.recv(chatClasses.MAX_MESSAGE_LENGTH)
            check = msg.decode()
            if msg: #incoming message
                if check == "$exit":
                    sys.stdout.write("Successfully disconnected to server.")
                    sys.exit(2)
                elif "You have successfully connected to the Lobby!!! What is your name?" in check:
                    print("condition met!")
                    first = True
                sys.stdout.write(msg.decode())
                sys.stdout.flush()
            else: # msg contained 0 bytes, disconnected
                print ('Connection closed!')
                serverConnection.close()
                sys.exit()

        else: # send a message from client
            if first == True:
                newMsg = "$newuser " + sys.stdin.readline()
                first = False
            else:
                newMsg = sys.stdin.readline()
            serverConnection.sendall(newMsg.encode())
            sys.stdout.flush()
        #if the client socket is readable, sending a msg. broadcast
        #to other clients.