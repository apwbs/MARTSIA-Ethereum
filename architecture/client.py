import socket
import ssl
from decouple import config
from hashlib import sha512
import sqlite3

# Connection to SQLite3 reader database
connection = sqlite3.connect('files/reader/reader.db')
x = connection.cursor()

HEADER = 64
PORT = 5065
FORMAT = 'utf-8'
server_sni_hostname = 'example.com'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "172.17.0.2"
ADDR = (SERVER, PORT)
server_cert = 'client-server/Keys/server.crt'
client_cert = 'client-server/Keys/client.crt'
client_key = 'client-server/Keys/client.key'

"""
creation and connection of the secure channel using SSL protocol
"""

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect(ADDR)


def sign_number(authority_invoked):
    x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND authority_name=?",
              (process_instance_id, authority_invoked))
    result = x.fetchall()
    number_to_sign = result[0][2]

    x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = x.fetchall()
    private_key = result[0]

    private_key_n = int(private_key[1])
    private_key_d = int(private_key[2])

    msg = bytes(str(number_to_sign), 'utf-8')
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, private_key_d, private_key_n)
    # print("Signature:", hex(signature))
    return signature


"""
function to handle the sending and receiving messages.
"""


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    # print(send_length)
    conn.send(message)
    receive = conn.recv(6000).decode(FORMAT)
    if len(receive) != 0:
        # if receive[:15] == 'number to sign:':
        #     x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?)",
        #               (process_instance_id, authority, receive[16:]))
        #     connection.commit()

        x.execute("INSERT OR IGNORE INTO authorities_generated_decription_keys VALUES (?,?,?)",
                  (process_instance_id, authority, receive))
        connection.commit()


manufacturer = config('DATAOWNER_MANUFACTURER_ADDRESS')
electronics = config('READER_ADDRESS_SUPPLIER1')
mechanics = config('READER_ADDRESS_SUPPLIER2')
process_instance_id_env = config('PROCESS_INSTANCE_ID')

reader_address = electronics
process_instance_id = int(process_instance_id_env)
gid = "bob"

authority = 'Auth-4'

# send(authority + " - Start handshake||" + str(process_instance_id) + '||' + reader_address)

signature_sending = sign_number(authority)

send(authority + " - Generate your part of my key||" + gid + '||' + str(process_instance_id) + '||' + reader_address
     + '||' + str(signature_sending))

# exit()
# input()

send(DISCONNECT_MESSAGE)
