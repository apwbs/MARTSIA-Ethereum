from decouple import config
from Crypto.PublicKey import RSA
from hashlib import sha512
import ipfshttpclient
import block_int
import sqlite3
import io
import argparse

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

parser = argparse.ArgumentParser(description='Reader name')
parser.add_argument('-r', '--reader', type=str, default='MANUFACTURER',help='Reader name')

args = parser.parse_args()
reader_address = config(args.reader + '_ADDRESS')
private_key = config(args.reader + '_PRIVATEKEY')

# Connection to SQLite3 reader database
conn = sqlite3.connect('files/reader/reader.db')
x = conn.cursor()


def generate_keys():
    keyPair = RSA.generate(bits=1024)
    # print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    # print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")

    f = io.StringIO()
    f.write('reader_address: ' + reader_address + '###')
    f.write(str(keyPair.n) + '###' + str(keyPair.e))
    f.seek(0)

    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey_readers(reader_address, private_key, hash_file)

    # reader address not necessary because each user has one key. Since we use only one 'reader/client' for all the
    # readers, we need a distinction.
    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)", (reader_address, str(keyPair.n), str(keyPair.d)))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
              (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
    conn.commit()

    


if __name__ == "__main__":
    generate_keys()
    