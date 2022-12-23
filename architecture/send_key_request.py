from decouple import config
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/55aa0d95a9be4261b3c676315d6abc7e"))

process_instance_id = config('PROCESS_INSTANCE_ID')

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
manufacturer_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
electronics_private_key = config('READER_PRIVATEKEY_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')
mechanics_private_key = config('READER_PRIVATEKEY_SUPPLIER2')

address_requesting = electronics_address
private_key_requesting = electronics_private_key


def send_key_request():
    nonce = web3.eth.getTransactionCount(address_requesting)

    tx = {
        'nonce': nonce,
        'to': authority4_address,
        'value': 0,
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'data': web3.toHex(b'generate your part of my key,bob,' + process_instance_id.encode())
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key_requesting)

    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'tx_hash: {web3.toHex(tx_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    # print(tx_receipt)


if __name__ == "__main__":
    send_key_request()
    