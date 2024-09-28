import time
import jwt
from project.settings import JWT_SECRET, JWT_ALGORITHM, JWT_TOKEN_EXPIRE_TIME

def generate_jwt_token(object_id: int) -> str:
    payload = {'object_id':object_id, 'exp': int(time.time()) + JWT_TOKEN_EXPIRE_TIME}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def is_valid_jwt_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp = int(payload.pop('exp'))
        return time.time() <= exp
    except jwt.PyJWTError:
        return False

def get_object_id_by_token(token: str) -> int:
    is_valid_jwt_token(token)
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload.get('object_id')
