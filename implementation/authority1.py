from charm.toolbox.pairinggroup import *
from maabe_class import *
import block_int
import mpc_setup
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import io
import sqlite3
import os

process_instance_id_env = config('PROCESS_INSTANCE_ID')

authority1_address = config('AUTHORITY1_ADDRESS')
authority1_private_key = config('AUTHORITY1_PRIVATEKEY')

authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']

# Connection to SQLite3 authority1 database
conn = sqlite3.connect('files/authority1/authority1.db')
x = conn.cursor()


def save_authorities_names(api, process_instance_id):
    f = io.StringIO()
    for i, addr in enumerate(authorities_list):
        f.write('identification: ' + 'authority ' + str(i + 1) + '\n')
        f.write('name: ' + str(authorities_names[i]) + '\n')
        f.write('address: ' + addr + '\n\n')
    f.seek(0)

    file_to_str = f.read()
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO authority_names VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    block_int.send_authority_names(authority1_address, authority1_private_key, process_instance_id, hash_file)


def initial_parameters_hashed(groupObj, process_instance_id):
    g1_1 = groupObj.random(G1)
    g2_1 = groupObj.random(G2)
    (h1_1, h2_1) = mpc_setup.commit(groupObj, g1_1, g2_1)

    x.execute("INSERT OR IGNORE INTO h_values VALUES (?,?,?)", (process_instance_id, h1_1, h2_1))
    conn.commit()

    block_int.sendHashedElements(authority1_address, authority1_private_key, process_instance_id, (h1_1, h2_1))

    g1_1_bytes = groupObj.serialize(g1_1)
    g2_1_bytes = groupObj.serialize(g2_1)

    x.execute("INSERT OR IGNORE INTO g_values VALUES (?,?,?)", (process_instance_id, g1_1_bytes, g2_1_bytes))
    conn.commit()


def initial_parameters(process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_1_bytes = result[0][1]
    g2_1_bytes = result[0][2]

    # if we want to save gas, we can put the values in an IPFS file and store its link instead of the values in plain
    block_int.sendElements(authority1_address, authority1_private_key, process_instance_id, (g1_1_bytes, g2_1_bytes))


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_1_bytes = result[0][1]
    g1_1 = groupObj.deserialize(g1_1_bytes)
    g2_1_bytes = result[0][2]
    g2_1 = groupObj.deserialize(g2_1_bytes)

    x.execute("SELECT * FROM h_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    h1 = result[0][1]
    h2 = result[0][2]

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

    file_to_str = pp_reduced.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    block_int.send_parameters_link(authority1_address, authority1_private_key, process_instance_id, hash_file)


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    public_parameters = result[0][2].encode()
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

    file_to_str = pk1_bytes.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO private_keys VALUES (?,?)", (process_instance_id, sk1_bytes))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO public_keys VALUES (?,?,?)", (process_instance_id, hash_file, pk1_bytes))
    conn.commit()

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
