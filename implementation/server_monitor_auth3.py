import time
from decouple import config
import authority3_keygeneration
import rsa
import block_int
from web3 import Web3
import ipfshttpclient
import io
import json
import base64

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

authority3_address = config('AUTHORITY3_ADDRESS')
authority3_private_key = config('AUTHORITY3_PRIVATEKEY')

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))


def send_ipfs_link(reader_address, process_instance_id, hash_file):
    nonce = web3.eth.getTransactionCount(authority3_address)

    tx = {
        'nonce': nonce,
        'to': reader_address,
        'value': 0,
        'gas': 40000,
        'gasPrice': web3.toWei(web3.eth.gasPrice, 'wei'),
        'data': web3.toHex(hash_file.encode() + b',' + str(process_instance_id).encode())
    }

    signed_tx = web3.eth.account.sign_transaction(tx, authority3_private_key)

    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'tx_hash: {web3.toHex(tx_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    # print(tx_receipt)


def generate_key(x):
    gid = bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[1]
    process_instance_id = int(bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[2])
    reader_address = x['from']
    key = authority3_keygeneration.generate_user_key(gid, process_instance_id, reader_address)
    cipher_generated_key(reader_address, process_instance_id, key)


def cipher_generated_key(reader_address, process_instance_id, generated_ma_key):
    public_key_ipfs_link = block_int.retrieve_publicKey_readers(reader_address)
    getfile = api.cat(public_key_ipfs_link)
    getfile = getfile.split(b'###')
    if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
        publicKey_usable = rsa.PublicKey.load_pkcs1(getfile[1].rstrip(b'"').replace(b'\\n', b'\n'))

        info = [generated_ma_key[i:i + 117] for i in range(0, len(generated_ma_key), 117)]

        f = io.BytesIO()
        for part in info:
            crypto = rsa.encrypt(part, publicKey_usable)
            f.write(crypto)
        f.seek(0)

        file_to_str = f.read()
        j = base64.b64encode(file_to_str).decode('ascii')
        s = json.dumps(j)
        hash_file = api.add_json(s)
        print(f'ipfs hash: {hash_file}')

        send_ipfs_link(reader_address, process_instance_id, hash_file)


def transactions_monitoring():
    min_round = 8444123
    transactions = []
    note = 'generate your part of my key'
    while True:
        block = web3.eth.getBlock(min_round, True)
        print(block.number)
        for transaction in block.transactions:
            if transaction['to'] == authority3_address and transaction['hash'] not in transactions \
                    and 'input' in transaction:
                if bytes.fromhex(transaction['input'][2:]).decode('utf-8').split(',')[0] == note:
                    transactions.append(transaction)
        min_round = min_round + 1
        for x in transactions:
            generate_key(x)
            transactions.remove(x)
        time.sleep(5)


if __name__ == "__main__":
    transactions_monitoring()
