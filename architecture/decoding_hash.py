hash_string = "6777"
decimal = int(hash_string, 16)
print('Ethereum encoded argument 1:', hash_string)
print('Purchase order number:', decimal)
# print(decimal)
print()

hash_string = "404d4152545349413a516d564641647031335a6e4a4a4774374735384848556b784b4c7a5a346655475754714436797236764765663851"
hash_bytes = bytes.fromhex(hash_string)
ascii_string = hash_bytes.decode('ascii')
print('Ethereum encoded argument 2:', hash_string)
print('Purchase order:', ascii_string)
# print(ascii_string)
