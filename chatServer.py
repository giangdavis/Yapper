import socket, sys, select

from classes.py import User, Room, Lobby
import classes.py

PORT = 54543 
MAXCLIENTS = 25 
READBUFFERSIZE = 4096

# get the host IP address and start listening for connections

arguments = len(sys.argv) - 1 
if arguments == 1: 
	hostAddr = sys.argv[1]
else: 
	hostAddr = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc 
s.setblocking(0)  # turns off socket blocking
s.bind((hostAddr, PORT))  # assigns host ip add and port to socket  
s.listen(MAXCLIENTS)  

print("Server set up & listening! Connect with address: " , hostAddr)

connectionList = [s]  # create a list of users, starting w/ host 

while True:  # always listening for connections & messages 
	readables, writables, exceptionals = select.select(connectionList, [], []) 
	for user in readables:  # loop through users 
		if user is s:  # if user is a socket, new connection
			newSocket, addr = user.accept()
			newUser = User(newSocket, "")
			connectionList.append(newUser)

		else:  # new messages 
			newMsg = user.socket.recv(READBUFFERSIZE) 
			if newMsg == 0 :  # message contents are empty 
				user.socket.close() 
				connection_list.remove(user)
			else:
				processMsg(user, msg.decode().lower())  #send to process 
	
	for user in errorUsers:  #error sockets 
		user.close()
		connectionList.remove(user)


def processMsg(User, msg) {

}