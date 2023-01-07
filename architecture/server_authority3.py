import socket
import ssl
import threading
import random
from datetime import datetime
from hashlib import sha512
import block_int
import authority3_keygeneration
import ipfshttpclient
import sqlite3

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

HEADER = 64
PORT = 5060
server_cert = 'client-server/Keys/server.crt'
server_key = 'client-server/Keys/server.key'
client_certs = 'client-server/Keys/client.crt'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

"""
creation and connection of the secure channel using SSL protocol
"""
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)
bindsocket = socket.socket()
bindsocket.bind(ADDR)
bindsocket.listen(5)

"""
function triggered by the client handler. Here starts the ciphering of the message with the policy.
"""


def generate_key_auth3(gid, process_instance_id, reader_address):
    return authority3_keygeneration.generate_user_key(gid, process_instance_id, reader_address)


def generate_number_to_sign(process_instance_id, reader_address):
    # Connection to SQLite3 authority3 database
    connection = sqlite3.connect('files/authority3/authority3.db')
    x = connection.cursor()

    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    number_to_sign = random.randint(1, 2 ** 64)
    x.execute("INSERT OR IGNORE INTO handshake_numbers VALUES (?,?,?)",
              (process_instance_id, reader_address, str(number_to_sign)))
    connection.commit()
    return number_to_sign


def check_handshake(process_instance_id, reader_address, signature):
    connection = sqlite3.connect('files/authority3/authority3.db')
    x = connection.cursor()

    x.execute("SELECT * FROM handshake_numbers WHERE process_instance=? AND reader_address=?",
              (process_instance_id, reader_address))
    result = x.fetchall()
    number_to_sign = result[0][2]
    msg = str(number_to_sign).encode()
    public_key_ipfs_link = block_int.retrieve_publicKey_readers(reader_address)
    getfile = api.cat(public_key_ipfs_link)
    getfile = getfile.split(b'###')
    public_key_n = int(getfile[1].decode('utf-8'))
    public_key_e = int(getfile[2].decode('utf-8').rstrip('"'))
    if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        hashFromSignature = pow(int(signature), public_key_e, public_key_n)
        print("Signature valid:", hash == hashFromSignature)
        return hash == hashFromSignature


"""
function that handles the requests from the clients. There is only one request possible, namely the 
ciphering of a message with a policy.
"""


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            # print(f"[{addr}] {msg}")
            # conn.send("Msg received!".encode(FORMAT))
            message = msg.split('||')
            if message[0] == "Auth-3 - Start handshake":
                number_to_sign = generate_number_to_sign(message[1], message[2])
                conn.send(b'number to sign: ' + str(number_to_sign).encode())
            if message[0] == "Auth-3 - Generate your part of my key":
                if check_handshake(message[2], message[3], message[4]):
                    user_sk3 = generate_key_auth3(message[1], message[2], message[3])
                    conn.send(user_sk3)

    conn.close()


"""
main function starting the server. It listens on a port and waits for a request from a client
"""


def start():
    bindsocket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        newsocket, fromaddr = bindsocket.accept()
        conn = context.wrap_socket(newsocket, server_side=True)
        thread = threading.Thread(target=handle_client, args=(conn, fromaddr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
