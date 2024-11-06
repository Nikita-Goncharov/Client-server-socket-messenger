import random

"""
RSA code realization:

p and q - any two big prime int numbers
n - p * q
fi(n) = (p-1)*(q-1) 														fi() - func euler(count of mutually prime numbers)

e - should be mutually prime with euler number
use one of fermat numbers - (2^2^a) + 1       examples: 3, 5, 17, 257, 65537, 4294967297, 18446744073709551617
find one of them which mutually prime with fi(n)


d - inverse number to "e" by mod   d*e = 1 mod fi(n)   -> (d*e) % fi(n) = 1


(e, n) - public key
(d, n) - private key

Using keys:
M^e mod n = Encrypt(M)
(Encrypt(M))^d mod n = Decrypt(Encrypt(M))

"""


# TODO:алгоритм евклида + расширеная версия
def gcd(a, b):  # taking bigger divider for two prime numbers
    while b != 0:
        a, b = b, a % b
    return a

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_large_prime():
    while True:
        num = random.randint(10**2, 10**3)
        if is_prime(num):
            return num

# Step 1: Generate public and private keys
def generate_keys():
    p = generate_large_prime()
    q = generate_large_prime()
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose e
    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:  # if bigger divider for two prime numbers equals 1, then we found "e" number 
        e = random.randint(2, phi - 1)

    # Calculate d
    d = modinv(e, phi)
    return ((e, n), (d, n))

# Step 2: Encrypt message
def encrypt(public_key: int, plaintext: str) -> str:
    e, n = public_key
    ciphertext = [(ord(char) ** e) % n for char in plaintext]
    ciphertext = map(str, ciphertext)
    return ":".join(ciphertext)

# Step 3: Decrypt message
def decrypt(private_key: int, ciphertext: str) -> str:
    ciphertext = ciphertext.split(":")
    ciphertext = map(int, ciphertext)
    
    d, n = private_key
    plaintext = ''.join([chr((char ** d) % n) for char in ciphertext])
    return plaintext