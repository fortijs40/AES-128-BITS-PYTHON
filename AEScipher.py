import PySimpleGUI as sg
import secrets
from AESOperations import getEncypheredText, getUncypheredText

# Define the window's contents
first_column = [
    [
    sg.Text("Choose a file to encrypt", size=(20, 1))
    ],
    [ 
        sg.InputText(key='fileName', size=(60)),
        sg.FileBrowse("Browse", key='-BROWSE-', file_types=(("Text Files", "*.txt"),), size=(10, 1), enable_events=True,target='-BROWSE-'),
    ],
    [
        sg.Text("Test FIPS197 hexBits:", size=(20, 1), key='textForTest', background_color='lime', text_color='black', pad=(0, 0)),
        sg.Multiline("3243f6a8885a308d313198a2e0370734",size=(40, 1), key='testBits', disabled=True, no_scrollbar=True, background_color='gray', pad=(0, 0),border_width=0)
    ],
    [
        sg.Text("Test FIPS197 hexKey:", size=(20, 1), key='textForKeyTest', background_color='lime', text_color='black', pad=(0, 0)),
        sg.Multiline("2b7e151628aed2a6abf7158809cf4f3c",size=(40, 1), key='testKeyBits', disabled=True, no_scrollbar=True, background_color='gray', pad=(0, 0),border_width=0)
    ],
    [
        sg.Text("Enter your 32 symbol hex to encrypt", size=(30, 1)),
        sg.Column([[sg.Input(key='message',size=(40), enable_events=True)]])
    ],
    [
        sg.Text("Enter your 32 symbol hex key", size=(30, 1)),
        sg.Column([[sg.Input(key='key', size=(40), enable_events=True)]])
    ],
    [sg.Text(key='warning'),sg.Text(key='warningKey')],
    [sg.Text(size=(40, 1), key='-OUTPUT-')],
    [sg.Button('SAVE')],
    [sg.Button('DISCARD')],
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
second_column = [
    [sg.Multiline(size=(75,18),key='-FILE-CONTENT-', background_color="pink",disabled=True)],
    [sg.Multiline(size=(75,18),key='-NEW-FILE-CONTENT-', background_color="pink",disabled=True)],
]
layout = [
    [
        sg.Column(first_column),
        sg.VSeperator(),
        sg.Column(second_column)
    ]
]


# Create the window
window = sg.Window('AES encrypt and decrypt', layout, size=(1200, 600))

# Display and interact with the Window using an Event Loop
#originalOutputText = window['-OUTPUT-']
#converts 4x4 matrix to 128 bit hex string
def matrix_to_string(matrix):
    return ''.join([''.join([str(cell) for cell in row]) for row in matrix])
#converts 4x4 matrix to plain text
def hex_to_text(hex):     
    text = ""
    for byte in range(0,len(hex),2):
            text += chr(int(hex[byte:byte+2], 16))
    padding_length = int(hex[-2:],16)
    print(hex[-2:],'====last 2 hex values')
    print(padding_length, '= PADDING LENGTH')
    return text[:-padding_length]
#converts hex string to 4x4 matrix
def hex_to_matrix(hex_string):
    matrix = [['00', '00', '00', '00'] for _ in range(4)] # create 4x4 matrix
    for i in range(4):
        for j in range(4):
            char_index = (i * 4 + j) * 2    
            matrix[i][j] = hex_string[char_index:char_index + 2]
    return matrix

def text_to_hex(text):
    return text.encode('utf-8').hex()
def add_padding_to_hex_text(hex_text):
    #print(len(hex_text)//2, '-garums teksta bytos-', (len(hex_text)%8)//2)
    amount_to_pad = 16 - ((len(hex_text)%32)//2)  #since the text is in hex already the reminder is taken from 32 (1 text character = 2 hex characters)
    print(amount_to_pad , "-padojamais garums")
    padding = format(amount_to_pad, '02x')  #converts int(amount) into hex number with 2 characters(will add 0 in front of the hex if needed)
    print(padding, ' == padding hexadec')
    return hex_text + padding * amount_to_pad
def chop_hex_into_128bits(hex_string):
    list_of_hex = [hex_string[x:x+32] for x in range(0,len(hex_string),32)]
    print(list_of_hex,"===== ŠITĀ SAGRIEŽ")
    return list_of_hex
def clear_variables_from_values():
    global cypheredText, input_text, fileContent
    input_text.clear()
    fileContent = ''
    cypheredText = ''
    window['-FILE-CONTENT-'].update('')
    window['-NEW-FILE-CONTENT-'].update('')
    window['fileName'].update('')
def write_to_file(text_to_write):
    file = open(values['fileName'],'w')
    file.write(text_to_write)
    file.close()

cypheredText = ''
uncypheredText = ''
input_text = ''
fileContent = ''
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    if event == '-BROWSE-':
        if values['-BROWSE-']:
            file = open(values['-BROWSE-'], 'r')
            fileContent = file.read()
            file.close()
            if fileContent:
                window['fileName'].update(values['-BROWSE-'])
                #print("File content:", len(fileContent))
                #print(text_to_hex(fileContent))
                #input_text = chop_hex_into_128bits(text_to_hex(fileContent))
                #input_text = chop_hex_into_128bits(input_text)
                #print(chop_hex_into_128bits(text_to_hex(fileContent)))
                window['-FILE-CONTENT-'].update(fileContent)
    input_key = values['key']
    # Check the length of the entered key
    if len(input_key) > 32:
        window['warningKey'].update("Cypher key character limit reached: 32/" + str(len(input_key) - 1))
        window['key'].update(input_key[:32])  # Truncate to the first 32 characters
    elif len(input_key) < 32:
        window['warningKey'].update("I still need more characters: 32/" + str(len(input_key)))
    elif len(input_key) == 32:
        window['warningKey'].update("Cypher key character limit reached: 32/" + str(len(input_key)))

    # if user presses encrypt button
    if event == 'ENCRYPT':
        if len(input_key) < 32 or len(fileContent) < 1 :
            continue
        iv = secrets.token_hex(16)
        input_text = add_padding_to_hex_text(text_to_hex(fileContent))
        input_text = chop_hex_into_128bits(input_text)
        #print(iv,"this is my IV")
        cbc_encrpytion_xor = format(int(iv,16) ^ int(input_text[0],16),'032x')
        for i in range(len(input_text)):
            if i == 0:
                originalPlainTextArray = hex_to_matrix(cbc_encrpytion_xor)
                cyphered4x4 = getEncypheredText(originalPlainTextArray,input_key)
                cypheredText = matrix_to_string(cyphered4x4)
            else:
                #print("old cypherblock:", matrix_to_string(cyphered4x4))
                cbc_encrpytion_xor = format(int(matrix_to_string(cyphered4x4),16) ^ int(input_text[i],16),'032x')
                #print("after xor with cyphered text:", cbc_encrpytion_xor, " == derived from:", hex(int(input_text[i],16)))
                originalPlainTextArray = hex_to_matrix(cbc_encrpytion_xor)
                cyphered4x4 = getEncypheredText(originalPlainTextArray,input_key)
                cypheredText += matrix_to_string(cyphered4x4)
        #print("Cyphered text:", cypheredText)
        cypheredText = iv+cypheredText
        window['-NEW-FILE-CONTENT-'].update(cypheredText)
        write_to_file(cypheredText)
        #print("Cypheredtext+IV",cypheredText)
        #hex_text = input_text.encode('utf-8').hex()  meant for text to hex, but had to change that we need to enter hex values from the start

        #originalPlainTextArray = hex_to_matrix(input_text)    # Convert hex string to 4x4 matrix
        #cyphered4x4 = getEncypheredText(originalPlainTextArray,input_key)   # Call encryption and get back cyphered 4x4 matrix
        #window['-CYPHERED-TEXT-'].update(matrix_to_string(cyphered4x4))
    if event == 'DECRYPT':
        if  len(input_key) < 32:
            continue
        input_text = chop_hex_into_128bits(fileContent)
        print(input_text, 'INPUT')
        iv = fileContent[:32]   #IV is the first 32 hex numbers
        print(iv,'          decypher IV')
        for i in range(1,len(input_text)):
            cypheredText = hex_to_matrix(input_text[i])
            uncyphered4x4 = getUncypheredText(cypheredText,input_key)
            if i == 1:
                uncypheredText = format(int(matrix_to_string(uncyphered4x4),16) ^ int(iv,16),'032x')
                print(uncypheredText)
            else:
                uncypheredText += format(int(matrix_to_string(uncyphered4x4),16) ^ int(input_text[i-1],16),'032x')
        plain_text = hex_to_text(uncypheredText)
        window['-NEW-FILE-CONTENT-'].update(plain_text)
        print(uncypheredText, '===uncyphered TEXT IN HEX')
        print(hex_to_text(uncypheredText), '===uncyphered TEXT')
        write_to_file(plain_text)
        #cypheredText = hex_to_matrix(values['cypherText'])
        #uncyphered4x4 = getUncypheredText(cypheredText,input_key)
        #window['-DECYPHERED-TEXT-'].update(matrix_to_string(uncyphered4x4))
    if event == 'SAVE':
        decision = sg.popup_ok_cancel("Do you want to overwrite the plaintext file?")
        if decision == 'Cancel' or decision == None or len(values['fileName'])<1 :
            continue
        file = open(values['fileName'],'w')
        file.write(cypheredText)
        file.close()
        clear_variables_from_values()

    if event == 'DISCARD':
        clear_variables_from_values()
 
# Finish up by removing from the screen
window.close()
