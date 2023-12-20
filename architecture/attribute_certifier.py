import json
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

attribute_certifier_address = config('CERTIFIER_ADDRESS')
private_key = config('CERTIFIER_PRIVATEKEY')

manufacturer_address = config('MANUFACTURER_ADDRESS')
supplier1_address = config('SUPPLIER1_ADDRESS')
supplier2_address = config('SUPPLIER2_ADDRESS')

# Connection to SQLite3 attribute_certifier database
conn = sqlite3.connect('files/attribute_certifier/attribute_certifier.db')
x = conn.cursor()

def store_process_id_to_env(value):
    name = 'PROCESS_INSTANCE_ID'
    with open('.env', 'r', encoding='utf-8') as file:
        data = file.readlines()
    edited = False
    for line in data:
        if line.startswith(name):
            data.remove(line)
            break
    line = "\n" +  name + "=" + value + "\n"
    data.append(line)

    with open('.env', 'w', encoding='utf-8') as file:
        file.writelines(data)

def generate_attributes():
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(1, 2 ** 64)
    print(f'process instance id: {process_instance_id}')

    dict_users = {
        manufacturer_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                               str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'MANUFACTURER@UT'],

        supplier1_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                            str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'SUPPLIER@OU',
                            'ELECTRONICS@OT'],

        supplier2_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                            str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'SUPPLIER@OU',
                            'MECHANICS@TU']
    }

    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)

    file_to_str = f.read()

    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    block_int.send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file)
    
    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()

    store_process_id_to_env(str(process_instance_id))


if __name__ == "__main__":
    generate_attributes()
