from cryptography.fernet import Fernet
import getpass
import os
import bcrypt
import sys
import hashlib

keyfile_name = "./key.key"
masterkey_file = "./masterkey.key"
expected_hash = "fef1ccd677b1a96ef6f125e7acdf6f0835e01f8826f1ff0fefe9dd3027c7fc77"

def load_masterkey():
    try:
        with open(masterkey_file, "rb") as file:
            sha256_hash = hashlib.sha256()
            chunk = file.read(4096)
            while len(chunk) > 0:
                sha256_hash.update(chunk)
                chunk = file.read(4096)
            file.seek(0)  # Reset file pointer to the beginning
            if sha256_hash.hexdigest() != expected_hash:
                print(f"Expected hash: {expected_hash}")
                # print(sha256_hash.hexdigest())
                print(f"Calculated hash: {sha256_hash.hexdigest()}") 
                print("Wrong Master key file.")
                sys.exit()
            else:
                print(f"Master Key file verified. Calculated hash:{sha256_hash.hexdigest()}")
            # read first line using readline method
            salt = file.readline().strip()
            # read second line using readline method
            hashed_password = file.readline().strip()
    except FileNotFoundError:
        print("Master key file not found.")
        return None
    except PermissionError:
        print("Permission denied.")
        return None
    except Exception as e:
        print("Error loading key:", e)
        return None
    return salt, hashed_password

salt, hashed_password = load_masterkey()

# function to verify our master password
def verify_masterpassword(user_input, salt, hashed_masterpassword):
    # hash the user input with the stored salt
    encoded_user_input = user_input.encode()
    # return True or False
    return bcrypt.checkpw(encoded_user_input, hashed_masterpassword)

def write_key():
    key = Fernet.generate_key()
    with open(keyfile_name, "wb") as key_file:
        key_file.write(key)

if not os.path.exists(keyfile_name):
    write_key()


def load_key():
    try:
        with open(keyfile_name, "rb") as key_file:
            key = key_file.read()
        return key
    except PermissionError:
        print("Permission denied. Unable to read key file. ")
        return None
    except Exception as e:
        print("Error loading key:", e)
        return None
    
key = load_key()
fer = Fernet(key)

# In a real-world scenario, you would replace the placeholder logic with a secure authentication mechanism. 
# This typically involves securely storing a hashed version of the master password (using a strong hashing algorithm such as SHA-256) and comparing it with the hashed input provided by the user.
# Additionally, you may implement additional security measures such as salting the password hashes to mitigate against dictionary attacks and rainbow table attacks.
def authenticate():
    master_pwd = getpass.getpass("Enter the master password: ")
    
    # Placeholder: Perform authentication logic here
    # For example, you might compare the hashed master_pwd with a securely stored hash
    stored_hash = "..."  # Placeholder for securely stored hash
    # Example of comparing hashed passwords (not recommended for production, use a secure hashing algorithm)
    if master_pwd == stored_hash:
        print("Authentication successful!")
        return True
    else:
        print("Authentication failed. Please try again.")
        return False


def view():
    user_input = getpass.getpass("Enter the master password: ")
    verification_result = verify_masterpassword(user_input, salt, hashed_password)
    if verification_result == False:
        print("Wrong password. Permission denied.")
        print("Verification_result:", verification_result)
        sys.exit()
    with open('password.txt', "r") as f:
        for line in f.readlines():
            data = line.rstrip()
            user, passw = data.split("|")
            print("user:", user, " password:", fer.decrypt(passw.encode()).decode())
    
def add():
    while True:
        user_input = getpass.getpass("Enter the master password: ")
        verification_result = verify_masterpassword(user_input, salt, hashed_password)
        # if verification results evaluate to true
        if verification_result:
            break
        if user_input.lower() == "q":
            print("Exited program. Goodbye. ")
            sys.exit()
        else:
            print("Wrong password. Permission denied. Try again or enter q to quit")
            print("Verification_result:", verification_result)
    
    while True:
        name = input("Account name: ")
        pwd = input("Password: ")

        with open('password.txt', "a") as f:
            f.write(name + "|" + fer.encrypt(pwd.encode()).decode() + "\n")

        print("Account added. Add another one? Enter no to quit.")
        resume = input().lower()
        if resume == "no":
            print("Goodbye. Have a nice day. ")
            sys.exit()

# user interaction
while True:
    mode = input("Would you like to add a new password or view existing ones (view/add)? Press q to quit. ").lower()
    if mode == "q":
        break
    if mode == "view":
        view()
    elif mode == "add":
        add()
    else:
        print("Invalid mode. ")
        continue