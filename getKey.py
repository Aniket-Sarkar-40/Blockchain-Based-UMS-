from cryptography.hazmat.primitives.asymmetric import rsa
# Generate sender's private and public keys
sender_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
sender_public_key = sender_private_key.public_key()

print(sender_private_key, sender_private_key)