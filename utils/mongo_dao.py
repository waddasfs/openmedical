import time
import re
import json
import pymongo
from pymongo import MongoClient
from pymongo import ASCENDING
from .mongo_config import mongo_config

class MongoDao:
    def __init__(self, config=mongo_config):
        self.__client = pymongo.MongoClient(config["ip"], config["port"], username=config['username'], password=config['password'])
        self.__db = self.__client[config["database"]]

    def insert(self, collection_name, parm):
        """
        insert log data into mongo
        :param collection_name:
        :param parm:
        :return: InsertOneResult object
        """
        try:
            result = self.__db[collection_name].insert_one(parm)
            print(f"数据插入成功，集合: {collection_name}, 插入ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"数据插入失败，集合: {collection_name}, 错误: {e}")
            return None

    def batch_search(self, collection_name, key, values):
        query_in = {key: {"$in": values}}
        rst = list(self.__db[collection_name].find(query_in))
        return rst

    def find_all(self, collection_name):
        """
        export all data in collection_name
        :param collection_name:
        :return:
        """
        rst = list(self.__db[collection_name].find({}))
        return rst

    def search(self, collection_name, key, value):
        """
        search record by keyword
        :param collection_name:
        :param keyword:
        :return:
        """
        rst = list(self.__db[collection_name].find({key: value}))
        return rst

    def search_multi_filter(self, collection_name, multi_filter_data):
        """
        search record by keyword
        :param collection_name:
        :param keyword:
        :return:
        """
        rst = list(self.__db[collection_name].find(multi_filter_data))
        return rst

    def update(self, collection_name, key, value, update_data):
        """
        update document by keyword
        :param collection_name:
        :param key:
        :param value:
        :param update_data:
        :return: True if successful, False otherwise
        """
        result = self.__db[collection_name].update_one({key: value}, {'$set': update_data})
        return result.modified_count > 0

    def delete(self, collection_name, keyword, value):
        '''
        delete all records that match keyword
        :param collection_name:
        :param keyword:
        :return:
        '''
        self.__db[collection_name].delete_many({keyword: value})

    def create_index(self, collection_name, keyword):
        """
        create index
        :param collection_name:
        :param keyword:
        :return: index name
        """
        try:
            # 检查索引是否已存在
            existing_indexes = self.__db[collection_name].list_indexes()
            for index in existing_indexes:
                if keyword in index.get('key', {}):
                    return f"{keyword}_1"  # 索引已存在
            
            # 创建新索引
            index_name = self.__db[collection_name].create_index([(keyword, ASCENDING)])
            return index_name
        except Exception as e:
            print(f"创建索引失败: {e}")
            return None

    def check_index(self, collection_name):
        """
        check if index exist
        :return:
        """
        try:
            index = len(self.__db.get_collection(collection_name).index_information())
            return True
        except Exception:
            return False

    def export_mongo(self, collection_name, output_path=""):
        data = self.__db.get_collection(collection_name)
        return data

    def check_mongo(self, collection, key, value):
        result = self.search(collection, key, value)
        flag = False
        for i in result:
            flag = True
        return flag

    def fuzzy_search(self, data, collection):
        """ relative slow """
        regex_dic = {}
        for text in data:
            regex_dic["search_key"] = re.compile(text)
        rst = self.__db[collection].find(regex_dic)
        return rst


mongo_dao = MongoDao()

if __name__ == '__main__':
    # rst = mongoDao.search("IdMap", "token", "7hg2e82295a0df70f2442f820655f28ca")
    # print(rst)
    data = mongoDao.search("kg_triples", "tenant_id", "d83bd7ee88a5d090d9d91f8e24ff86b0")
    print(data)
