from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
import block_int
import ipfshttpclient
import json
from maabe_class import *
from decouple import config

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def retrieve_data(authority_address, process_instance_id):
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    return authorities, public_parameters


def generate_public_parameters(process_instance_id):
    check_authorities = []
    check_parameters = []

    data = retrieve_data(authority1_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority2_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority3_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    data = retrieve_data(authority4_address, process_instance_id)
    check_authorities.append(data[0])
    check_parameters.append(data[1])

    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        with open('files/reader/public_parameters_reader_' + str(process_instance_id) + '.txt', 'wb') as ppw:
            ppw.write(getfile)


def retrieve_public_parameters(process_instance_id):
    with open('files/reader/public_parameters_reader_' + str(process_instance_id) + '.txt', 'rb') as ppr:
        public_parameters = ppr.read()
    return public_parameters


def actual_decryption(remaining, public_parameters, user_sk, ciphertext_dict):
    test = remaining['CipheredKey'].encode('utf-8')

    ct = bytesToObject(test, groupObj)
    v2 = maabe.decrypt(public_parameters, user_sk, ct)
    v2 = groupObj.serialize(v2)

    dec_field = [cryptocode.decrypt(remaining['Fields'][x], str(v2)) for x in
                 range(len(remaining['Fields']))]
    decoded = [cryptocode.decrypt(ciphertext_dict['body'][x], str(v2)) for x in remaining['Fields']]
    decoded_final = zip(dec_field, decoded)
    print(dict(decoded_final))


def main(groupObj, maabe, process_instance_id, message_id, slice_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # keygen Bob
    with open('files/reader/user_sk1_' + str(process_instance_id) + '.txt', 'r') as us1:
        user_sk1 = us1.read()
    user_sk1 = bytesToObject(user_sk1, groupObj)

    with open('files/reader/user_sk2_' + str(process_instance_id) + '.txt', 'r') as us2:
        user_sk2 = us2.read()
    user_sk2 = bytesToObject(user_sk2, groupObj)

    with open('files/reader/user_sk3_' + str(process_instance_id) + '.txt', 'r') as us3:
        user_sk3 = us3.read()
    user_sk3 = bytesToObject(user_sk3, groupObj)

    with open('files/reader/user_sk4_' + str(process_instance_id) + '.txt', 'r') as us4:
        user_sk4 = us4.read()
    user_sk4 = bytesToObject(user_sk4, groupObj)

    user_sk = {'GID': 'bob', 'keys': merge_dicts(user_sk1, user_sk2, user_sk3, user_sk4)}

    # decrypt
    ciphertext_link = block_int.retrieve_MessageIPFSLink(message_id)
    getfile = api.cat(ciphertext_link)
    ciphertext_dict = json.loads(getfile)
    if ciphertext_dict['metadata']['process_instance_id'] == int(process_instance_id) \
            and ciphertext_dict['metadata']['message_id'] == message_id:
        slice_check = ciphertext_dict['header']
        if len(slice_check) == 1:
            actual_decryption(ciphertext_dict['header'][0], public_parameters, user_sk, ciphertext_dict)
        elif len(slice_check) > 1:
            for remaining in slice_check:
                if remaining['Slice_id'] == slice_id:
                    actual_decryption(remaining, public_parameters, user_sk, ciphertext_dict)


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    process_instance_id = 9325236771567211612

    # generate_public_parameters(process_instance_id)
    message_id = 12990717557941230051
    slice_id = 9522254365290608874
    main(process_instance_id, message_id, slice_id)