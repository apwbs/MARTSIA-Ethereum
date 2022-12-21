from charm.toolbox.pairinggroup import *
from decouple import config
import block_int
import mpc_setup
from maabe_class import *
import ipfshttpclient
from charm.core.engine.util import objectToBytes, bytesToObject

process_instance_id_env = config('PROCESS_INSTANCE_ID')

authority2_address = config('AUTHORITY2_ADDRESS')
authority2_private_key = config('AUTHORITY2_PRIVATEKEY')

authority1_address = config('AUTHORITY1_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']


def save_authorities_names(api, process_instance_id):
    name_file = 'files/authority2/authorities_names_au2_' + str(process_instance_id) + '.txt'
    with open(name_file, 'w') as ua:
        for i, addr in enumerate(authorities_list):
            ua.write('identification: ' + 'authority ' + str(i + 1) + '\n')
            ua.write('name: ' + authorities_names[i] + '\n')
            ua.write('address: ' + addr + '\n\n')

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_authority_names(authority2_address, authority2_private_key, process_instance_id, hash_file)


def initial_parameters_hashed(groupObj, process_instance_id):
    g1_2 = groupObj.random(G1)
    g2_2 = groupObj.random(G2)
    (h1_2, h2_2) = mpc_setup.commit(groupObj, g1_2, g2_2)

    with open('files/authority2/h1_2_' + str(process_instance_id) + '.txt', 'w') as h1_2w:
        h1_2w.write(h1_2)

    with open('files/authority2/h2_2_' + str(process_instance_id) + '.txt', 'w') as h2_2w:
        h2_2w.write(h2_2)

    block_int.sendHashedElements(authority2_address, authority2_private_key, process_instance_id, (h1_2, h2_2))

    g1_2_bytes = groupObj.serialize(g1_2)
    g2_2_bytes = groupObj.serialize(g2_2)

    with open('files/authority2/g1_2_' + str(process_instance_id) + '.txt', 'wb') as g1_2w:
        g1_2w.write(g1_2_bytes)

    with open('files/authority2/g2_2_' + str(process_instance_id) + '.txt', 'wb') as g2_2w:
        g2_2w.write(g2_2_bytes)


def initial_parameters(process_instance_id):
    with open('files/authority2/g1_2_' + str(process_instance_id) + '.txt', 'rb') as g1r:
        g1_2_bytes = g1r.read()

    with open('files/authority2/g2_2_' + str(process_instance_id) + '.txt', 'rb') as g2r:
        g2_2_bytes = g2r.read()

    block_int.sendElements(authority2_address, authority2_private_key, process_instance_id, (g1_2_bytes, g2_2_bytes))


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    with open('files/authority2/g1_2_' + str(process_instance_id) + '.txt', 'rb') as g1:
        g1_2_bytes = g1.read()
    g1_2 = groupObj.deserialize(g1_2_bytes)

    with open('files/authority2/g2_2_' + str(process_instance_id) + '.txt', 'rb') as g2:
        g2_2_bytes = g2.read()
    g2_2 = groupObj.deserialize(g2_2_bytes)

    with open('files/authority2/h1_2_' + str(process_instance_id) + '.txt', 'r') as h1:
        h1 = h1.read()

    with open('files/authority2/h2_2_' + str(process_instance_id) + '.txt', 'r') as h2:
        h2 = h2.read()

    ####################
    #######AUTH1########
    ####################
    g1g2_1_hashed = block_int.retrieveHashedElements(authority1_address, process_instance_id)

    g1g2_1 = block_int.retrieveElements(authority1_address, process_instance_id)
    g1_1 = g1g2_1[0]
    g1_1 = groupObj.deserialize(g1_1)
    g2_1 = g1g2_1[1]
    g2_1 = groupObj.deserialize(g2_1)

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
    hashes1 = [g1g2_1_hashed[0], h1, g1g2_3_hashed[0], g1g2_4_hashed[0]]
    hashes2 = [g1g2_1_hashed[1], h2, g1g2_3_hashed[1], g1g2_4_hashed[1]]
    com1 = [g1_1, g1_2, g1_3, g1_4]
    com2 = [g2_1, g2_2, g2_3, g2_4]
    (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)

    public_parameters = maabe.setup(value1, value2)
    public_parameters_reduced = dict(list(public_parameters.items())[0:3])
    pp_reduced = objectToBytes(public_parameters_reduced, groupObj)

    name_file = 'files/authority2/public_parameters_authority2_' + str(process_instance_id) + '.txt'
    with open(name_file, 'wb') as ipfs:
        ipfs.write(pp_reduced)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_parameters_link(authority2_address, authority2_private_key, process_instance_id, hash_file)


def retrieve_public_parameters(process_instance_id):
    with open('files/authority2/public_parameters_authority2_' + str(process_instance_id) + '.txt', 'rb') as ppa2:
        public_parameters = ppa2.read()
    return public_parameters


def generate_pk_sk(groupObj, maabe, api, process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # authsetup 2AA
    (pk2, sk2) = maabe.authsetup(public_parameters, 'OU')
    pk2_bytes = objectToBytes(pk2, groupObj)
    sk2_bytes = objectToBytes(sk2, groupObj)

    name_file = 'files/authority2/authority_ou_pk_' + str(process_instance_id) + '.txt'
    with open(name_file, 'wb') as a2:
        a2.write(pk2_bytes)
    with open('files/authority2/private_key_au2_' + str(process_instance_id) + '.txt', 'wb') as as2:
        as2.write(sk2_bytes)

    new_file = api.add(name_file)
    hash_file = new_file['Hash']
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey_link(authority2_address, authority2_private_key, process_instance_id, hash_file)


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


if __name__ == '__main__':
    main()
