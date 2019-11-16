import socket
import select
import sys
import PySimpleGUI as sg
from chatClasses import User, Room, Lobby
import chatClasses

# =========================================================== 

def welcomeMenu(): 
    sg.change_look_and_feel('DarkTanBlue')

    layout = [[sg.Text('You have successfully connected to the Lobby!!!')],      
                 [sg.Text('Enter a Username:'), sg.InputText(key = '__roomName__')],      
                 [sg.Submit(), sg.Cancel()]]      

    window = sg.Window('Yapper', layout)    

    event, values = window.read()    
    window.close()
    username = values['__roomName__']
    print(type(username))
    return username
  

# ===========================================================

'''
# NEW WINDOW ===========================================================================
#create new window 
layout = [[sg.InputText(key='room'), sg.Text('Add a room!'), sg.Button(image_filename="addRoomButton.png", image_size=(50,50), image_subsample=10,border_width=0)]]
createRoomWindow = sg.Window('Yapper', layout) 

event, values = createRoomWindow.read()   
while True:
    if event in ('Button'):
        room = values[0]
createRoomWindow.close()
# =========================================================== 
# '''

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
            check = msg.decode()
            if msg: #incoming message
                if check == "$exit":
                    sys.stdout.write("Successfully disconnected to server.")
                    sys.exit(2)
                elif "You have successfully connected to the Lobby!!! What is your name?" in check:
                    sendName=welcomeMenu()
                    first = True
                    print(sendName)
                    newMsg = "$newuser " + sendName
                    serverConnection.sendall(newMsg.encode())
                sys.stdout.write(msg.decode()) # get rid of it
                sys.stdout.flush() # get rid of it
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