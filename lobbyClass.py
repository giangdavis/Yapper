import re
import roomClass
import datetime

# NAMECHANGE = "$name name [Changes username]"
NEWROOM = "$room roomname [Creates/Joins Room]\n"
LEAVE = "$leave roomname [Removes user from room]\n"
MEMBERS = "$members roomname [List members of room]\n"
EXIT = "$exit [disconnects from server]\n"
LOBBY = "$lobby [list all rooms in the lobby]\n"
COMMAND = "$commands [displays commands]\n"
CHATIN = "$chat roomname [to start sending messages to a room(s)]\n"
EXIT = "$exit [disconnects from server]\n"
YAP = "$yap roomname1 roomname2 ... roomnameX ~~~message~~~ [sends message to all rooms specified]\n"
PRIVATEMSG = "$msg username ~~~message~~~ [send a private msg(enclose with 3 tildes) to 'username']\n"
FILE = "$file filename username [send a file from filepath to 'username']\n"
COMMANDS = "All available commands:\n" +  NEWROOM + LEAVE + MEMBERS + LOBBY + COMMAND + CHATIN +  YAP + PRIVATEMSG + EXIT + FILE

class Lobby:
    def __init__(self):
        self.rooms = {}  # {room name : room}
        self.users = [] # [user object,]

    def __del__(self):
        print("Lobby closed\n")

    def disconnectFromClients(self):
        for roomName in self.rooms:
            room = self.rooms[roomName]
            room.clean()
            del room

    def invalidCommand(self, user):
        user.socket.sendall(b'Invalid command')

    def promptForName(self, user):
        user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?')

    def printRooms(self):
        print("Rooms: ")
        for x in self.rooms.values():
            print(x.name + " ")

    def listRooms(self, user):
        if len(self.rooms) == 0:  # no rooms to list:
            user.socket.sendall(b'There are no rooms right now.')
        else:
            first = True
            for room in self.rooms:
                if first == True:
                    msg = room
                    first = False
                else:
                    msg = msg + ", " + room
            user.socket.sendall(b'Current Rooms in the Lobby: ' + msg.encode())

    def removeUser(self, user): # server removing user
        for roomName in user.rooms: # loops through the users rooms
            room = self.rooms.get(roomName) # grabs the room
            if room.removeUser(user) == 0:# removes user frm the room
                self.rooms.pop(roomName)
        user.socket.sendall(b'$$exit')
        if user in self.users:
            self.users.remove(user)

    def exit(self, user):
        self.removeUser(user)

    def leaveRoom(self, user, roomName):
        if roomName in self.rooms and roomName in user.rooms:
            room = self.rooms[roomName]
            user.socket.sendall(b'You have left the room: ' + roomName.encode())
            user.rooms.pop(roomName)
            if room.removeUser(user) == 0:  # empty room now
                self.rooms.pop(roomName)
        else:
            user.socket.sendall(b'You are not in this room...')

    def roomCommand(self, user, msgArr):
        for roomName in msgArr[1:]:
            print(user.name + " trying to create/join: " + roomName)
            if roomName in self.rooms:  # existing room
                room = self.rooms[roomName]
                if user in room.users:
                    user.socket.sendall(b'You are already in a room you tried to create/join')
                else:
                    room.addUser(user)
                    user.addRoom(roomName)
                    newMsg = "You just joined " + roomName + ' Use "$chat roomname" to talk!'
                    user.socket.sendall(newMsg.encode())
            else: # new room
                newRoom = roomClass.Room(roomName)
                newRoom.addUser(user)
                self.rooms[roomName] = newRoom
                user.addRoom(roomName)
                user.socket.sendall(b'Room Creation Successful! Use "$chat roomname" to talk in here!')
        user.socket.sendall(b'\n')
    # creates a new user
    def newUser(self, user, username):
        for x in self.users:
            if username == x.name:
                print("duplicate  user tried to join\n")
                return -1
        user.setName(username)
        print("NEW USER: " + username)
        user.socket.sendall(b'Username setting successful! Type $commands for a Command List')
        self.users.append(user)
        return 1

    def privateMessage(self, user, msgArr):
        success = False
        receiverName = msgArr[1]    
        print(user.name + " sending to " + receiverName)     # get the name 
        for receivers in self.users:
            if receivers.name == receiverName:
                print("found")
                msg = self.getValidMsg(msgArr)
                if msg != "": 
                    time = datetime.datetime.now()
                    timeStr = time.strftime("%I") + ":" + time.strftime("%M") + " " + time.strftime("%p ")
                    receivers.socket.sendall(timeStr.encode() + user.name.encode() + b': ' + msg.encode())
                    success = True
        if success == False:
            user.socket.sendall(b'Could not send private message, check arguments and try again.')

    def getValidMsg(self, msgArr):
        tildeCount = 0
        yap = ""
        first = True
        for word in msgArr:
            if '~~~' in word:
                if first == True:
                    startMsg = msgArr.index(word)
                    first = False
                tildeCount = tildeCount + 3
                if len(word) > 3 and 6 > tildeCount:
                    for char in word[3:]:
                        if char == '~':
                            tildeCount = tildeCount + 1

        first = True 
        if tildeCount == 6:
            for x in msgArr[startMsg:]:
                if first == True:
                    yap = x
                    first = False
                else:
                    yap = yap + " " + x
            yapArr = re.findall("~~~(.*?)~~~", yap) 
            first = True
            yap = yapArr[0]
        return yap
        '''
        print("yap1: " +  yap)
        yapArr = re.findall("~~~(.*?)~~~", yap) 
        first = False
        new = ""

        for word in yapArr:
            if word != '~~~':
                if 
        print("yap3: ")
        print(test)
        return yap '''


    def yap(self, user, msgArr, msgLen):
        # check argument length
        print("LENGTH OF ARR TO YAP: " + str(msgLen) + "\n")
        success = False
        if msgLen > 2:
            # check for valid message
            msgToYap = self.getValidMsg(msgArr)
            if msgToYap != "":
                print("MSG TO YAP : " + msgToYap + "\n")
                for roomName in msgArr[1:]:
                    if roomName in self.rooms:
                        room = self.rooms[roomName]
                        print ("Yapping to : " + roomName + "\n" )
                        room.broadcast(user, msgToYap)
                        success = True
        if not success:
            self.invalidCommand(user)

    def sendFile(self, msg, sender):
        msgArr = msg.split(" ", 4)
        msgArr = msgArr[2].split("\n")
        # msgArr = self.formatMsg(msgArr)
        print(msgArr)
        receiverName = msgArr[0]
        success = False
        for curr in self.users:
            if receiverName == '':
                break
            if receiverName == curr.name:
                msg = sender.name  + " " + msg
                curr.socket.sendall(msg.encode())
                sender.socket.sendall(b'File transfer successful')
                success = True
        if success == False:
            sender.socket.sendall(b'File transfer unsuccessful, user does not exist')
        
    def formatMsg(self, msgArr):
        while("" in msgArr):
            msgArr.remove("")
        return msgArr

    def chatCommand(self, user, roomName): 
        if roomName in self.rooms and roomName in user.rooms:
            user.rooms[roomName] = True
            user.socket.sendall(b'You are now able to chat in the desired room')
        else:
            tStr = "The room " + roomName + " is not yet created. Or you're not in there. Use $room!"
            user.socket.sendall(tStr.encode()) 

    def handle(self, user, msg):
        #check for file transfers first 
        if "$file" in msg:
            self.sendFile(msg, user)
        else:
            msg = msg.rsplit('\n')
            msg = msg[0]
            msgLen = len(re.findall(r'\w+', msg))  # returns an int
            msgArr = msg.split(" ")   # returns a list
            commandLen = len(msgArr[0])  # length of "$usersommand"
            msgArr = self.formatMsg(msgArr)
            print("msg arr  =  ")
            print(msgArr)
            print("command length = " + str(commandLen))
            print("msg length = " + str(msgLen))
            if "$newuser" in msg:
                if msgLen == 2 and self.newUser(user, msgArr[1]) == 1:
                    print("user joined")
                else:
                    user.socket.sendall(b'Username setting unsuccessful. Connect Again!')

            elif "$commands" in msg and commandLen == 9:
                user.socket.sendall(COMMANDS.encode())

            elif "$lobby" in msg and commandLen == 6:
                if msgLen == 1:
                    self.listRooms(user)
                else:
                    self.invalidCommand(user)

            elif "$msg" in msg and commandLen == 4:
                if msgLen >= 3:
                    self.privateMessage(user, msgArr)
                else:
                    user.socket.sendall(b'private messaging failed, invalid argument count')

            elif "$room" in msg and commandLen == 5: # cases : no room, existing room, existing room and user is already in there
                if msgLen >= 2:  # argument check
                    self.roomCommand(user, msgArr)
                else:
                    user.socket.sendall(b'Room Join/Create failed. Try Again.')

            elif "$yap" in msg and commandLen == 4:
                self.yap(user, msgArr, msgLen)

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

            elif "$chat" in msg and commandLen == 5 and msgLen == 2 :  
                self.chatCommand(user, msgArr[1])

            elif "$exit" in msg and commandLen == 5:
                if msgLen == 1:
                    self.exit(user)
                else:
                    self.invalidCommand(user)

            else:
                if len(self.rooms) == 0:  # no rooms
                    self.invalidCommand(user)
                else:
                    success = False
                    for i in user.rooms:  # loop through the rooms that the user is in
                        if user.rooms.get(i) and msg[0] != '$':  # the user is actively chatting in this room
                            room = self.rooms.get(i)
                            room.broadcast(user, msg)
                            success = True
                    if success == False:
                        self.invalidCommand(user)
