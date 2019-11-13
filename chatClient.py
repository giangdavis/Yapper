import socket 
import select
import sys
from chatClasses import User, Room, Lobby
import chatClasses

MAX_MESSAGE_LENGTH = 4096

if len(sys.argv) < 2:
    print("Run as follows: python3 chatClient.py hostname where hostname is an IP", file=sys.stderr)
else:
    serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverConnection.connect(sys.argv[1], chatClasses.PORT)
   
   
   ''' 
while True:
    readables, _, exceptionals = 
    '''