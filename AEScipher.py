import PySimpleGUI as sg
from AESOperations import getEncypheredText, getUncypheredText

# Define the window's contents
layout = [
    [
        sg.Text("Enter your 16 characters to encrypt", size=(30, 1)),
        sg.Column([[sg.Input(key='message',size=(25), enable_events=True)]])
    ],
    [
        sg.Text("Enter your 16-symbol key", size=(30, 1)),
        sg.Column([[sg.Input(key='key', size=(25), enable_events=True)]])
    ],
    [sg.Text(key='warning'),sg.Text(key='warningKey')],
    [sg.Text(size=(40, 1), key='-OUTPUT-')],
    [sg.Button('ENCRYPT')],
    [
        sg.Text("Cyphered output:", size=(13, 1), key='CypherOut', background_color='pink', text_color='black', pad=(0, 0)),
        sg.Multiline(size=(40, 1), key='-CYPHERED-TEXT-', disabled=True, no_scrollbar=True, background_color='pink', pad=(0, 0),border_width=0)
    ],
    [
    sg.Text("Enter your cypherText:", size=(30, 1)),
    sg.Column([[sg.Input(key='cypherText',size=(40), enable_events=True)]])
    ],
    [
        sg.Text("Decyphered output:", size=(20, 1), key='DecypherOut', background_color='pink', text_color='black', pad=(0, 0)),
        sg.Multiline(size=(40, 1), key='-DECYPHERED-TEXT-', disabled=True, no_scrollbar=True, background_color='pink', pad=(0, 0),border_width=0)
    ],
    [sg.Button('DECRYPT')]
]

# Create the window
window = sg.Window('AES encrypt and decrypt', layout, size=(600, 300))

# Display and interact with the Window using an Event Loop
#originalOutputText = window['-OUTPUT-']
#converts 4x4 matrix to 128 bit hex string
def matrix_to_string(matrix):
    return ''.join([''.join([str(cell) for cell in row]) for row in matrix])
#converts 4x4 matrix to plain text
def matrix_to_text(matrix):     
    text = ""
    for row in matrix:
        for cell in row:
            text += chr(int(cell, 16))
    return text
#converts hex string to 4x4 matrix
def hex_to_matrix(hex_string):
    matrix = [['00', '00', '00', '00'] for _ in range(4)] # create 4x4 matrix
    for i in range(4):
        for j in range(4):
            char_index = (i * 4 + j) * 2    
            matrix[i][j] = hex_string[char_index:char_index + 2]
    return matrix
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    input_text = values['message']
    input_key = values['key']
    cypheredText = values['cypherText']
    # Check the length of the entered text
    if len(input_text) > 16:
        window['warning'].update("Plain text character limit reached: 16/" + str(len(input_text) - 1))
        window['message'].update(input_text[:16])  # Truncate to the first 16 characters
    elif len(input_text) < 16:
        window['warning'].update("I still need more characters: 16/" + str(len(input_text)))
    elif len(input_text) == 16:
        window['warning'].update("Plain text character limit reached: 16/" + str(len(input_text)))

    # Check the length of the entered key
    if len(input_key) > 16:
        window['warningKey'].update("Cypher key character limit reached: 16/" + str(len(input_key) - 1))
        window['key'].update(input_key[:16])  # Truncate to the first 16 characters
    elif len(input_key) < 16:
        window['warningKey'].update("I still need more characters: 16/" + str(len(input_key)))
    elif len(input_key) == 16:
        window['warningKey'].update("Cypher key character limit reached: 16/" + str(len(input_key)))


    # if user presses encrypt button
    if event == 'ENCRYPT':
        if len(input_text) < 16 or len(input_key) < 16:
            continue
        hex_text = input_text.encode('utf-8').hex() # Convert text to hex
        hex_key = input_key.encode('utf-8').hex()   # Convert key to hex

        #originalOutputText.update(hex_text)  # Display the original hex value
        #tempInput = "3243f6a8885a308d313198a2e0370734"
        #tempKey = "2b7e151628aed2a6abf7158809cf4f3c"

        originalPlainTextArray = hex_to_matrix(hex_text)    # Convert hex string to 4x4 matrix
        cyphered4x4 = getEncypheredText(originalPlainTextArray,hex_key)   # Call encryption and get back cyphered 4x4 matrix
        window['-CYPHERED-TEXT-'].update(matrix_to_string(cyphered4x4))
    if event == 'DECRYPT':
        if len(cypheredText) != 32 or len(input_key) < 16:
            continue
        hex_key = input_key.encode('utf-8').hex()
        cypheredText = hex_to_matrix(values['cypherText'])
        uncyphered4x4 = getUncypheredText(cypheredText,hex_key)
        window['-DECYPHERED-TEXT-'].update(matrix_to_text(uncyphered4x4))

# Finish up by removing from the screen
window.close()
