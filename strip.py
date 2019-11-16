#!/usr/bin/env python
import PySimpleGUI as g

'''
A chat window.  Add call to your send-routine, print the response and you're done
'''

g.ChangeLookAndFeel('GreenTan')            # give our window a spiffy set of colors

layout =  [[g.Text('Your output will go here', size=(40, 1))],
            [g.Output(size=(60, 15), font=('Helvetica 10'))],
            [g.Multiline(size=(44, 5), enter_submits=True, key='query', do_not_clear=False),
            g.Button('SEND', button_color=(g.YELLOWS[0], g.BLUES[0]), bind_return_key=True),
            g.Exit(button_color=(g.YELLOWS[0], g.GREENS[0]))]]

window = g.Window('Chat window', 
                   default_element_size=(30, 2), 
                   font=('Helvetica',' 13'), 
                   default_button_element_size=(8,2)).Layout(layout)

# ---===--- Loop taking in user input and using it  --- #
while True:
    event, values = window.Read()
    if event is 'SEND':
        query = values['query'].rstrip()
        # EXECUTE YOUR COMMAND HERE
        print('The command you entered was {}'.format(query))
    elif event in (None, 'Exit'):            # quit if exit button or X
        break

window.Close()
