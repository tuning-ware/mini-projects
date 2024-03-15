import bcrypt
import hashlib

# Function to generate a salt and hash the master password
def hash_master_password():
    master_password = input("Make your password. ")
    # Generate a random salt
    salt = bcrypt.gensalt()
    # Hash the master password with the salt
    hashed_password = bcrypt.hashpw(master_password.encode(), salt)
    return salt, hashed_password

def write_masterkeyfile(salt, hashed_password):
    with open("./masterkey.key", "wb") as file:
        file.write(salt + b"\n")
        file.write(hashed_password + b"\n")

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        # Read the file in chunks to handle large files efficiently
        chunk = file.read(4096)
        while len(chunk) > 0:
            sha256_hash.update(chunk)
            chunk = file.read(4096)   
    return sha256_hash.hexdigest()


print(calculate_file_hash("./masterkey.key"))