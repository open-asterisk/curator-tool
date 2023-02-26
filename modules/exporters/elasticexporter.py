from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
from modules.module import aExporter

class ElasticExporter(aExporter):

    name = "ElasticSearch Exporter"
    author = "ef1500, pog"
    version = "1.0"

    def __init__(self, index_name, host='localhost', port=9200):
        self.index_name = index_name
        self.host = host
        self.port = port
        self.es = AsyncElasticsearch([f'{host}:{port}'])

    @staticmethod
    async def before(index_name):
        pass

    @asynccontextmanager
    async def connection_manager(self, index_name):
        try:
            yield self.es
        finally:
            await self.es.close()

    async def create_table(self, table_name, data_dict):
        try:
            mapping = {
                'properties': {key: {'type': self.get_es_type(value)} for key, value in data_dict.items()}
            }
            async with self.connection_manager(self.index_name) as es:
                await es.indices.create(index=self.index_name, body={'mappings': mapping}, ignore=400)
        except Exception as ex:
            print(f"[{self.name}] ERROR CREATING INDEX: {ex}")

    async def add_data(self, table_name, data):
        try:
            async with self.connection_manager(self.index_name) as es:
                await es.index(index=self.index_name, body=data)
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    async def add_bulk_data(self, table_name, data):
        try:
            body = [{'index': {'_index': self.index_name}} for doc in data]
            async with self.connection_manager(self.index_name) as es:
                await es.bulk(body=body)
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING BULK DATA: {ex}")

    async def after(self, connection):
        pass

    def get_es_type(self, value):
        """
        Returns the ElasticSearch data type based on the Python data type of the value
        """
        type_map = {int: 'integer', float: 'float', str: 'text', bytes: 'binary', bytearray: 'binary'}
        return type_map.get(type(value), 'null')