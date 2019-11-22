import socket, select, sys
import PySimpleGUI as sg

# import time

PORT = 55555
MAX_MESSAGE_LENGTH = 4096
HELLO = 5


# ===========================================================================
# ===========================================================================
class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connectionList = [self.socket]

    # ===========================================================================

    def createRoom(self):
        name = sg.PopupGetText('Enter room name(s) (separate with a space) : ', 'Input Room Name')
        msg = "$room " + name
        self.socket.sendall(msg.encode())

    # ===========================================================================

    def roomInfo(self):
        msg = "$rooms"
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

    def chat(self, msg):
        self.socket.sendall(msg.encode())

    # ===========================================================================

    def usernameFail(self):
        layout = [[sg.Popup("Invalid username, please restart the client and enter a new username")]]
        window = sg.Window('Yapper', layout)
        window.close()

    # ===========================================================================

    def joinRoom(self, room):
        msg = "$room " + room
        self.socket.sendall(msg.encode())

    # ===========================================================================

    def displayRooms(self, msg):
        arr = msg.split(" ")
        rooms = {arr[1]} # set room for fast look ups

        if len(arr) > 2:
            for currentRoomName in arr[2:]:
                rooms.add(currentRoomName)
        arr = []
        for room in rooms:
            arr.append(room)

        layout = [[self.roomBt(arr)]] # add refresh button
        window = sg.Window('Rooms', layout, size=(150,225))

        while True:
            event, values = window.read()
            if event == None:
                break
            if event == 'ROOMS':
                self.joinRoom(values['ROOMS'])
        window.close()
    # ===========================================================================

    def roomBt(self, rooms):
        return sg.Listbox(key='ROOMS', values=rooms, right_click_menu=['Join'], size=(100, 200), enable_events=True)

    # ===========================================================================

    def welcomeMenu(self):
        username = sg.PopupGetText('You have successfull connected to the lobby, what is your name?', '')
        msg = "$newuser " + username
        self.socket.sendall(msg.encode())


    # ===========================================================================
    def sendLobbyCheck(self):
        msg = "!@#$roomUpdate!@#$"
        self.socket.sendall(msg.encode())

    # ===========================================================================

    def getData(self, runFreq, lock, guiQueue):
        readables, _, _ = select.select(self.connectionList, [], [])
        while True:
            for notifiedSocket in readables:
                if notifiedSocket is self.socket:  # new message
                    encodedMsg = notifiedSocket.recv(MAX_MESSAGE_LENGTH)
                    msg = encodedMsg.decode()
                    if msg == "You have successfully connected to the Lobby!!! What is your name?\n":
                        guiQueue.put('You have successfully connected to the Lobby!!! What is your name?\n')
                    elif "!@#$Username!@#$" in msg:
                        guiQueue.put('Username setting successful!')
                    elif msg == "$#@!Username$#@!":
                        self.usernameFail()
                    elif msg:
                        guiQueue.put(msg)
                    else:
                        print('Connection closed!')
                        self.socket.close()
                        sys.exit()
                        window.close()

    # ===========================================================================

    def start(self, ip):
        try:
            self.socket.connect((ip, PORT))
        except Exception as e:
            print("Could not connect, try again")
            print(e)
            self.socket.close()
            sys.exit()

# ===========================================================================
