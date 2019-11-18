import socket, sys, select

from chatClasses import User, Room, Lobby, Server
import chatClasses

# get the host IP address and start listening for connections

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'  #if no argument, default to local host

s = Server()
s.run(hostAddr)
