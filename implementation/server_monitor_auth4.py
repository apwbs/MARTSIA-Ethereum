import time
from decouple import config
import authority4_keygeneration
import rsa
import block_int
from web3 import Web3
import ipfshttpclient

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

authority4_address = config('AUTHORITY4_ADDRESS')
authority4_private_key = config('AUTHORITY4_PRIVATEKEY')

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/55aa0d95a9be4261b3c676315d6abc7e"))


def send_ipfs_link(reader_address, process_instance_id, hash_file):
    nonce = web3.eth.getTransactionCount(authority4_address)

    tx = {
        'nonce': nonce,
        'to': reader_address,
        'value': 0,
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'data': web3.toHex(hash_file.encode() + b',' + str(process_instance_id).encode())
    }

    signed_tx = web3.eth.account.sign_transaction(tx, authority4_private_key)

    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'tx_hash: {web3.toHex(tx_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    # print(tx_receipt)


def generate_key(x):
    gid = bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[1]
    process_instance_id = int(bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[2])
    reader_address = x['from']
    key = authority4_keygeneration.generate_user_key(gid, process_instance_id, reader_address)
    cipher_generated_key(reader_address, process_instance_id, key)


def cipher_generated_key(reader_address, process_instance_id, generated_ma_key):
    public_key_ipfs_link = block_int.retrieve_reader_public_key(reader_address)
    getfile = api.cat(public_key_ipfs_link)
    getfile = getfile.split(b'###')
    if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
        publicKey_usable = rsa.PublicKey.load_pkcs1(getfile[1])

        info = [generated_ma_key[i:i + 117] for i in range(0, len(generated_ma_key), 117)]

        name_file = 'files/authority4/generated_key_ciphered_' + str(reader_address) + '_' \
                    + str(process_instance_id) + '.txt'

        text_in_file = b''
        for part in info:
            crypto = rsa.encrypt(part, publicKey_usable)
            text_in_file = text_in_file + crypto
        with open(name_file, 'wb') as ipfs:
            ipfs.write(text_in_file)

        new_file = api.add(name_file)
        hash_file = new_file['Hash']
        print(f'ipfs hash: {hash_file}')

        send_ipfs_link(reader_address, process_instance_id, hash_file)


def transactions_monitoring():
    min_round = 8187465
    transactions = []
    note = 'generate your part of my key'
    while True:
        block = web3.eth.getBlock(min_round, True)
        print(block.number)
        for transaction in block.transactions:
            if transaction['to'] == authority4_address and transaction['hash'] not in transactions \
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
