from AESdefault import Sbox, InvSbox

    # Rotates each round key by one byte/2 hex values
def RotWord(word):
    return (word[2:]+word[:2])

# Function to substitute each byte of a word
def SubWord(word):
    word_int = int(word, 16)
    return (Sbox(word_int >> 24) << 24) | (Sbox((word_int >> 16) & 0xFF) << 16) | (Sbox((word_int >> 8) & 0xFF) << 8) | Sbox(word_int & 0xFF)
def rcon(i):
    rcon_values = [
        0x01000000, 0x02000000, 0x04000000, 0x08000000,
        0x10000000, 0x20000000, 0x40000000, 0x80000000,
        0x1b000000, 0x36000000,
    ]
    return f'{rcon_values[i - 1]:08x}'

def KeyExpansion(key,Nk=4,Nr=10,Nb=4):
    # Convert key to first round_keys aka w0,w1,w2,w3
    key_words = [key[i:i+8] for i in range(0, len(key), 8)]  # splits the initial 16 byte key into 4 words each containing 8 hex values
    i=0
    # Initialize round keys array
    round_keys = [0] * (Nb * (Nr + 1))  # creates an array of 44 round keys
    for i in range(Nk):
        round_keys[i] = key_words[i]
    i = Nk
    while i < len(round_keys):
        temp = round_keys[i - 1]
        if i % Nk == 0:
            temp = SubWord(RotWord(temp)) ^ int(rcon(i // Nk), 16)  
            temp = format(temp, 'x')    # converts int value back to hex
        # XOR with the word Nk positions back
        round_keys[i] = format(int(round_keys[i - Nk], 16) ^ int(temp, 16), '08x')  # ensures each word has 8 hex characters 
        i += 1
    return round_keys

def AddRoundKey(state, round_key):  
    for i in range(4):
        for j in range(4): # state is 4x4 matrix,round key is 1 dimentional array of 4 round keys 
            state[i][j] = hex(int(state[i][j], 16) ^ int(round_key[i][2 * j:2 * (j + 1)], 16))[2:].zfill(2)    
            
def SubBytes(state):
    for i in range(4):
        for j in range(4):  # substitute every byte from Sbox table
            state[i][j] = format(Sbox(int(state[i][j], 16)), '02x')
            
def ShiftRows(state):
    # Need to transpose the state matrix so it gets shifted correctly
    state = list(map(list, zip(*state)))
    for i in range(1, 4):
        state[i] = state[i][i:] + state[i][:i]
    # after shifting, transpose back
    state = list(map(list, zip(*state)))  
    return state

def MixColumns(state):
    #take each column and mix it
    for i in range(4):
        s0 = int(state[i][0], 16)   
        s1 = int(state[i][1], 16)
        s2 = int(state[i][2], 16)
        s3 = int(state[i][3], 16)
        # mix each column and format back to hex
        state[i][0] = format(gmult(0x02, s0) ^ gmult(0x03, s1) ^ s2 ^ s3 , '02x')
        state[i][1] = format(s0 ^ gmult(0x02, s1) ^ gmult(0x03, s2) ^ s3 , '02x')
        state[i][2] = format(s0 ^ s1 ^ gmult(0x02, s2) ^ gmult(0x03, s3) , '02x')
        state[i][3] = format(gmult(0x03, s0) ^ s1 ^ s2 ^ gmult(0x02, s3) , '02x')
# Function to multiply two numbers in GF(2^8)
def gmult(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        a &= 0xFF  # Keep only the lowest 8 bits of the result
        if hi_bit_set:
            a ^= 0x1b  # XOR with the irreducible polynomial (x^8 + x^4 + x^3 + x + 1)
        b >>= 1
    return p 

def Encypher(state,round_keys,Nk=4,Nb=4,Nr=10):
    
    AddRoundKey(state,round_keys[0:4])    # give first 4 round keys
    start_index = 0
    for round in range (1,Nr):
        start_index += Nk
        SubBytes(state)
        state = ShiftRows(state)
        MixColumns(state)
        AddRoundKey(state, round_keys[start_index:start_index+4])   # give next 4 round keys
    SubBytes(state)
    state = ShiftRows(state)
    AddRoundKey(state,round_keys[40:44])  # give last 4 round keys
    return state
# return back 4x4 matrix of cyphered text
def getEncypheredText(inputArray,round_keys):
    resultArray = Encypher(inputArray,round_keys)
    return resultArray

def InvShiftRows(state):
    state = list(map(list, zip(*state)))
    for i in range(1, 4):
        state[i] = state[i][-i:] + state[i][:-i]
    state = list(map(list, zip(*state)))
    return state
def InvSubBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = format(InvSbox(int(state[i][j], 16)), '02x')
def InvMixColumns(state):
    #state = list(map(list, zip(*state)))
    for i in range(4):
        s0 = int(state[i][0], 16)
        s1 = int(state[i][1], 16)
        s2 = int(state[i][2], 16)
        s3 = int(state[i][3], 16)

        state[i][0] = format(gmult(0x0e, s0) ^ gmult(0x0b, s1) ^ gmult(0x0d, s2) ^ gmult(0x09, s3), '02x')
        state[i][1] = format(gmult(0x09, s0) ^ gmult(0x0e, s1) ^ gmult(0x0b, s2) ^ gmult(0x0d, s3), '02x')
        state[i][2] = format(gmult(0x0d, s0) ^ gmult(0x09, s1) ^ gmult(0x0e, s2) ^ gmult(0x0b, s3), '02x')
        state[i][3] = format(gmult(0x0b, s0) ^ gmult(0x0d, s1) ^ gmult(0x09, s2) ^ gmult(0x0e, s3), '02x')

    #state = list(map(list, zip(*state)))
    #return state
def Decypher(state, round_keys, Nk=4, Nb=4, Nr=10): 
    AddRoundKey(state, round_keys[40:44])   # take last 4 round keys
    for round in range(Nr - 1, 0, -1):      # start from 9 and go down to 1
        state = InvShiftRows(state)
        InvSubBytes(state)
        AddRoundKey(state, round_keys[round * Nk:(round + 1) * Nk])
        InvMixColumns(state)
    state = InvShiftRows(state)
    InvSubBytes(state)
    AddRoundKey(state, round_keys[0:4])     # take first 4 round keys
    return state
def getUncypheredText(cypheredArray,round_keys):   # return back 4x4 matrix of plain text
    plainArray = Decypher(cypheredArray,round_keys)
    return plainArray