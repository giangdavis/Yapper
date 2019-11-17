import socket
import select
import sys
import PySimpleGUI as sg
from chatClasses import User, Room, Lobby
import chatClasses


def createRoom(socket, name):
    msg =  "$room " + name
    socket.sendall(msg.encode())

def listMembers(socket, roomName):
    msg = "$members " + roomName
    socket.sendall(msg.encode())

# =========================================================== 

def welcomeMenu(): 
    sg.change_look_and_feel('DarkTanBlue')

    layout = [[sg.T('You have successfully connected to the Lobby!!!')],      
                 [sg.Text('Enter a Username:'), sg.InputText(key = '__roomName__')],      
                 [sg.Submit(), sg.Cancel()]]      

    window = sg.Window('Yapper', layout)    

    event, values = window.read()    
    window.close()
    username = values['__roomName__']
    return username
  

# ===========================================================

def emptyLobby(socket): 
    layout = [[(sg.Text('This is where standard out is being routed', size=[40, 1]))],
              [sg.Output(size=(80, 20))],
              [sg.Multiline(size=(70, 5), enter_submits=True),
               sg.Button('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0])), sg.Button('members'), sg.RButton('create'),
               sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

    window = sg.Window('Chat Window', layout, default_element_size=(30, 2))

    # ---===--- Loop taking in user input and using it to query HowDoI web oracle --- #
    while True:
        event, value = window.read()
        if event == 'SEND':
            print(value)
        elif event == 'members':
            listMembers(socket, value[0])
        elif event == 'create':
            createRoom(socket, value[0])
        else:
            break
    window.close()
#create new window 


# ===========================================================

if len(sys.argv) < 2:
    print("Run as follows: python3 chatClient.py hostname (where hostname is an IP)")
    exit()
else:
    serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverConnection.connect((sys.argv[1], chatClasses.PORT))

# connectionList = [sys.stdin, serverConnection]
connectionList = [serverConnection]

first = False
while 1:
    readables, _, _ = select.select(connectionList, [], [])
    for notified_socket in readables:
        if notified_socket is serverConnection: # new msg
            msg = notified_socket.recv(chatClasses.MAX_MESSAGE_LENGTH)
            msgStr = msg.decode()
            print(msgStr)
            if msg: #incoming message
                if msgStr == "$exit":
                    sys.stdout.write("Successfully disconnected to server.")
                    sys.exit(2)
                elif "You have successfully connected to the Lobby!!! What is your name?" in msgStr:
                    sendName=welcomeMenu()
                    first = True
                    print(sendName)
                    newMsg = "$newuser " + sendName
                    serverConnection.sendall(newMsg.encode())
                    serverConnection.sendall(b' $$$checkLobby') # check if there are rooms
                elif "$$$rooms" in msgStr:
                    emptyLobby()
                elif "$$$norooms" in msgStr:
                    test=emptyLobby(serverConnection)
                    print("--test--: " + test)
                    serverConnection.sendall(test.encode())
                sys.stdout.write(msg.decode()) 
                # sys.stdout.flush() # get rid of it
            else: # msg contained 0 bytes, disconnected
                print ('Connection closed!')
                serverConnection.close()
                sys.exit()

    

'''
        else: # send a message from client
            if first == True:
                # newMsg = "$newuser " + sys.stdin.readline()
                newMsg = "$newuser " + sendName
                first = False
            else:
                # newMsg = sys.stdin.readline()
                newMsg = "failed"
            serverConnection.sendall(newMsg.encode())
            # sys.stdout.flush() # get rid of it
        #if the client socket is readable, sending a msg. broadcast
        #to other clients.'''