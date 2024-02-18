import PySimpleGUI as sg
import secrets
from AESOperations import getEncypheredText, getUncypheredText

# Define the window's contents
first_column = [
    [sg.Text("", size=(20, 3),background_color='#240A2B')],
    [sg.Text("Choose a file to encrypt", size=(52, 1),font=("Roboto",15),background_color="white",text_color="black",justification="centre")],
    [ 
        sg.InputText(key='fileName', size=(40),font=("Roboto",15)),
        sg.FileBrowse("Browse", key='-BROWSE-', file_types=(("Text Files", "*.txt"),), size=(10, 1), enable_events=True,target='-BROWSE-',font=("Roboto",15)), #targets itself to launch event when clicked
    ],
    [sg.Text("", size=(20, 3),background_color='#240A2B')],
    [
        sg.Text("TEST PURPOSE KEY:", size=(20, 1), key='textForKeyTest', background_color='lime', text_color='black',justification='centre',font=("Roboto",15)),
        sg.Multiline("2b7e151628aed2a6abf7158809cf4f3c",size=(31, 1), key='testKeyBits', disabled=True, no_scrollbar=True, background_color='gray',border_width=0,font=("Roboto",15))
    ],
    [sg.Text("Enter your 32 symbol hex key:", size=(52),font=("Roboto",15),background_color="white",text_color="black",justification="centre")],
    [sg.Input(key='key', size=(52), enable_events=True,font=("Roboto",14),background_color="#B7F0EA",justification="centre")],
    [sg.Text("I still need more characters: 0/32",size=(52),key='warningKey',font=("Roboto",15),background_color="white",text_color="black",justification="centre")],
    [sg.Text("", size=(20, 4),background_color='#240A2B')],
    [
        sg.Button('ENCRYPT',size=(25,2),font=("Roboto",15),button_color=("black","#90fca0")),
        sg.Button('DECRYPT',size=(25,2),font=("Roboto",15),button_color=("black","#fc9090"))
    ],
]
second_column = [
    [sg.Text("Preview of before:",size=(50,1),background_color="white",text_color="black",justification="centre",font=("Roboto",15))],
    [sg.Multiline(size=(47,11),key='-FILE-CONTENT-', background_color="#c190fc",disabled=True,font=("Roboto",14))],
    [sg.Text("Preview of after decryption/encryption:",size=(50,1),background_color="white",text_color="black",justification="centre",font=("Roboto",15))],
    [sg.Multiline(size=(47,11),key='-NEW-FILE-CONTENT-', background_color="#c190fc",disabled=True,font=("Roboto",14))],
]
layout = [
    [
        sg.Column(first_column,size=(600,1100),background_color="#240A2B"),
        sg.VSeperator(),
        sg.Column(second_column,size=(600,1100),background_color="#240A2B")
    ]
]

# Create the window
window = sg.Window('AES encrypt and decrypt', layout, size=(1200, 600),background_color="black",button_color=("black","white"))

# Display and interact with the Window using an Event Loop
#originalOutputText = window['-OUTPUT-']
#converts 4x4 matrix to 128 bit hex string
def matrix_to_string(matrix):
    return ''.join([''.join([str(cell) for cell in row]) for row in matrix])
