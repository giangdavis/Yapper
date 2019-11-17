import socket
import re
import PySimpleGUI as sg
import select

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
LEAVE = "$leave roomname [Removes user from room]\n"
MEMBERS = "$members roomname [List members of room]\n"
EXIT = "$exit [disconnects from server]"
ROOMS = "$rooms [list all rooms in the lobby]\n"
COMMAND = "$commands [displays commands]\n"
CHATIN = "$chat roomname [to start sending messages to a room(s)]\n"
COMMANDS = "All available commands:\n" + NAMECHANGE + NEWROOM + LEAVE + MEMBERS + ROOMS + COMMAND + CHATIN

# ===========================================================================
# ===========================================================================

class User:
    def __init__(self, socket, name):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.rooms = {} # {RoomName : Bool} Bool = user is sending msgs to room

# ===========================================================================

    def setName(self, newName):
        self.name = newName
# ===========================================================================

    def fileno(self):
        return self.socket.fileno()
# ===========================================================================

    def getName(self):
        return self.name

# ===========================================================================

    def addRoom(self, room):
        self.rooms[room] = False

# ===========================================================================

    def printRooms(self):
        for x in self.rooms:
            print(x.name)

# ===========================================================================

    def leaveRoom(self, roomName):
        self.rooms.pop(roomName)

# ===========================================================================
# ===========================================================================

class Room:
    def __init__(self, name, password=""):
        self.users = []   # a list of sockets
        self.name = name
        self.password = password

# ===========================================================================

    def addUser(self, user):
        self.users.append(user)

# ===========================================================================

    def printUsers(self):  # for server use only
        print("Users in room: " + self.name + " ")
        for x in self.users:
            print(x.getName() + ' ')
            
# ===========================================================================

    def broadcast(self, msg):
        for x in self.users:
            x.socket.sendall(msg.encode())

# ===========================================================================

    def removeUser(self, user):
        self.users.remove(user)

# ===========================================================================

    def printMembers(self, user):  # to send the client users of room
        for x in self.users:
            member = x.name
            user.socket.sendall(member.encode())

# ===========================================================================
# ===========================================================================

class Lobby:
    def __init__(self):
        self.rooms = {}  # {room name : room}

# ===========================================================================

    def invalidCommand(self, user):
        user.socket.sendall(b'Invalid command')

# ===========================================================================

    def promptForName(self, user):
        user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?\n')

# ===========================================================================

    def printRooms(self):
        print("Rooms: ")
        for x in self.rooms.values():
            print(x.name + " ")

# ===========================================================================

    def checkLobby(self): 
        if len(self.rooms) == 0:
            return False
        return True

# ===========================================================================

    def listRooms(self, user):
        if len(self.rooms) == 0: # no rooms to list:
            user.socket.sendall(b'There are no rooms right now.\n')
        else:
            for room in self.rooms:
                msg = room
                user.socket.sendall(room.encode())

# ===========================================================================

    def handle(self, user, msg):
        msgLen = len(re.findall(r'\w+', msg)) # returns an int
        msgArr = msg.split(" ") # returns a list
        commandLen = len(msgArr[0]) #length of "$usersommand"
        print("command length = " + str(commandLen))
        print("msg length = " + str(msgLen))

        if "$newuser" in msg:
            # parse name from msg
            # if msgLen == 2: # argument check
            if msgLen == 2:
                # for room in self.rooms:
                    # if msgArr[1] in room.users:
                        # user.socket.sendall(b'$#@!Username$#@!')
                user.setName(msgArr[1])
                print("New user: " + user.getName())
                user.socket.sendall(b'!@#$Username!@#$') #success
            else: # adjust 
                user.socket.sendall(b'$#@!Username$#@!') #not success
            '''if self.checkLobby() is False:
                user.socket.sendall(b'0')
            else:
                user.socket.sendall(b'1')'''

        elif "$commands" in msg and commandLen == 9:
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
                self.invalidCommand(user)

        else:
            if len(self.rooms) == 0: # no rooms
                self.invalidCommand(user)
            else:
                for i in user.rooms: # loop through the rooms that the user is in
                    if user.rooms.get(i): # the user is actively chatting in this room
                        room = self.rooms.get(i)
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
# ===========================================================================
# ===========================================================================

class Server:
    def __init__(self): 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.socketList = []
        self.socketList.append(self.socket) 

    def addClient(self):
        newSocket, addr = self.socket.accept()
        newUser = User(newSocket, "")
        # newUser.fileno()
        self.socketList.append(newUser)
        return newUser
