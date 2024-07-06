from decouple import config
from Crypto.PublicKey import RSA
import ipfshttpclient
import sqlite3
import io
import block_int
import rsa
import random
from datetime import datetime
import json

authorities_names = ['UT', 'OU', 'OT', 'TU']


class Certifier():
    """ Manage the certification of the attributes of the actors

    A collection of static methods to generate the rsa keys of the actors
    and to certify the attributes of the actors
    """

    def certify(actors, roles):
        """ Read the public keys of actors and SKM, and certify the attributes of the actors

        Read the public keys of each actor in actors and certify the attributes of the actors

        Args:
            actors (list): list of actors
            roles (dict): a dict that map each actor to a list of its roles

        Returns:
            int : process instance id
        """
        for actor in actors:
            Certifier.generate_rsa_keys(actor)
        return Certifier.__attribute_certification__(roles)

    def read_public_key(actors):
        """ Read the public keys of each actor in actors
        
        Args:
            actors (list): list of actors
        """
        for actor in actors:
            Certifier.generate_rsa_keys(actor)

    def attribute_certification(roles):
        """ Certify the attributes of the actors

        Certify the attributes of the actors on the blockchain.
        The certification is performed by the SKM.

        Args:
            roles (dict): a dict that map each actor to a list of its roles
        
        Returns:
            int : process instance id
        """
        Certifier.__attribute_certification__(roles)

    def generate_rsa_keys(actor_name):
        """ Generate the public and private rsa key of an actor

        Generate the public and private key of an actor from .env and store them in a SQLite3 database
        and on the blockchain on the PKReadersContract  

        Args:
            actor_name (str): name of the actor
        """
        api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

        print("Generate keys for " + actor_name)
        reader_address = config(actor_name + '_ADDRESS')
        private_key = config(actor_name + '_PRIVATEKEY')

        # Connection to SQLite3 reader database
        conn = sqlite3.connect('files/reader/reader.db')
        x = conn.cursor()

        # # Connection to SQLite3 data_owner database
        connection = sqlite3.connect('files/data_owner/data_owner.db')
        y = connection.cursor()

        x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
        result = x.fetchall()
        if result:
            print("rsa key already present")
            exit()

        keyPair = RSA.generate(bits=1024)

        f = io.StringIO()
        f.write('reader_address: ' + reader_address + '###')
        f.write(str(keyPair.n) + '###' + str(keyPair.e))
        f.seek(0)

        hash_file = api.add_json(f.read())
        print(f'ipfs hash: {hash_file}')

        block_int.send_publicKey_readers(reader_address, private_key, hash_file)

        x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)",
                  (reader_address, str(keyPair.n), str(keyPair.d)))
        conn.commit()

        x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
                  (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
        conn.commit()

    def __store_process_id_to_env__(process_instance_id):
        name = 'PROCESS_INSTANCE_ID'
        with open('.env', 'r', encoding='utf-8') as file:
            data = file.readlines()
        for line in data:
            if line.startswith(name):
                data.remove(line)
                break
        line = "\n" + name + "=" + process_instance_id + "\n"
        data.append(line)

        with open('.env', 'w', encoding='utf-8') as file:
            file.writelines(data)

    def __attribute_certification__(roles):
        """ Certify the attributes of the actors

        Certify the attributes of the actors on the blockchain.
        The certification is performed by the SKM.

        Args:
            roles (dict): a dict that map each actor to a list of its roles

        Returns:
            int : the process instance id of the certification process
        """

        api = ipfshttpclient.connect(
            '/ip4/127.0.0.1/tcp/5001')  # Connect to local IPFS node

        certifier_address = config('ATTRIBUTE_CERTIFIER_ADDRESS')
        certifier_private_key = config('ATTRIBUTE_CERTIFIER_PRIVATEKEY')

        # Connection to SQLite3 attribute_certifier database
        conn = sqlite3.connect('files/attribute_certifier/attribute_certifier.db')  # Connect to the database
        x = conn.cursor()

        now = datetime.now()
        now = int(now.strftime("%Y%m%d%H%M%S%f"))
        random.seed(now)
        process_instance_id = random.randint(1, 2 ** 64)
        print(f'process instance id: {process_instance_id}')

        dict_users = {}
        for actor, list_roles in roles.items():
            dict_users[config(actor + '_ADDRESS')] = [str(process_instance_id) + '@' + name for name in
                                                      authorities_names] + [role for role in list_roles]

        f = io.StringIO()
        dict_users_dumped = json.dumps(dict_users)
        f.write('"process_instance_id": ' + str(process_instance_id) + '####')
        f.write(dict_users_dumped)
        f.seek(0)

        file_to_str = f.read()

        hash_file = api.add_json(file_to_str)
        print(f'ipfs hash: {hash_file}')

        block_int.send_users_attributes(certifier_address, certifier_private_key, process_instance_id, hash_file)

        x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
                  (str(process_instance_id), hash_file, file_to_str))
        conn.commit()

        Certifier.__store_process_id_to_env__(str(process_instance_id))

        return process_instance_id
