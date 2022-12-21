from charm.toolbox.pairinggroup import *
from maabe_class import *
import block_int
import mpc_setup
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import os

process_instance_id_env = config('PROCESS_INSTANCE_ID')

authority1_address = config('AUTHORITY1_ADDRESS')
authority1_private_key = config('AUTHORITY1_PRIVATEKEY')

authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']


def save_authorities_names(api, process_instance_id):
    name_file = 'files/authority1/authorities_names_au1_' + str(process_instance_id) + '.txt'
    with open(name_file, 'w') as ua:
        for i, addr in enumerate(authorities_list):
            ua.write('identification: ' + 'authority ' + str(i + 1) + '\n')
            ua.write('name: ' + authorities_names[i] + '\n')
            ua.write('address: ' + addr + '\n\n')

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_authority_names(authority1_address, authority1_private_key, process_instance_id, hash_file)


def initial_parameters_hashed(groupObj, process_instance_id):
    g1_1 = groupObj.random(G1)
    g2_1 = groupObj.random(G2)
    (h1_1, h2_1) = mpc_setup.commit(groupObj, g1_1, g2_1)

    with open('files/authority1/h1_1_' + str(process_instance_id) + '.txt', 'w') as h1_1w:
        h1_1w.write(h1_1)

    with open('files/authority1/h2_1_' + str(process_instance_id) + '.txt', 'w') as h2_1w:
        h2_1w.write(h2_1)

    block_int.sendHashedElements(authority1_address, authority1_private_key, process_instance_id, (h1_1, h2_1))

    g1_1_bytes = groupObj.serialize(g1_1)
    g2_1_bytes = groupObj.serialize(g2_1)

    with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'wb') as g1_1w:
        g1_1w.write(g1_1_bytes)

    with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'wb') as g2_1w:
        g2_1w.write(g2_1_bytes)


def initial_parameters(process_instance_id):
    with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'rb') as g1:
        g1_1_bytes = g1.read()

    with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'rb') as g2:
        g2_1_bytes = g2.read()

    block_int.sendElements(authority1_address, authority1_private_key, process_instance_id, (g1_1_bytes, g2_1_bytes))


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'rb') as g1:
        g1_1_bytes = g1.read()
    g1_1 = groupObj.deserialize(g1_1_bytes)

    with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'rb') as g2:
        g2_1_bytes = g2.read()
    g2_1 = groupObj.deserialize(g2_1_bytes)

    with open('files/authority1/h1_1_' + str(process_instance_id) + '.txt', 'r') as h1:
        h1 = h1.read()

    with open('files/authority1/h2_1_' + str(process_instance_id) + '.txt', 'r') as h2:
        h2 = h2.read()

    ####################
    #######AUTH2########
    ####################
    g1g2_2_hashed = block_int.retrieveHashedElements(authority2_address, process_instance_id)

    g1g2_2 = block_int.retrieveElements(authority2_address, process_instance_id)
    g1_2 = g1g2_2[0]
    g1_2 = groupObj.deserialize(g1_2)
    g2_2 = g1g2_2[1]
    g2_2 = groupObj.deserialize(g2_2)

    ####################
    #######AUTH3########
    ####################
    g1g2_3_hashed = block_int.retrieveHashedElements(authority3_address, process_instance_id)

    g1g2_3 = block_int.retrieveElements(authority3_address, process_instance_id)
    g1_3 = g1g2_3[0]
    g1_3 = groupObj.deserialize(g1_3)
    g2_3 = g1g2_3[1]
    g2_3 = groupObj.deserialize(g2_3)

    ####################
    #######AUTH4########
    ####################
    g1g2_4_hashed = block_int.retrieveHashedElements(authority4_address, process_instance_id)

    g1g2_4 = block_int.retrieveElements(authority4_address, process_instance_id)
    g1_4 = g1g2_4[0]
    g1_4 = groupObj.deserialize(g1_4)
    g2_4 = g1g2_4[1]
    g2_4 = groupObj.deserialize(g2_4)

    #############################
    ##########VALUES#############
    #############################
    hashes1 = [h1, g1g2_2_hashed[0], g1g2_3_hashed[0], g1g2_4_hashed[0]]
    hashes2 = [h2, g1g2_2_hashed[1], g1g2_3_hashed[1], g1g2_4_hashed[1]]
    com1 = [g1_1, g1_2, g1_3, g1_4]
    com2 = [g2_1, g2_2, g2_3, g2_4]
    (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)

    # setup
    public_parameters = maabe.setup(value1, value2)
    public_parameters_reduced = dict(list(public_parameters.items())[0:3])
    pp_reduced = objectToBytes(public_parameters_reduced, groupObj)

    name_file = 'files/authority1/public_parameters_authority1_' + str(process_instance_id) + '.txt'
    with open(name_file, 'wb') as ipfs:
        ipfs.write(pp_reduced)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_parameters_link(authority1_address, authority1_private_key, process_instance_id, hash_file)


def retrieve_public_parameters(process_instance_id):
    with open('files/authority1/public_parameters_authority1_' + str(process_instance_id) + '.txt', 'rb') as ppa1:
        public_parameters = ppa1.read()
    return public_parameters


def generate_pk_sk(groupObj, maabe, api, process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # authsetup 2AA
    (pk1, sk1) = maabe.authsetup(public_parameters, 'UT')
    pk1_bytes = objectToBytes(pk1, groupObj)
    sk1_bytes = objectToBytes(sk1, groupObj)

    name_file = 'files/authority1/authority_ut_pk_' + str(process_instance_id) + '.txt'
    with open(name_file, 'wb') as a1:
        a1.write(pk1_bytes)
    with open('files/authority1/private_key_au1_' + str(process_instance_id) + '.txt', 'wb') as as1:
        as1.write(sk1_bytes)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey_link(authority1_address, authority1_private_key, process_instance_id, hash_file)


def main():
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    # save_authorities_names(api, process_instance_id)
    # initial_parameters_hashed(groupObj, process_instance_id)
    # initial_parameters(process_instance_id)
    # generate_public_parameters(groupObj, maabe, api, process_instance_id)
    generate_pk_sk(groupObj, maabe, api, process_instance_id)

    # test = api.name.publish('/ipfs/' + hash_file)
    # print(test)
    # os.system('ipfs cat ' + hash_file)
    # os.system('ipfs name publish /ipfs/' + hash_file)


if __name__ == '__main__':
    main()
