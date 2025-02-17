import socket
import sys
import select
import userClass
import lobbyClass

PORT = 50000
MAX_CLIENTS = 15
MAX_MESSAGE_LENGTH = 4096

'''
from chatClasses import User, Room, Lobby
import chatClasses

# get the host IP address and start listening for connections

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'  #if no argument, default to local host
'''


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object s
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc
        self.socket.setblocking(False)  # turns off socket blocking
        self.socketList = []
        self.socketList.append(self.socket)
        self.socketList.append(sys.stdin)

        #self.socket.bind((hostAddr, chatClasses.PORT))  # assigns host ip add and port to socket

        # s.bind((socket.gethostname(), chatClasses.PORT)) # make it available to the outside world Test this w/ Erik Device !

        #s.listen(chatClasses.MAX_CLIENTS)

        # s = Server(hostAddr, chatClasses.PORT)

        #print("Server set up & listening! Connect with address: " , hostAddr)

        #chatClasses.SERVERSOCKETLIST.append(s)
        #lobby = Lobby()

    def addClient(self):
        newSocket, addr = self.socket.accept()
        newUser = userClass.User(newSocket, "")
        self.socketList.append(newUser)
        return newUser

    def run(self, ip):
        lobby = lobbyClass.Lobby()
        self.socket.bind((ip, PORT))  # assigns host ip add and port to socket
        self.socket.listen(MAX_CLIENTS)
        print("Server set up & listening! Connect with address: ", ip)

        while True:
            readables, writables, exceptionals = select.select(self.socketList, [], [])
            for notified_socket in readables:
                if notified_socket is self.socket:  # new connection
                    newUser = self.addClient()
                    lobby.promptForName(newUser)  # ERR
                elif notified_socket is sys.stdin:
                    command = sys.stdin.readline()
                    if command == 'quit\n':
                        lobby.disconnectFromClients()
                        del lobby
                        sys.exit(0)
                else:
                    try:
                        newMsg = notified_socket.socket.recv(MAX_MESSAGE_LENGTH)
                        print(newMsg.decode())
                        if newMsg:
                            print("sending msg to handler")
                            lobby.handle(notified_socket, newMsg.decode())
                        else:  # recv sent 0 bytes, closed connection
                            print("Closed a connection")
                            if notified_socket in lobby.users:
                                lobby.removeUser(notified_socket)
                            if notified_socket in self.socketList:
                                self.socketList.remove(notified_socket)
                    except:
                        if notified_socket in lobby.users:
                            lobby.removeUser(notified_socket)
                        notified_socket.socket.sendall(b'$$exit')
                        print("Connection to client has been broken")
                        if notified_socket in self.socketList:
                            self.socketList.remove(notified_socket)
