from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
import block_int
from decouple import config
import ipfshttpclient
import json
from maabe_class import *
from datetime import datetime
import random


authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

dataOwner_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
dataOwner_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')

process_instance_id_env = config('PROCESS_INSTANCE_ID')


def retrieve_data(authority_address, process_instance_id):
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    public_key = block_int.retrieve_publicKey_link(authority_address, process_instance_id)
    return authorities, public_parameters, public_key


def generate_pp_pk(process_instance_id):
    check_authorities = []
    check_parameters = []

    data = retrieve_data(authority1_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk1 = api.cat(data[2])
    with open('files/data_owner/public_key_auth1_' + str(process_instance_id) + '.txt', 'wb') as ppw:
        ppw.write(pk1)

    data = retrieve_data(authority2_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk2 = api.cat(data[2])
    with open('files/data_owner/public_key_auth2_' + str(process_instance_id) + '.txt', 'wb') as ppw:
        ppw.write(pk2)

    data = retrieve_data(authority3_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk3 = api.cat(data[2])
    with open('files/data_owner/public_key_auth3_' + str(process_instance_id) + '.txt', 'wb') as ppw:
        ppw.write(pk3)

    data = retrieve_data(authority4_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk4 = api.cat(data[2])
    with open('files/data_owner/public_key_auth4_' + str(process_instance_id) + '.txt', 'wb') as ppw:
        ppw.write(pk4)

    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        with open('files/data_owner/public_parameters_dataowner_' + str(process_instance_id) + '.txt', 'wb') as ppw:
            ppw.write(getfile)


def retrieve_public_parameters(process_instance_id):
    with open('files/data_owner/public_parameters_dataowner_' + str(process_instance_id) + '.txt', 'rb') as ppr:
        public_parameters = ppr.read()
    return public_parameters


def main(process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    with open('files/data_owner/public_key_auth1_' + str(process_instance_id) + '.txt', 'rb') as pk1r:
        pk1 = pk1r.read()
    pk1 = bytesToObject(pk1, groupObj)

    with open('files/data_owner/public_key_auth2_' + str(process_instance_id) + '.txt', 'rb') as pk2r:
        pk2 = pk2r.read()
    pk2 = bytesToObject(pk2, groupObj)

    with open('files/data_owner/public_key_auth3_' + str(process_instance_id) + '.txt', 'rb') as pk3r:
        pk3 = pk3r.read()
    pk3 = bytesToObject(pk3, groupObj)

    with open('files/data_owner/public_key_auth4_' + str(process_instance_id) + '.txt', 'rb') as pk4r:
        pk4 = pk4r.read()
    pk4 = bytesToObject(pk4, groupObj)

    # public keys authorities
    pk = {'UT': pk1, 'OU': pk2, 'OT': pk3, 'TU': pk4}

    f = open('files/data.json')
    data = json.load(f)
    # access_policy = ['(1387640806@UT and 1387640806@OU and 1387640806@OT and 1387640806@TU) and (MANUFACTURER@UT or '
    #                  'SUPPLIER@OU)',
    #                  '(1387640806@UT and 1387640806@OU and 1387640806@OT and 1387640806@TU) and (MANUFACTURER@UT or ('
    #                  'SUPPLIER@OU and ELECTRONICS@OT)',
    #                  '(1387640806@UT and 1387640806@OU and 1387640806@OT and 1387640806@TU) and (MANUFACTURER@UT or ('
    #                  'SUPPLIER@OU and MECHANICS@TU)']
    #
    # entries = [['ID', 'SortAs', 'GlossTerm'], ['Acronym', 'Abbrev'], ['Specs', 'Dates']]

    access_policy = ['(1387640806@UT and 1387640806@OU and 1387640806@OT and 1387640806@TU) and (MANUFACTURER@UT or '
                     'SUPPLIER@OU)']

    entries = [list(data.keys())]

    if len(access_policy) != len(entries):
        print('ERROR: The number of policies and entries is different')
        exit()

    keys = []
    header = []
    for i in range(len(entries)):
        key_group = groupObj.random(GT)
        key_encrypt = groupObj.serialize(key_group)
        keys.append(key_encrypt)
        key_encrypt_deser = groupObj.deserialize(key_encrypt)

        ciphered_key = maabe.encrypt(public_parameters, pk, key_encrypt_deser, access_policy[i])
        ciphered_key_bytes = objectToBytes(ciphered_key, groupObj)
        ciphered_key_bytes_string = ciphered_key_bytes.decode('utf-8')

        ## Possibility to clean the code here. This check can be done outside the 'for loop'
        if len(access_policy) == len(entries) == 1:
            dict_pol = {'CipheredKey': ciphered_key_bytes_string, 'Fields': entries[i]}
            header.append(dict_pol)
        else:
            now = datetime.now()
            now = int(now.strftime("%Y%m%d%H%M%S%f"))
            random.seed(now)
            slice_id = random.randint(1, 2 ** 64)
            dict_pol = {'Slice_id': slice_id, 'CipheredKey': ciphered_key_bytes_string, 'Fields': entries[i]}
            print(f'slice id {i}: {slice_id}')
            header.append(dict_pol)

    json_file_ciphered = {}
    for i, entry in enumerate(entries):
        ciphered_fields = []
        for field in entry:
            cipher_field = cryptocode.encrypt(field, str(keys[i]))
            ciphered_fields.append(cipher_field)
            cipher = cryptocode.encrypt(data[field], str(keys[i]))
            json_file_ciphered[cipher_field] = cipher
        header[i]['Fields'] = ciphered_fields

    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    message_id = random.randint(1, 2 ** 64)
    metadata = {'process_instance_id': int(process_instance_id), 'message_id': message_id}
    print(f'message id: {message_id}')

    json_total = {'metadata': metadata, 'header': header, 'body': json_file_ciphered}

    # encoded = cryptocode.encrypt("Ciao Marzia!", str(key_encrypt1))

    name_file = 'files/key&ciphertext.txt'
    with open(name_file, 'w', encoding='utf-8') as f:
        json.dump(json_total, f, ensure_ascii=False, indent=4)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_MessageIPFSLink(dataOwner_address, dataOwner_private_key, message_id, hash_file)


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    # generate_pp_pk(process_instance_id)
    main(process_instance_id)