#converts 4x4 matrix to plain text
def hex_to_text(hex):
    text = bytes.fromhex(hex).decode('utf-8')
    padding_length = int(hex[-2:], 16)
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
    amount_to_pad = 16 - ((len(hex_text)%32)//2)  #since the text is in hex already the reminder is taken from 32 (1 text character = 2 hex characters)
    padding = format(amount_to_pad, '02x')  #converts int(amount) into hex number with 2 characters(will add 0 in front of the hex if needed)
    return hex_text + padding * amount_to_pad

def chop_hex_into_128bits(hex_string):
    list_of_hex = [hex_string[x:x+32] for x in range(0,len(hex_string),32)]
    return list_of_hex

def clear_variables_from_values():          #clears used variables
    global cypheredText, input_text, fileContent
    input_text.clear()
    fileContent = ''
    cypheredText = ''
    window['fileName'].update('')

def write_to_file(text_to_write):
    with open(values['fileName'], 'w', encoding='utf-8') as file:
        file.write(text_to_write)

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
            file = open(values['-BROWSE-'], 'r',encoding="utf8")
            fileContent = file.read()
            #print(text_to_hex(fileContent))
            file.close()
            if fileContent:
                window['fileName'].update(values['-BROWSE-'])
                window['-FILE-CONTENT-'].update(fileContent[:256])
                window['-NEW-FILE-CONTENT-'].update('')

    input_key = values['key']
    # Check the length of the entered key
    if len(input_key) > 32:
        window['warningKey'].update("Cypher key character limit reached:"+ str(len(input_key) - 1)+ "/32")
        window['key'].update(input_key[:32])  # Truncate to the first 32 characters
    elif len(input_key) < 32:
        window['warningKey'].update("I still need more characters: "+str(len(input_key))+"/32" )
    elif len(input_key) == 32:
        window['warningKey'].update("Cypher key character limit reached:"+str(len(input_key))+"/32")

    # if user presses encrypt button
    if event == 'ENCRYPT':
        try:
            if len(input_key) < 32 or len(fileContent) < 1 :
                continue
            iv = secrets.token_hex(16)      #Generates secure 16 byte hex key for each encryption
            input_text = add_padding_to_hex_text(text_to_hex(fileContent))
            input_text = chop_hex_into_128bits(input_text)
            cbc_encrpytion_xor = format(int(iv,16) ^ int(input_text[0],16),'032x')

            for i in range(len(input_text)):
                if not i == 0:              # on first iteration IV is XOR'ed with plain text and this is ignored
                    cbc_encrpytion_xor = format(int(matrix_to_string(cyphered4x4),16) ^ int(input_text[i],16),'032x')
                #print("after xor with cyphered text:", cbc_encrpytion_xor, " == derived from:", hex(int(input_text[i],16)))
                originalPlainTextArray = hex_to_matrix(cbc_encrpytion_xor)
                cyphered4x4 = getEncypheredText(originalPlainTextArray,input_key)
                cypheredText += matrix_to_string(cyphered4x4)
        
            cypheredText = iv+cypheredText
            window['-NEW-FILE-CONTENT-'].update(cypheredText[:256])
            write_to_file(cypheredText)
            clear_variables_from_values()
            sg.popup_ok("Encryption was succesful",auto_close_duration=5)
            #print("Cypheredtext+IV",cypheredText)
        except:
            clear_variables_from_values()
            sg.popup_error_with_traceback(" Uhhm, something went wrong. ")
    #if decrypt button is pressed
    if event == 'DECRYPT':
        try:
            if  len(input_key) < 32 or len(fileContent) < 1:
                continue
            input_text = chop_hex_into_128bits(fileContent)
            iv = fileContent[:32]   #IV is the first 32 hex numbers
            for i in range(1,len(input_text)):
                cypheredText = hex_to_matrix(input_text[i])
                uncyphered4x4 = getUncypheredText(cypheredText,input_key)
                if i == 1:
                    uncypheredText = format(int(matrix_to_string(uncyphered4x4),16) ^ int(iv,16),'032x')
                else:
                    uncypheredText += format(int(matrix_to_string(uncyphered4x4),16) ^ int(input_text[i-1],16),'032x')
            plain_text = hex_to_text(uncypheredText)
            #print(plain_text)
            window['-NEW-FILE-CONTENT-'].update(plain_text[:256])
            #print(hex_to_text(uncypheredText), '===uncyphered TEXT')
            write_to_file(plain_text)
            clear_variables_from_values()
        except:
            clear_variables_from_values()
            sg.popup_error_with_traceback(" Uhhm, something went wrong. ")
 
# Finish up by removing from the screen
window.close()
