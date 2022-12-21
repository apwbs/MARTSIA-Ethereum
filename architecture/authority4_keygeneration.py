from charm.toolbox.pairinggroup import *
from decouple import config
from maabe_class import *
from charm.core.engine.util import objectToBytes, bytesToObject
import block_int
import ipfshttpclient
import json


def retrieve_public_parameters(process_instance_id):
    with open('files/authority4/public_parameters_authority4_' + str(process_instance_id) + '.txt', 'rb') as ppa4:
        public_parameters = ppa4.read()
    return public_parameters


def generate_user_key(gid, process_instance_id, reader_address):
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    with open('files/authority4/private_key_au4_' + str(process_instance_id) + '.txt', 'rb') as sk4r:
        sk4 = sk4r.read()
    sk4 = bytesToObject(sk4, groupObj)

    # keygen Bob
    attributes_ipfs_link = block_int.retrieve_users_attributes(process_instance_id)
    getfile = api.cat(attributes_ipfs_link)
    getfile = getfile.split(b'\n')
    attributes_dict = json.loads(getfile[1].decode('utf-8'))
    user_attr4 = attributes_dict[reader_address]
    user_attr4 = [k for k in user_attr4 if k.endswith('@TU')]
    user_sk4 = maabe.multiple_attributes_keygen(public_parameters, sk4, gid, user_attr4)
    user_sk4_bytes = objectToBytes(user_sk4, groupObj)
    return user_sk4_bytes
