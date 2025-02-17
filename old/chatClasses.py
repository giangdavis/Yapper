import socket
import re

PORT = 50000
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
LEAVE = "$leave roomname [Removes user from room]\n"
MEMBERS = "$members roomname [List members of room]\n"
EXIT = "$exit [disconnects from server]"
ROOMS = "$rooms [list all rooms in the lobby]\n"
COMMAND = "$commands [displays commands]\n"
CHATIN = "$chat roomname [to start sending messages to a room(s)]\n"
COMMANDS = "All available commands:\n" + NAMECHANGE + NEWROOM + LEAVE + MEMBERS + ROOMS + COMMAND + CHATIN

class User:
    def __init__(self, socket, name):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.rooms = {} # {RoomName : Bool} Bool = user is sending msgs to room

    def setName(self, newName):
        self.name = newName

    def fileno(self):
        return self.socket.fileno()

    def getName(self):
        return self.name

    def addRoom(self, room):
        self.rooms[room] = False

    def printRooms(self):
        for x in self.rooms:
            print(x.name)

    def leaveRoom(self, roomName):
        self.rooms.pop(roomName)


class Room:
    def __init__(self, name, password=""):
        self.users = []   # a list of sockets
        self.name = name
        self.password = password

    def addUser(self, user):
        self.users.append(user)

    def printUsers(self):  # for server use only
        print("Users in room: " + self.name + " ")
        for x in self.users:
            print(x.getName() + ' ')

    def broadcast(self, msg):
        for x in self.users:
            x.socket.sendall(msg.encode())

    def removeUser(self, user):
        self.users.remove(user)

    def printMembers(self, user):  # to send the client users of room
        for x in self.users:
            member = x.name
            user.socket.sendall(member.encode())

