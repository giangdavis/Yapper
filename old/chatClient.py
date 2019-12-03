<<<<<<< HEAD
import socket
import select
import sys
from chatClasses import User, Room, Lobby
import chatClasses

if len(sys.argv) < 2:
    print("Run as follows: python3 chatClient.py hostname (where hostname is an IP)")
    exit()
else:
    serverConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverConnection.connect((sys.argv[1], chatClasses.PORT))

connectionList = [sys.stdin, serverConnection]
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
                    print("condition met!")
                    first = True
                sys.stdout.write(msg.decode())
                sys.stdout.flush()
            else: # msg contained 0 bytes, disconnected
                print ('Connection closed!')
                serverConnection.close()
                sys.exit()

        else: # send a message from client
            if first == True:
                newMsg = "$newuser " + sys.stdin.readline()
                first = False
            else:
                newMsg = sys.stdin.readline()
            serverConnection.sendall(newMsg.encode())
            sys.stdout.flush()
        #if the client socket is readable, sending a msg. broadcast
        #to other clients.
=======
import socket # dont need 
import select
import sys
import queue
import time
import threading
from chatClasses import User, Room, Lobby, Client
import chatClasses
import PySimpleGUI as sg

client = Client()
client.start('127.0.0.1')

guiQueue = queue.Queue()
threading.Thread(target=client.getData, args=(500, guiQueue), daemon=True).start()

layout = [[(sg.Text('Chat Feed', size=[40, 1]))],
              [sg.Output(key='FEED', size=(80, 20)), sg.RealtimeButton('commands'), sg.RealtimeButton('chat')],
              [sg.Multiline(key='INPUT', size=(70, 5), enter_submits=True, disabled=True, do_not_clear=True),
               sg.RealtimeButton('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0])), sg.RealtimeButton('members'), sg.RealtimeButton('create'),
               sg.RealtimeButton('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

window = sg.Window('Yapper', layout, default_element_size=(30, 2), finalize=True)

i = 0 

while True:
    event, values = window.read(timeout=100)

    if event == 'create':
        client.createRoom()
    elif event == 'members':
        client.listMembers() 
    elif event == 'commands':
        client.displayCommands()
    elif event == 'chat':
        client.turnOnChat()
        window['INPUT'].update(disabled=False)
    elif event == 'SEND':
        msg = values.get('INPUT')
        client.chat(msg)
    elif event in (None, 'EXIT'):
        break
        # loop through messages coming in from threads

    while True: 
        try: 
            message = guiQueue.get_nowait()
        except queue.Empty: # get_nowait() will get exception when queue is empty
            break
        # if msg received from queue, display the message in the window
        if message:
            if message == 'You have successfully connected to the Lobby!!! What is your name?\n':
                client.welcomeMenu()
            else:
                #window['FEED'].update(message)
                print(message)
                #window.refresh()
            # print(message)

window.close()
>>>>>>> 6ce3a64c63543d0d73091f68f7194fea4731ef2e
