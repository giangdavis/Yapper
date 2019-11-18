import queue, threading
# import time

import PySimpleGUI as sg
import yapper_client_class as yapper

client = yapper.Client()
client.start('127.0.0.1')

lock = threading.Lock()

guiQueue = queue.Queue()
threading.Thread(target=client.getData, args=(lock, guiQueue), daemon=True).start()

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