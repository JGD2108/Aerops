"""
Este archivo va a concetar la BD

"""
from app.config import config
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

uri = config.MONGODB_URI
# Cosmos DB for MongoDB does not support retryable writes. Keep this disabled
# globally so the same code works for local MongoDB and cloud Cosmos Mongo.
client = MongoClient(uri, retryWrites=False)

db = client[config.MONGODB_DB_NAME]

def check_mongodb_connection():
    try:
        client.admin.command('ping')
        return True
    except ConnectionFailure:
        return False
