# structure starting w/ 3 tiers. lobby > rooms > users 

import socket 

class User: 
	def __init__(self, socket, name): 
		socket.setblock(0)  # turn off blocking
		self.socket = socket 
		self.name = name	


class Room:
	def __init__(self, name, password=""):
		self.users = []   # a list of sockets
		self.name = name
		self.password = password  # rooms can be locked with a password 

	def removeUser(self, user): 
		self.users.remove(user)
		msg = user.name.encode(encoding = 'UTF-8') + " left the room\n"
		self.transmit(user, msg) 

	def transmit(self, sender, msg):
		msg = send.name.encode() + ":" + msg
		for users in self.users
			user.socket.sendall(msg) 

	# can add a welcome msg 

# class feed ? haven't decided where this should go.. 
# thinking its server side.. and server will handle outputting
# all room msgs to all its clients 

class Lobby: 
	def __init__(self): 
		self.rooms = {}  #dict, {room name : room} 
		self.roomUsers = {}  #dict contain users & rooms they're in. {user : room name} 

	def welcomeMsg(self, user):
		user.socket.sendall("Welcome to the lobby, \n Enter a username: ")

	def processMsg(self, user, msg): 
		 
