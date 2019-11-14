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

print("Succesfully connected to the lobby!")

connectionList = [sys.stdin, serverConnection] 

while 1:
    readables, _, _ = select.select(connectionList, [], []) 
    for socket in readables: 
        if socket is serverConnection: # new msg 
            msg = socket.recv(chatClasses.MAX_MESSAGE_LENGTH) 
            if msg: #incoming message
                sys.stdout.write(msg.decode()) 
                sys.stdout.flush() 
            else: # msg contained 0 bytes, disconnected
                print ('Connection closed!') 
                serverConnection.close() 
                sys.exit() 

        else: # send a message from client 
            print("sending mesage now")
            newMsg = sys.stdin.readline() 
            serverConnection.sendall(newMsg.encode()) 
            sys.stdout.flush() 
			#if the client socket is readable, sending a msg. broadcast
			#to other clients. 