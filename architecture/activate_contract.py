import block_int
from decouple import config

attribute_certifier_address = config('ATTRIBUTE_CERTIFIER_ADDRESS')
private_key = config('ATTRIBUTE_CERTIFIER_PRIVATEKEY')

attribute_certifier_address2 = config('ATTRIBUTE_CERTIFIER_ADDRESS2')
private_key2 = config('ATTRIBUTE_CERTIFIER_PRIVATEKEY2')

attribute_certifier_address3 = config('ATTRIBUTE_CERTIFIER_ADDRESS3')
private_key3 = config('ATTRIBUTE_CERTIFIER_PRIVATEKEY3')



def activate():
    # block_int.activate_contract(attribute_certifier_address, private_key)
    block_int.activate_contract(attribute_certifier_address2, private_key2)
    # block_int.activate_contract(attribute_certifier_address3, private_key3)


if __name__ == "__main__":
    activate()
