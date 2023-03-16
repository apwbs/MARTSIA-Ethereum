# docker run --rm -it --network host orlenyslp/caterpillar-demo:v1

import web3
import time
import reader

web3 = web3.Web3(web3.Web3.HTTPProvider("http://localhost:8545"))

block = web3.eth.getBlock('latest', True)

smart_contract = '0x9341ab6d297f1e2c0ca27d8adfff9ae161af991c'
smart_contract = web3.toChecksumAddress(smart_contract)


def transactions_monitoring_manually():
    for transaction in block.transactions:
        print(transaction)
        input = transaction['input']
        message_ID = input[10:138]
        message_ID = int(message_ID, 16)
        print('message_ID:', message_ID)
        ipfs_link = input[138:]
        ipfs_link = bytes.fromhex(ipfs_link).decode('utf-8')
        print('ipfs_link:', ipfs_link)


def transactions_monitoring_automatically():
    min_round = 0
    while True:
        try:
            block = web3.eth.getBlock(min_round, True)
            for transaction in block.transactions:
                print(transaction)
                print()
                # if transaction['to'] == smart_contract:
                #     input = transaction['input']
                #     input_function = input[2:10]
                #     if input_function == '07464b3d' or input_function == '978ba02b' or input_function == '004ab00e':
                #         message_ID = input[10:138]
                #         message_ID = int(message_ID, 16)
                #         print('message_ID:', message_ID)
                #         ipfs_link = input[138:]
                #         ipfs_link = bytes.fromhex(ipfs_link).decode('utf-8')
                #         print('ipfs_link:', ipfs_link)
                #         print(transaction)
                #         print()
                    # reader.set_message_id(message_ID)
            min_round = min_round + 1
        except:
            print('waiting', min_round)
            time.sleep(2)


if __name__ == "__main__":
    # transactions_monitoring_manually()
    transactions_monitoring_automatically()
