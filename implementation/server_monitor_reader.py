import time
from decouple import config
import rsa
from web3 import Web3
import ipfshttpclient

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/55aa0d95a9be4261b3c676315d6abc7e"))

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')


def retrieve_key(transaction):
    if transaction['from'] == authority4_address:
        partial = bytes.fromhex(transaction['input'][2:]).decode('utf-8').split(',')
        process_instance_id = partial[1]
        ipfs_link = partial[0]
        getfile = api.cat(ipfs_link)

        info2 = [getfile[i:i + 128] for i in range(0, len(getfile), 128)]
        final_bytes = b''

        with open('files/keys_readers/private_key_' + str(electronics_address) + '.txt', 'rb') as sk1r:
            sk1 = sk1r.read()
        sk1 = sk1.split(b'###')[1]
        privateKey_usable = rsa.PrivateKey.load_pkcs1(sk1)

        for j in info2:
            message = rsa.decrypt(j, privateKey_usable)
            final_bytes = final_bytes + message

        with open('files/reader/user_sk4_' + str(process_instance_id) + '.txt', "wb") as text_file:
            text_file.write(final_bytes)

        print('key retrieved')


def transactions_monitoring():
    min_round = 8187469
    transactions = []
    while True:
        block = web3.eth.getBlock(min_round, True)
        print(block.number)
        for transaction in block.transactions:
            if transaction['hash'] not in transactions and 'input' in transaction:
                transactions.append(transaction)
        min_round = min_round + 1
        for x in transactions:
            retrieve_key(x)
            transactions.remove(x)
        time.sleep(5)


if __name__ == "__main__":
    transactions_monitoring()
