import aiosqlite
from modules.module import aExporter


class SQLiteExporter(aExporter):

    name = "SQLite Exporter"
    author = "ef1500"
    version = "1.0"

    def __init__(self, db_path):
        # Set up the important variables here
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    async def before(self):
        """
        Connect to the SQLite database.
        """
        # Create Connections to the database
        self.conn = await aiosqlite.connect(self.db_path)
        self.cursor = await self.conn.cursor()

    async def create_table(self, table_name, data_dict):
        """
        Create a table in the SQLite database with the given name, and columns 
        based on the keys and data types of the data_dict.
        """
        # Try to create a table if it doesn't already exist
        try:
            columns = ', '.join([f"{key} {self.get_sqlite_type(value)}" for key, 
                                 value in data_dict.items()])
            column_names = ', '.join([f'{key}' for key in data_dict.keys()])
            await self.cursor.execute(
                f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}, UNIQUE({column_names}));')
            await self.conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR CREATING TABLE: {ex}")

    async def add_data(self, table_name, data):
        """
        Add data to the table in the SQLite database using multiple threads.
        """
        # Try to insert data here
        try:
            placeholders = ', '.join('?' * len(data.keys()))
            insert_query = f'''INSERT OR IGNORE INTO {table_name} VALUES ({placeholders});'''
            data_to_insert = [tuple(data.values())]
            await self.cursor.executemany(insert_query, data_to_insert)
            await self.conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    async def add_bulk_data(self, table_name, data):
        """
        Add data to the table in the SQLite database in bulk.
        """
        try:
            placeholders = ', '.join('?' * len(data[0].keys()))
            insert_query = f'''INSERT OR IGNORE INTO {table_name} VALUES ({placeholders});'''
            data_to_insert = [tuple(d.values()) for d in data]
            # Use the Executemany function to bulk insert data
            await self.cursor.executemany(insert_query, data_to_insert)
            await self.conn.commit()
        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    async def after(self):
        """
        Close the connection to the database
        """
        # Close the connection once the export is finished.
        await self.conn.close()

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