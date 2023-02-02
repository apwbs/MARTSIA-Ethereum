# MARTSIA-Ethereum

#### This repository contains the Ethereum-based version of the MARTSIA approach. 

### Guide

In order to run the system, the following libraries must be installed: python3.6, charm https://github.com/JHUISI/charm, rsa, web3 (python-version), python-decouple, truffle, sqlite3.

The first thing to do is to deploy the smart contract on the blockchain. 
To do that, create a Metamask wallet and fund an account with some Eth in the Goerli testnet with a Goerli faucet. 
Then create an account on Infura and obtain a key for the Goerli testnet.

Then, move in the 'blockchain' folder and create a '.env' file. Put two constants in there:
1. 'MNEMONIC'=the secret words of the Metamask wallet
2. 'PROJECT_ID'=the project ID obtained from Infura

After doing this, open a terminal and run 'truffle init'. Copy the folders 'contracts' and 'migrations' from the repo
and also the 'truffle-config.js' file. Then run 'truffle migrate --network goerli' and wait for the deployment of the 
contract on chain.

When these passages are completed, the databases for all the actors involved in the process need to be created. 
Move in the 'files' folder and create/copy the folders you need. To create a database run 'sqlite3 name_of_the_database.db'.
When inside that database run '.read database.sql' to instantiate the database with the right tables.

Once all these preliminary steps are completed, you can start running the actual code. And '.env' file must be created in order
to store all the necessary values of the constants. This file must be put in the 'architecture' or 'implementation' folder.

The first thing to do is provide a pair of private and public keys to the readers. Open a terminal and move in the 
architecture or implementation folder and run 'python3 rsa_public_keys.py'. In the file specify the actors
you intend to give a pair of keys to.

Next, open the attribute certifier file and write down the attributes that you intend to give to the actors of the system.
Then run 'python3 attribute_certifier.py' to store those values both in the certifier db and on chain. Copy the resulting
process_instance_id number in the .env file.

In order to instantiate the four authorities with multi-party computation open the four scripts, namely authority1.py, authority2.py
authority3.py and authority4.py. Consider the lines 185-189 of the first file and lines 182-186 of the remaining three.
Run the function 'save_authorities_names()' for all the authorities. Then, after all the authorities have completed this step,
run 'initial_parameters_hashed()' for all the authorities. Then run the other three functions, but keeping the same procedure, namely
run the third function for all the authorities, then the fourth function of all the authorities and so on. At the end of this 
procedure, the authorities are instantiated via multi-party computation, and they are ready to generate keys for the users.

To cipher a message and store it on the blockchain, open the 'data_owner.py' file. Firstly, run 'generate_pp_pk()' to 
instantiate the data owner, then modify the file 'data.json' with the data you want to cipher. Then, run the main() function, but
remember to modify the access policy and the entries that you need to cipher with a particular policy: lines 132-139.

