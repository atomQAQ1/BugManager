from config import Config
from pymongo import MongoClient
import pandas as pd
def get_mongodb_collection():
    client = MongoClient(
        host=Config.MONGODB_SETTINGS['host'],
        port=Config.MONGODB_SETTINGS['port']
    )
    db = client[Config.MONGODB_SETTINGS['db']]
    return db[Config.MONGODB_SETTINGS['collection']]

def read_mongodb_to_dataframe():
    """将整个MongoDB集合读取为pandas DataFrame"""
    collection = get_mongodb_collection()
    cursor = collection.find({})
    return pd.DataFrame.from_records(cursor)