# ===========================================================================
    def start(self, ip): 
        lobby = Lobby() 
        self.socket.bind((ip, PORT))   # local host    
        # use cloud  
        # s.bind((socket.gethostname(), chatClasses.PORT)) 
        self.socket.listen(MAX_CLIENTS)

        print("Server set up & listening! Connect with address: " , ip)

        while True:
            readables, _, _ = select.select(self.socketList, [], [])
            for notifiedSocket in readables:
                if notifiedSocket is self.socket: # new connection
                    newUser = self.addClient()
                    lobby.promptForName(newUser)
                else:
                    try: 
                        encodedMsg = notifiedSocket.socket.recv(MAX_MESSAGE_LENGTH)
                        msg = encodedMsg.decode()
                        if encodedMsg: # msg from client 
                            print("Received data from " + notifiedSocket.name + ": " + msg)
                            lobby.handle(notifiedSocket, msg.lower()) 
                        else: #recv got 0 bytes, closed connection
                            print("Client sent 0 bytes, closed connection")
                            if notifiedSocket in self.socketList:
                                self.socketList.remove(notifiedSocket)
                    except:
                        print("Connection to client has been broken")
                        self.socketList.remove(notifiedSocket)

# ===========================================================================
# ===========================================================================
class Client:
    def __init__(self): 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connectionList = [self.socket]

# ===========================================================================

    def createRoom(self):
        name = sg.PopupGetText('Enter room name: ', 'Input Room Name')
        msg = "$room " + name
        self.socket.sendall(msg.encode())
    
# ===========================================================================

    def listMembers(self):
        name = sg.PopupGetText('Which room would you like to see the members of?', 'Input Room Name')
        msg = "$members " + name 
        self.socket.sendall(msg.encode()) 

# ===========================================================================

    def turnOnChat(self):
        name = sg.PopupGetText('Which room would you like to chat in?', 'Input Room Name')
        msg = "$chat " + name 
        self.socket.sendall(msg.encode()) 

# ===========================================================================

    def displayCommands(self):
        msg = "$commands"
        self.socket.sendall(msg.encode())
# ===========================================================================
    def usernameSuccess(self): 
        return

# ===========================================================================

    def usernameFail(self):
        layout = [[sg.Popup("Username already in use, please enter a new username")]]
        window = sg.Window('Yapper', layout)
        
# ===========================================================================

    def welcomeMenu(self, msg): 
        sg.change_look_and_feel('DarkTanBlue')

        layout = [[sg.T(msg)],      
                 [sg.Text('Enter a Username:'), sg.InputText(key = '__username__')],      
                 [sg.Submit(), sg.Cancel()]]      

        window = sg.Window('Yapper', layout)    

        event, values = window.read()    
        window.close()
        username = "$newuser " + values['__username__']
        return username

# MAIN CHAT WINDOW =======================================================
    # def runChat(self, username, roomCheck): 
    def runChat(self, username):
        self.socket.sendall(username.encode())

        # nameMsg = self.socket.recv(MAX_MESSAGE_LENGTH)
        # print(nameMsg.decode())
        layout = [[(sg.Text('Chat Feed', size=[40, 1]))],
              [sg.Output(size=(80, 20)), sg.RButton('commands'), sg.RButton('chat')],
              [sg.Multiline(size=(70, 5), enter_submits=True),
               sg.Button('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0])), sg.RButton('members'), sg.RButton('create'),
               sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

        window = sg.Window('Yapper', layout, default_element_size=(30, 2))

        while True: 
            readables, _, _ = select.select(self.connectionList, [], [])

            for notifiedSocket in readables:
                if notifiedSocket is self.socket: # new message 
                    encodedMsg = notifiedSocket.recv(MAX_MESSAGE_LENGTH)
                    msg = encodedMsg.decode()
                    if msg:
                        print(msg)
                    else: 
                        print('Connection closed!') 
                        self.socket.close()
                        sys.exit()
                        window.close()

            event, values = window.read()
            if event == 'create':
                self.createRoom()
            elif event == 'members':
                self.listMembers()
            elif event == 'commands':
                self.displayCommands()
            elif event == 'chat':
                self.turnOnChat()
            else:
                window.close()


# ===========================================================================
    def start(self, ip):
        try: 
            self.socket.connect((ip, PORT)) 
            encodedMsg = self.socket.recv(MAX_MESSAGE_LENGTH)
            msg = encodedMsg.decode()
            username=self.welcomeMenu(msg) 
            # roomCheck = self.socket.recv(MAX_MESSAGE_LENGTH)
            # self.runChat(username, roomCheck.decode()) 
            self.runChat(username) 
        except:
            print("connection lost")
            self.socket.close()
# ===========================================================================