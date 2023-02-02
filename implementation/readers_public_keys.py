import rsa
from decouple import config
import ipfshttpclient
import block_int
import sqlite3
import io

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
manufacturer_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
electronics_private_key = config('READER_PRIVATEKEY_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')
mechanics_private_key = config('READER_PRIVATEKEY_SUPPLIER2')

reader_address = mechanics_address
private_key = mechanics_private_key

# Connection to SQLite3 reader database
conn = sqlite3.connect('files/reader/reader.db')
x = conn.cursor()


def generate_keys():
    (publicKey, privateKey) = rsa.newkeys(1024)
    publicKey_store = publicKey.save_pkcs1().decode('utf-8')
    privateKey_store = privateKey.save_pkcs1().decode('utf-8')

    f = io.StringIO()
    f.write('reader_address: ' + reader_address + '###' + publicKey_store)
    f.seek(0)

    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey_readers(reader_address, private_key, hash_file)

    # reader address not necessary because each user has one key. Since we use only one 'reader/client' for all the
    # readers, we need a distinction.
    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?)", (reader_address, privateKey_store))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?)", (reader_address, hash_file, publicKey_store))
    conn.commit()


if __name__ == "__main__":
    generate_keys()