class Lobby:
    def __init__(self):
        self.rooms = {}  # {room name : room}

    def invalidCommand(self, user):
        user.socket.sendall(b'Invalid command')

    def promptForName(self, user):
        user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?\n')

    def printRooms(self):
        print("Rooms: ")
        for x in self.rooms.values():
            print(x.name + " ")

    def listRooms(self, user):
        if len(self.rooms) == 0: # no rooms to list:
            user.socket.sendall(b'There are no rooms right now.\n')
        else:
            for room in self.rooms:
                msg = room
                user.socket.sendall(room.encode())

    def handle(self, user, msg):
        msgLen = len(re.findall(r'\w+', msg)) # returns an int
        msgArr = msg.split(" ") # returns a list
        commandLen = len(msgArr[0]) #length of "$usersommand"
        print("command length = " + str(commandLen))
        print("msg length = " + str(msgLen))
        if "$newuser" in msg:
            # parse name from msg
            if msgLen == 2: # argument check
                print(msgArr[1])
                user.setName(msgArr[1])
                print("New user: " + user.getName())
                user.socket.sendall(b'Username setting successful! Type $commands for a command list\n')
            else:
                user.socket.sendall(b'Username setting unsuccessful, please try again with the $changeName command\n')

        elif "$commands" in msg and commandLen == 10:
            user.socket.sendall(COMMANDS.encode())

        elif "$rooms" in msg and commandLen == 7:
            if msgLen == 1:
                self.listRooms(user)
            else:
                self.invalidCommand(user)

        elif "$room" in msg and commandLen == 5: # cases : no room, existing room, existing room and user is already in there
            # how many rooms is the users trying to join ?
            # join rooms that exist and create rooms that don't
            # TODO shorten, optimize this code.
            if msgLen == 2: # argument check
                # See if there is an existing room
                roomName = msgArr[1]
                print("Looking for room: " + roomName)
                if roomName in self.rooms: # trying to join an existing room
                    print("check")
                    room = self.rooms[roomName]
                    if user in room.users: # user is already in the room
                        user.socket.sendall(b"You're already in this room!\n")
                    else:
                        room.addUser(user)
                        room.printUsers()
                        user.addRoom(roomName)
                        welcome = user.name +  ":has joined the room!\n"
                        room.broadcast(welcome)
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
                else: # new room TO DO turn into function
                    newRoom = Room(roomName)
                    newRoom.addUser(user)
                    self.rooms[roomName] = newRoom
                    user.addRoom(roomName)
                    welcome = user.name +  ":has joined the room!\n"
                    print("created a new room: " + roomName)
                    newRoom.printUsers()
                    user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
            elif msgLen > 2: #user is trying to join multiple rooms
                for currentRoomName in msgArr[1:]:
                    print (currentRoomName)
                    if currentRoomName in self.rooms:
                        room = self.rooms[currentRoomName]
                        welcome = user.name +  ":has joined the room!\n"
                        room.broadcast(welcome)
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
                    else:
                        newRoom = Room(currentRoomName)
                        newRoom.addUser(user)
                        self.rooms[currentRoomName] = newRoom
                        print("created a new room:" + currentRoomName)
                        newRoom.printUsers()
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
            else:
                user.socket.sendall(b'Room Join/Create failed. Try Again.')

        elif "$sendall" in msg and commandLen == 8: #broadcast to all current rooms
            if msgLen > 1:
                newMsg = msg[9:] + "\n"
                for currentRoom in user.rooms:
                    if currentRoom in self.rooms:
                        self.rooms[currentRoom].broadcast(newMsg)

        elif "$leave" in msg and commandLen == 6:
            if msgLen == 2:
                roomName = msgArr[1]
                if roomName in self.rooms: # found the room user is trying to leave
                    room = self.rooms[roomName] # grab the room
                    room.removeUser(user) # remove user from the room
                    user.leaveRoom(roomName) # remove room from the user
                    if len(room.users) == 0: #room is now empty, remove from rooms
                        print("before pop")
                        self.rooms.pop(roomName)
                    else:
                        room.broadcast(user.name + " has left the room\n")
            else:
                self.invalidCommand(user)

        elif "$members" in msg and commandLen == 8:
            if msgLen == 2:
                roomName = msgArr[1]
                if roomName in self.rooms:
                    room = self.rooms[roomName]
                    room.printMembers(user)
                else:
                    self.invalidCommand(user)
            else:
                self.invalidCommand(user)

        elif "$chat" in msg and commandLen == 5: # and msgArr >= 2: # see if this 3rd condition works
            for roomName in msgArr:
                if roomName in self.rooms:
                    if roomName in user.rooms:
                        user.rooms[roomName] = True
                        user.socket.sendall(b'You are now able to chat in the desired room\n')
                    else:
                        tStr = "The room " + roomName + " is not yet created. Use $room!\n"
                        user.socket.sendall(tStr.encode())

        elif "$exit" in msg and commandLen == 6:
            if msgLen == 1:
                if len(user.rooms) > 0:
                    for currentRoomName in user.rooms: # go through the rooms the user is in
                        # remove user from the room
                        if currentRoomName in self.rooms:
                            room = self.rooms[currentRoomName]
                            room.removeUser(user)
                            if len(room.users) == 0:
                                self.rooms.pop(currentRoomName) # check if room is empty, turn this into func
                                print("room: " + currentRoomName + " is empty, closing it off.\n")
                            else:
                                room.broadcast(user.name + " has left the room\n")
                user.socket.sendall(b'$exit')
            else:
                print("check")
                self.invalidCommand(user)

        else:
            if len(self.rooms) == 0: # no rooms
                self.invalidCommand(user)
            else:
                for i in user.rooms: # loop through the rooms that the user is in
                    if user.rooms.get(i): # the user is actively chatting in this room
                        print("works")
                        room = self.rooms.get(i)
                        print("worksx2")
                        room.broadcast(msg)


'''
Notes
Can we move msg length check to only do it once? 
commands: create/join room , broadcast to all rooms, broadcast to more than 1 room, disconnect 
list all rooms, leave room, joining multiple rooms 
For existing room check: make a function 
fuck it make functions for most of this shit : 
	add room to rooms 
	create room 
	turn these into f unctions  (sphaghetti)
	program currently accepts : "$roomf as a valid room command and for other commands. 
	can fix this by also checking the str len 
For some reason, command length is being inconsistent... stress test this 
	i think its bc if you do 1 command w/out arguments like $commands it counts the extra white space at the end. 
	move msgLen check up into $command check if it only accepts 1 argument number like $members only accepts $members roomname (2)
'''