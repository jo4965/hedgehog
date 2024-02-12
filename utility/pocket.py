from pocketbase import PocketBase
import jwt
import time
import os
import traceback

from dotenv import load_dotenv
load_dotenv()

pb = PocketBase("http://127.0.0.1:8090")


def auth():
    try:
        db_id = os.getenv("DB_ID")
        db_password = os.getenv("DB_PASSWORD")
        pb.admins.auth_with_password(db_id, db_password)
    except Exception as e:
        raise Exception("DB auth error")


def reauth():
    try:
        token = pb.auth_store.base_token
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        expire_time = decoded_token["exp"]
        current_time = int(time.time())
        if current_time > expire_time:
            auth()
    except:
        raise Exception("DB reauth error")


def create(collection, data):
    try:
        reauth()
        pb.collection(collection).create(data)
    except:
        raise Exception("DB create error")


def delete(collection, id):
    try:
        reauth()
        pb.collection(collection).delete(id)
    except:
        raise Exception("DB delete error")


def get_full_list(collection, batch_size=200, query_params=None):
    try:
        reauth()
        return pb.collection(collection).get_full_list(
            batch=batch_size, query_params=query_params
        )
    except:
        print(traceback.format_exc())
        raise Exception("DB get_full_list error")


try:
    auth()
except:
    print("auth error")