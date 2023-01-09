import time
from decouple import config
import rsa
from web3 import Web3
import ipfshttpclient
import sqlite3
import base64
import json

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')

# Connection to SQLite3 data_owner database
conn = sqlite3.connect('files/reader/reader.db')
x = conn.cursor()

reader_address = electronics_address
authority_address = authority2_address


def retrieve_key(transaction):
    if transaction['from'] == authority_address:
        partial = bytes.fromhex(transaction['input'][2:]).decode('utf-8').split(',')
        process_instance_id = partial[1]
        ipfs_link = partial[0]
        getfile = api.cat(ipfs_link)
        getfile = getfile.decode('utf-8').replace(r'\"', r'')
        j2 = json.loads(getfile)
        data2 = base64.b64decode(j2)

        x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
        result = x.fetchall()
        pk = result[0][1]
        privateKey_usable = rsa.PrivateKey.load_pkcs1(pk)

        info2 = [data2[i:i + 128] for i in range(0, len(data2), 128)]
        final_bytes = b''

        for j in info2:
            message = rsa.decrypt(j, privateKey_usable)
            final_bytes = final_bytes + message

        x.execute("INSERT OR IGNORE INTO authorities_generated_decription_keys VALUES (?,?,?,?)",
                  (str(process_instance_id), authority_address, ipfs_link, final_bytes))
        conn.commit()

        print('key retrieved')


def transactions_monitoring():
    min_round = 8283532
    transactions = []
    while True:
        block = web3.eth.getBlock(min_round, True)
        print(block.number)
        for transaction in block.transactions:
            if transaction['to'] == reader_address and transaction['hash'] not in transactions and 'input' in transaction:
                transactions.append(transaction)
        min_round = min_round + 1
        for x in transactions:
            retrieve_key(x)
            transactions.remove(x)
        time.sleep(5)


if __name__ == "__main__":
    transactions_monitoring()
