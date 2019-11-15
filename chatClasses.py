import socket
import re

PORT = 55555
MAX_MESSAGE_LENGTH = 4096
MAX_CLIENTS = 15
SERVERSOCKETLIST = [] 

''' TO DO : make server its own class, with a hall, rooms and users 
 Decisions to make : How do we want to handle incorrect username setting first time logging in?
 class feed ? haven't decided where this should go.. 
 thinking its server side.. and server will handle outputting
 all room msgs to all its clients 

Server disconnecting from clients 
Client/Server "gracefully" handling crashes 

  Extra credit: PMs, File Transfer 
  
Have not implemented password 

class Server: 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def __init__ (self, host, port): 
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc 
	s.setblocking(False)  # turns off socket blocking
	s.bind(host, port)  # assigns host ip add and port to socket  
	# s.bind((socket.gethostname(), chatClasses.PORT)) # make it available to the outside world Test this w/ Erik Device ! 
	s.listen(MAX_CLIENTS) 
'''
# commands (only create once)
NAMECHANGE = "$name name [Changes username]\n" 
NEWROOM = "$Room roomname [Creates/Joins Room]\n"
COMMANDS = "All available commands:\n" + NAMECHANGE + NEWROOM

class User: 
	def __init__(self, socket, name): 
		socket.setblocking(0)  
		self.socket = socket 
		self.name = name
		self.rooms = [] # holds room names user is in 

	def setName(self, newName): 
		self.name = newName

	def fileno(self): 
		return self.socket.fileno()

	def getName(self): 
		return self.name
	
	def addRoom(self, room): 
		self.rooms.append(room) 

	def printRooms(self): 
		for x in self.rooms: 
			print(x.name)

	def leaveRoom(self, roomName): 
		self.rooms.remove(roomName)


class Room:
	def __init__(self, name, password=""):
		self.users = []   # a list of sockets
		self.name = name
		self.password = password 

	def addUser(self, user): 
		self.users.append(user) 

	def printUsers(self): 
		print("Users in room: " + self.name + " ") 
		for x in self.users: 
			print(x.getName() + ' ')

	def broadcast(self, msg): 
		for x in self.users: 
			x.socket.sendall(msg.encode())

	def removeUser(self, user):
		self.users.remove(user) 

class Lobby: 
	def __init__(self): 
		self.rooms = {}  # {room name : room} 

	def promptForName(self, user):
		user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?\n')

	def printRooms(self): 
		print("Rooms: ")
		for x in self.rooms.values(): 
			print(x.name + " ")

	def handle(self, user, msg): 
		msgLen = len(re.findall(r'\w+', msg)) # returns an int 
		msgArr = msg.split(" ")
		# print("msg length = " + str(msgLen)  
		if "$newuser" in msg or "$name" in msg: # cases: 1st time connecting: newuser, using $name 
			# parse name from msg 
			if msgLen == 2: # argument check 
				user.setName(msgArr[1])
				print("New user: " + user.getName())
				user.socket.sendall(b'Username setting successful! Type $commands for a command list\n')
			else: 
				user.socket.sendall(b'Username setting unsuccessful, please try again with the $changeName command\n')
		elif "$commands" in msg: 
			user.socket.sendall(COMMANDS.encode())
		elif "$room" in msg: # cases : no room, existing room, existing room and user is already in there 
			if msgLen == 2: # argument check 
				# See if there is an existing room 
				roomName = msgArr[1]
				print("Looking for room: " + roomName)
				if roomName in self.rooms: # trying to join an existing room
					print("check")
					room = self.rooms[roomName] 
					if user in room.users: # user is already in the room 
						user.socket.sendall(b"You're already in this room!")
					else:
						room.addUser(user)
						room.printUsers()
						user.addRoom(roomName)
						welcome = user.name +  ":has joined the room!\n"
						room.broadcast(welcome)
				else: # new room 
					newRoom = Room(roomName, user.getName()) 
					newRoom.addUser(user) 
					self.rooms[roomName] = newRoom
					user.addRoom(roomName)
					print("created a new room: " + roomName) 
					newRoom.printUsers()
			else: 
				user.socket.sendall(b'Room Join/Create failed. Try Again.')
		elif "$sendall" in msg: #broadcast to all current rooms 
			if msgLen > 1: 
				newMsg = msg[9:] + "\n"
				for currentRoom in user.rooms: 
					if currentRoom in self.rooms: 
						self.rooms[currentRoom].broadcast(newMsg)

				''' IN PROGRESS 
		elif "$leave" in msg: 
			if msgLen == 2: 
				roomName = msgArr[1] 
				if roomName in self.rooms: # found the room user is trying to leave
					room = self.rooms[roomName] # grab the room
					room.removeUser(user) # remove user from the room 
					user.leaveRoom(roomName) # remove room from the user 
					if len(room.users): #room is now empty, remove from rooms 
						self.rooms.pop(roomName) 
					user.printRooms()
					# self.printRooms()					
			else: 
				return # TODO 
				'''
		else: 
			if len(self.rooms) == 0: # no rooms
				user.socket.sendall(b'invalid command, try again')
			else: 
				return #TODO 
		


		# didn't issue a valid command 
		# else:  
			# if user is in a room , broadcast to room x


'''
Notes
Can we move msg length check to only do it once? 
commands: create/join room , broadcast to more than 1 room, disconnect 
list all rooms, leave room, joining multiple rooms 
For existing room check: make a function 
fuck it make functions for most of this shit : 
	add room to rooms 
	create room 
	turn these into f unctions  (sphaghetti)
'''