from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)

# Build certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u'SK'),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'Bratislava'),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u'Bratislava'),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'GreyHill'),
    x509.NameAttribute(NameOID.COMMON_NAME, u'localhost'),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName(u'localhost'),
        x509.DNSName(u'127.0.0.1'),
        x509.DNSName(u'greyhill.azurewebsites.net'),
        x509.DNSName(u'greyhill-api.azurewebsites.net'),
        x509.DNSName(u'greyhill-dev.azurewebsites.net'),
        x509.DNSName(u'greyhill-dev-api.azurewebsites.net'),

    ]),
    critical=False,
).sign(private_key, hashes.SHA256(), default_backend())

# Save files
with open('key.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open('cert.pem', 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print('✅ Generated cert.pem and key.pem')