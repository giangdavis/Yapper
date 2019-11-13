import socket, sys, select

from chatClasses import User, Room, Lobby
import chatClasses

# get the host IP address and start listening for connections

arguments = len(sys.argv) - 1 
if arguments == 1: 
	hostAddr = sys.argv[1]
else: 
	hostAddr = '127.0.0.1'  #if no argument, default to local host 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object s 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc 
s.setblocking(False)  # turns off socket blocking
s.bind((hostAddr, chatClasses.PORT))  # assigns host ip add and port to socket  
# s.bind((socket.gethostname(), chatClasses.PORT)) # make it available to the outside world Test this w/ Erik Device ! 
s.listen(chatClasses.MAX_CLIENTS) 
# s = Server(hostAddr, chatClasses.PORT)

print("Server set up & listening! Connect with address: " , hostAddr)

chatClasses.SERVERSOCKETLIST.append(s) 

lobby = Lobby() 

while 1:  
	readables, writables, exceptionals = select.select(chatClasses.SERVERSOCKETLIST, [], [])
	for socket in readables:
		if socket is s:  # if theres info coming from the host server, its a new socket trying to connect.. 
			newSocket, addr = socket.accept()
			newUser = User(newSocket, "")
			# newUser.fileno()
			chatClasses.SERVERSOCKETLIST.append(newSocket)
			# clients.append(newUser)
			lobby.promptForName(newUser)

# message handling not work ing ! 
		else: 
			try: 
				newMsg = socket.recv(chatClasses.MAX_MESSAGE_LENGTH)
				if newMsg: 
					lobby.handle(socket, newMsg) 
				else: # recv sent 0 bytes, closed connection 
					if socket in chatClasses.SERVERSOCKETLIST: 
						socket.close()
						chatClasses.SERVERSOCKETLIST.remove(socket)

				# broken connection 
				print("connection to client is broken")
				socket.close() 
				chatClasses.SERVERSOCKETLIST.remove(socket)
			except: 
				print("connection to client is broken")
				socket.close() 
				chatClasses.SERVERSOCKETLIST.remove(socket)






