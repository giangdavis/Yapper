import socket, sys, select

from chatClasses import User, Room, Lobby, Server
import chatClasses

# get the host IP address and start listening for connections

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'  #if no argument, default to local host

'''s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object s
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc 
s.setblocking(False)  # turns off socket blocking
s.bind((hostAddr, chatClasses.PORT))  # assigns host ip add and port to socket
# s.bind((socket.gethostname(), chatClasses.PORT)) # make it available to the outside world Test this w/ Erik Device !
s.listen(chatClasses.MAX_CLIENTS)'''
s = Server(hostAddr)

print("Server set up & listening! Connect with address: " , hostAddr)

chatClasses.SERVERSOCKETLIST.append(s.getSocket())
lobby = Lobby()

while True:
    readables, writables, exceptionals = select.select(chatClasses.SERVERSOCKETLIST, [], [])
    for notified_socket in readables:
        if notified_socket is s.getSocket():  # new connection
            newSocket, addr = notified_socket.accept()
            newUser = User(newSocket, "")
            # newUser.fileno()
            chatClasses.SERVERSOCKETLIST.append(newUser)
            # clients.append(newUser)
            lobby.promptForName(newUser)
        else:
            try:
                newMsg = notified_socket.socket.recv(chatClasses.MAX_MESSAGE_LENGTH)
                print(newMsg.decode())
                if newMsg:
                    print("sending msg to handler")
                    lobby.handle(notified_socket, newMsg.decode().lower())
                else: # recv sent 0 bytes, closed connection
                    print("Closed a connection")
                    if notified_socket in chatClasses.SERVERSOCKETLIST:
                        chatClasses.SERVERSOCKETLIST.remove(notified_socket)
            except:
                print("Connection to client has been broken")
                chatClasses.SERVERSOCKETLIST.remove(notified_socket)