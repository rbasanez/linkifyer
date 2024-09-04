import hashlib

def get_hash_string(value:str):
    try:
        hash = hashlib.md5()
        hash.update(value.encode('utf-8'))
        hash = hash.hexdigest()
        return hash
    except Exception as err:
        return None
    
