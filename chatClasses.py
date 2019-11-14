import socket 

PORT = 55555
MAX_MESSAGE_LENGTH = 4096
MAX_CLIENTS = 15
SERVERSOCKETLIST = [] 
'''
class Server: 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def __init__ (self, host, port): 
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set the socket option, to continually listen. see doc 
	s.setblocking(False)  # turns off socket blocking
	s.bind(host, port)  # assigns host ip add and port to socket  
	# s.bind((socket.gethostname(), chatClasses.PORT)) # make it available to the outside world Test this w/ Erik Device ! 
	s.listen(MAX_CLIENTS) 
'''

class User: 
	def __init__(self, socket, name): 
		socket.setblocking(0)  # turn off blocking
		self.socket = socket 
		self.name = name

	def setName(self, newName): 
		self.name = newName

	def fileno(self): 
		return self.socket.fileno()

class Room:
	def __init__(self, name, password=""):
		self.users = []   # a list of sockets
		self.name = name
		# self.password = password  # rooms can be locked with a password 

	def removeUser(self, user): 
		self.users.remove(user)
		msg = user.name.encode(encoding = 'UTF-8') + " left the room\n" 


# class feed ? haven't decided where this should go.. 
# thinking its server side.. and server will handle outputting
# all room msgs to all its clients 

class Lobby: 
	def __init__(self): 
		self.rooms = {}  #dict, {room name : room} 
		self.roomUsers = {}  #dict contain users & rooms they're in. {user : room names} 

	def promptForName(self, user):
		# msg = "You have connected to the Lobby ! What is your name?" 
		user.socket.sendall(b'You have connected to the Lobby ! What is your name?\n') # send as bytes 

	# TO DO not working , temporarily just sending back to all sockets
	def handle(self, user, msg): 
		for socket in SERVERSOCKETLIST: 
			print(user.name + ': ')
			# right now printing to server as well, can change this style later 
			# if socket != server socket 
			try: 
				msgToSend = user.name.encode() + msg   
				socket.sendall(msgToSend)  
			except: 
				socket.close() 
				if socket in SERVERSOCKETLIST: 
					SERVERSOCKETLIST.remove(socket)