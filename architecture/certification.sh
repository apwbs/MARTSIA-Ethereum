# Generate public/private RSA key for the actors of the system
set -e
python3 reader_public_key.py --reader 'MANUFACTURER'
echo "✅ Keys generated for the MANUFACTURER"
python3 reader_public_key.py --reader 'SUPPLIER1'
echo "✅ Keys generated for the SUPPLIER1"
python3 reader_public_key.py --reader 'SUPPLIER2'
echo "✅ Keys generated for the SUPPLIER2"

python3 attribute_certifier.py 
echo "✅ Attribute certifier done"