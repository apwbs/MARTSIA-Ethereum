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
import sqlite3

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

dataOwner_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
dataOwner_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')

process_instance_id_env = config('PROCESS_INSTANCE_ID')

# Connection to SQLite3 data_owner database
conn = sqlite3.connect('files/data_owner/data_owner.db')
x = conn.cursor()


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
    pk1 = pk1.decode('utf-8').rstrip('"').lstrip('"')
    pk1 = pk1.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (process_instance_id, 'Auth-1', data[2], pk1))
    conn.commit()

    data = retrieve_data(authority2_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk2 = api.cat(data[2])
    pk2 = pk2.decode('utf-8').rstrip('"').lstrip('"')
    pk2 = pk2.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (process_instance_id, 'Auth-2', data[2], pk2))
    conn.commit()

    data = retrieve_data(authority3_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk3 = api.cat(data[2])
    pk3 = pk3.decode('utf-8').rstrip('"').lstrip('"')
    pk3 = pk3.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (process_instance_id, 'Auth-3', data[2], pk3))
    conn.commit()

    data = retrieve_data(authority4_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk4 = api.cat(data[2])
    pk4 = pk4.decode('utf-8').rstrip('"').lstrip('"')
    pk4 = pk4.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (process_instance_id, 'Auth-4', data[2], pk4))
    conn.commit()

    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
        getfile = getfile.encode('utf-8')
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (process_instance_id, check_parameters[0], getfile))
        conn.commit()


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    public_parameters = result[0][2]
    return public_parameters


def main(groupObj, maabe, api, process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (process_instance_id, 'Auth-1'))
    result = x.fetchall()
    pk1 = result[0][3]
    pk1 = bytesToObject(pk1, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (process_instance_id, 'Auth-2'))
    result = x.fetchall()
    pk2 = result[0][3]
    pk2 = bytesToObject(pk2, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (process_instance_id, 'Auth-3'))
    result = x.fetchall()
    pk3 = result[0][3]
    pk3 = bytesToObject(pk3, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (process_instance_id, 'Auth-4'))
    result = x.fetchall()
    pk4 = result[0][3]
    pk4 = bytesToObject(pk4, groupObj)

    # public keys authorities
    pk = {'UT': pk1, 'OU': pk2, 'OT': pk3, 'TU': pk4}

    f = open('files/data.json')
    data = json.load(f)
    access_policy = ['(6029956255136507926@UT and 6029956255136507926@OU and 6029956255136507926@OT and '
                     '6029956255136507926@TU) and (MANUFACTURER@UT or '
                     'SUPPLIER@OU)',
                     '(6029956255136507926@UT and 6029956255136507926@OU and 6029956255136507926@OT and '
                     '6029956255136507926@TU) and (MANUFACTURER@UT or ('
                     'SUPPLIER@OU and ELECTRONICS@OT)',
                     '(6029956255136507926@UT and 6029956255136507926@OU and 6029956255136507926@OT and '
                     '6029956255136507926@TU) and (MANUFACTURER@UT or ('
                     'SUPPLIER@OU and MECHANICS@TU)']

    entries = [['ID', 'SortAs', 'GlossTerm'], ['Acronym', 'Abbrev'], ['Specs', 'Dates']]

    # access_policy = ['(6379627265815999091@UT and 6379627265815999091@OU '
    #                  'and 6379627265815999091@OT and 6379627265815999091@TU) '
    #                  'and (MANUFACTURER@UT or SUPPLIER@OU)']
    #
    # entries = [list(data.keys())]

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
    metadata = {'sender': dataOwner_address, 'process_instance_id': int(process_instance_id),
                'message_id': message_id}
    print(f'message id: {message_id}')

    json_total = {'metadata': metadata, 'header': header, 'body': json_file_ciphered}

    # encoded = cryptocode.encrypt("Ciao Marzia!", str(key_encrypt1))

    hash_file = api.add_json(json_total)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
              (process_instance_id, str(message_id), hash_file, str(json_total)))
    conn.commit()

    block_int.send_MessageIPFSLink(dataOwner_address, dataOwner_private_key, message_id, hash_file)


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    # generate_pp_pk(process_instance_id)
    main(groupObj, maabe, api, process_instance_id)
