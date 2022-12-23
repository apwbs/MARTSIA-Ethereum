import rsa
from decouple import config
import ipfshttpclient
import block_int

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
manufacturer_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
electronics_private_key = config('READER_PRIVATEKEY_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')
mechanics_private_key = config('READER_PRIVATEKEY_SUPPLIER2')

reader_address = electronics_address
private_key = electronics_private_key


def generate_keys():
    (publicKey, privateKey) = rsa.newkeys(1024)
    publicKey_store = publicKey.save_pkcs1().decode('utf-8')
    privateKey_store = privateKey.save_pkcs1().decode('utf-8')

    name_file1 = 'files/keys_readers/private_key_' + str(reader_address) + '.txt'
    with open(name_file1, 'w') as ipfs:
        ipfs.write('reader_address: ' + reader_address + '###')
        ipfs.write(privateKey_store)

    name_file = 'files/keys_readers/public_key_' + str(reader_address) + '.txt'
    with open(name_file, 'w') as ipfs:
        ipfs.write('reader_address: ' + reader_address + '###')
        ipfs.write(publicKey_store)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_reader_public_key(reader_address, private_key, hash_file)


if __name__ == "__main__":
    generate_keys()
