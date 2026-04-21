import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain text password matches the hashed one in the database"""
    # bcrypt requires passwords to be encoded into bytes
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    """Hashes a password with a randomly generated salt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decode back to a normal string to store in the database
    return hashed_password_bytes.decode('utf-8')