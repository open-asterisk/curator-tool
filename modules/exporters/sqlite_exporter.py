import aiosqlite
import asyncio
import os
from contextlib import asynccontextmanager
from modules.module import aExporter


class SQLiteExporter(aExporter):

    name = "SQLite Exporter"
    author = "ef1500"
    version = "1.0"

    def __init__(self, db_path):
        # Set up the important variables here
        self.db_path = db_path
        
    @staticmethod
    async def before(db_path):
        """
        Connect to the SQLite database.
        """
        # Create Connections to the database

        # Check if the file exists
        if not os.path.isfile(db_path):
            with open(db_path, 'w', encoding='utf-8'):
                pass
            
    @asynccontextmanager
    async def connection_manager(self, db_path):
        conn = await aiosqlite.connect(db_path)
        try:
            yield conn
        finally:
            await conn.close()

    async def create_table(self, table_name, data_dict):
        """
        Create a table in the SQLite database with the given name, and columns 
        based on the keys and data types of the data_dict.
        """
        # Try to create a table if it doesn't already exist
        try:
            async with self.connection_manager(self.db_path) as conn:
                cursor = await conn.cursor()
                columns = ', '.join([f"{key} {self.get_sqlite_type(value)}" for key, 
                                    value in data_dict.items()])
                column_names = ', '.join([f'{key}' for key in data_dict.keys()])
                await cursor.execute(
                    f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}, UNIQUE({column_names}));')
                await conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR CREATING TABLE: {ex}")

    async def add_data(self, table_name, data):
        """
        Add data to the table in the SQLite database using multiple threads.
        """
        # Try to insert data here
        try:
            async with self.connection_manager(self.db_path) as conn:
                cursor = await conn.cursor()
                placeholders = ', '.join('?' * len(data.keys()))
                insert_query = f'''INSERT OR IGNORE INTO {table_name} VALUES ({placeholders});'''
                data_to_insert = [tuple(data.values())]
                await cursor.executemany(insert_query, data_to_insert)
                await conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    async def add_bulk_data(self, table_name, data):
        """
        Add data to the table in the SQLite database in bulk.
        """
        try:
            async with self.connection_manager(self.db_path) as conn:
                cursor = await conn.cursor()
                placeholders = ', '.join('?' * len(data[0].keys()))
                insert_query = f'''INSERT OR IGNORE INTO {table_name} VALUES ({placeholders});'''
                data_to_insert = [tuple(d.values()) for d in data]
                # Use the Executemany function to bulk insert data
                await cursor.executemany(insert_query, data_to_insert)
                await conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    async def after(self, connection):
        """
        Close the connection to the database
        """
        # Close the connection once the export is finished.
        try:
            await connection.close()
        except Exception as ex:
            print(f"Error closing cursor or connection: {ex}")

    def get_sqlite_type(self, value):
        """
        Returns the SQLite data type based on the Python data type of the value
        """
        # Map the Dict types to SQLite types
        type_map = {int: 'INTEGER', float: 'REAL', str: 'TEXT', bytes: 'BLOB', bytearray: 'BLOB'}
        return type_map.get(type(value), 'NULL')

# Usage Example
#    exporter = Exporter('my_database.db')
#    exporter.before()
#    exporter.create_table('my_table', ['column1', 'column2', 'column3'])
#    extractor = MyExtractor()
#    data = extractor.extract_data('my_file.txt')
#    exporter.add_data('my_table', data)
#    exporter.after()