import re
import roomClass

# NAMECHANGE = "$name name [Changes username]\n"
NEWROOM = "$room roomname [Creates/Joins Room]\n"
LEAVE = "$leave roomname [Removes user from room]\n"
MEMBERS = "$members roomname [List members of room]\n"
EXIT = "$exit [disconnects from server]"
LOBBY = "$lobby [list all rooms in the lobby]\n"
COMMAND = "$commands [displays commands]\n"
CHATIN = "$chat roomname [to start sending messages to a room(s)]\n"
EXIT = "$exit [disconnects from server]\n"
COMMANDS = "All available commands:\n" +  NEWROOM + LEAVE + MEMBERS + LOBBY + COMMAND + CHATIN + EXIT

class Lobby:
    def __init__(self):
        self.rooms = {}  # {room name : room}

    def invalidCommand(self, user):
        user.socket.sendall(b'Invalid command\n')

    def promptForName(self, user):
        user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?\n')

    def printRooms(self):
        print("Rooms: ")
        for x in self.rooms.values():
            print(x.name + " ")

    def listRooms(self, user):
        if len(self.rooms) == 0:  # no rooms to list:
            user.socket.sendall(b'There are no rooms right now.\n')
        else:
            for room in self.rooms:
                msg = room
                user.socket.sendall(room.encode())

    def removeUser(self, user): # server removing user
        for roomName in user.rooms: # loops through the users rooms
            room = self.rooms.get(roomName) # grabs the room
            room.removeUser(user) # removes user frm the room
        user.socket.sendall(b'$$exit')
        if len(room.users) == 0:
            self.rooms.pop(roomName)

    def exit(self, user):
        self.removeUser(user)

    def leaveRoom(self, user, roomname):
        if roomname in self.rooms:
            room = self.rooms[roomname]
            user.socket.sendall(b'You have left the room: ' + roomname.encode())
            if room.removeUser(user) == 0:  # empty room now
                self.rooms.pop(roomname)

    # def roomCommand(self):

    # creates a new user
    def newUser(self, user, username):
        user.setName(username)
        print("NEW USER: " + username)
        user.socket.sendall(b'Username setting successful! Type $commands for a Command List\n')

    def handle(self, user, msg):
        msgLen = len(re.findall(r'\w+', msg))  # returns an int
        msgArr = msg.split(" ")   # returns a list
        commandLen = len(msgArr[0])  # length of "$usersommand"
        print("command length = " + str(commandLen))
        print("msg length = " + str(msgLen))
        if "$newuser" in msg:
            if msgLen == 2:  # argument check
                self.newUser(user, msgArr[1])
            else:
                user.socket.sendall(b'Username setting unsuccessful. Connect Again!')

        elif "$commands" in msg and commandLen == 10:
            user.socket.sendall(COMMANDS.encode())

        elif "$lobby" in msg and commandLen == 7:
            if msgLen == 1:
                self.listRooms(user)
            else:
                self.invalidCommand(user)

        elif "$room" in msg and commandLen == 5: # cases : no room, existing room, existing room and user is already in there
            # how many rooms is the users trying to join ?
            # join rooms that exist and create rooms that don't
            # TODO shorten, optimize this code.
            if msgLen == 2:  # argument check
                # See if there is an existing room
                roomName = msgArr[1]
                print("Looking for room: " + roomName)
                if roomName in self.rooms:  # trying to join an existing room
                    print("check")
                    room = self.rooms[roomName]
                    if user in room.users:  # user is already in the room
                        user.socket.sendall(b"You're already in this room!\n")
                    else:
                        room.addUser(user)
                        room.printUsers()
                        user.addRoom(roomName)
                        welcome = user.name + ": has joined the room!\n"
                        room.broadcast(welcome)
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
                else:  # new room TO DO turn into function
                    newRoom = roomClass.Room(roomName)  # might be fooked
                    newRoom.addUser(user)
                    self.rooms[roomName] = newRoom
                    user.addRoom(roomName)
                    welcome = user.name + ": has joined the room!\n"
                    print("created a new room: " + roomName)
                    newRoom.printUsers()
                    user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
            elif msgLen > 2:  # user is trying to join multiple rooms
                for currentRoomName in msgArr[1:]:
                    print(currentRoomName)
                    if currentRoomName in self.rooms:
                        room = self.rooms[currentRoomName]
                        welcome = user.name + ":has joined the room!\n"
                        room.broadcast(welcome)
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
                    else:
                        newRoom = roomClass(currentRoomName)
                        newRoom.addUser(user)
                        self.rooms[currentRoomName] = newRoom
                        print("created a new room:" + currentRoomName)
                        newRoom.printUsers()
                        user.socket.sendall(b'You now receive messages from this room, to chat in this room: use the command $chat\n')
            else:
                user.socket.sendall(b'Room Join/Create failed. Try Again.')

        elif "$sendall" in msg and commandLen == 8:  # broadcast to all current rooms
            if msgLen > 1:
                newMsg = msg[9:] + "\n"
                for currentRoom in user.rooms:
                    if currentRoom in self.rooms:
                        self.rooms[currentRoom].broadcast(newMsg)

        elif "$leave" in msg and commandLen == 6:
            if msgLen == 2:
                self.leaveRoom(user, msgArr[1])
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

        elif "$chat" in msg and commandLen == 5:  # and msgArr >= 2: # see if this 3rd condition works
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
                self.exit(user)
            else:
                self.invalidCommand(user)

        else:
            if len(self.rooms) == 0:  # no rooms
                self.invalidCommand(user)
            else:
                for i in user.rooms:  # loop through the rooms that the user is in
                    if user.rooms.get(i):  # the user is actively chatting in this room
                        room = self.rooms.get(i)
                        room.broadcast(msg)
