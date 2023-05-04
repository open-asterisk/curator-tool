# Open asterisk backend
# ef1500
# objective: to gather all of our files together so we can classify them
# basically, we're gonna assign some JSON to each file, like import time, file extension, filename, etc.
# then, once we have all of the files collected, we're gonna classify them one by one
import os
import json
import logging

from datetime import datetime

class BackendImporter:

    def __init__(self, directory, output_directory, recursive=False):
        """Initialize the backend importer

        Args:
            directory (str): the directory to import from
            output_directory (str): the directory to output to
            recursive (bool, optional): search recursively? Defaults to False.
        """
        # Initialize the Backend Importer. This will define the 
        # directory that we are going to import, and give us some 
        # additional options as well. Recursive search would be 
        # good for stealer logs and ransomware dumps

        self.version = "dev-1.0"

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[open_asterisk/{}] %(message)s'.format(self.__class__.__name__))
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.directory = directory
        self.output_directory = output_directory
        self.recursive = recursive
        self.filename = "backendimporter_db.json"

    def _gather_files(self):
        """Get all files in the directory"""
        self.logger.info(f"Gathering all files in {self.directory}, recursive={self.recursive}")

        # Create a temporary list for all of the files
        gathered_files = list()

        for root, _, files in os.walk(self.directory):
            for filename in files:
                # Since we already have this, let's do some
                # Of the heavy lifting now so we don't have to do it twice.
                file_data = [os.path.join(root, filename), filename]
                 # Append the file information to the gathered files list
                gathered_files.append(file_data)
            if not self.recursive:
                break # Stop going through subdirs if recursive is false

        return gathered_files

    def _initialize_json(self):
        """Initialize the JSON File if it does not exist"""
        db_filepath = os.path.join(self.output_directory, self.filename)
        if not os.path.isfile(db_filepath):
            self.logger.info(f"{self.filename} does not exist. Creating it...")
            with open(db_filepath, encoding="utf-8", mode="w") as json_db:
                json_to_write = {}

                # Create the Header
                json_to_write["header"] = {
                    "authors": ["ef1500", "request", "pog", "theangrybagel"],
                    "description": "Open Asterisk Curator Tool Importer Database",
                    "version": self.version
                }

                # Create the space for the files
                json_to_write["files"] = []

                # Write it
                json_db.write(json.dumps(json_to_write))
        return

    def _generate_json(self, gathered_files):
        """Generate JSON from the list of gathered files and put it into the database file"""
        # We are going to want to get some interesting data here, like:
        # File creation Date
        # File Import Date
        # File last modified Date
        # Filesize
        self.logger.info(f"Generating JSON for {len(gathered_files)} files")
        db_filepath = os.path.join(self.output_directory, self.filename)

        with open(db_filepath, encoding="utf-8", mode="r+") as json_db:
            json_data = json.load(json_db)

            for filepath, filename in gathered_files:
                creation_date = int(os.path.getctime(filepath)) # Get the file creation date
                 # Get the file's last modified date
                last_modified_date = int(os.path.getmtime(filepath))
                file_extension = os.path.splitext(filename)[-1] # Get the file extension
                filesize = os.path.getsize(filepath) # Get the file's size in bytes
                 # Get the current unix time
                import_time = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())

                json_to_write = {
                    "full_path": filepath,
                    "filename": filename,
                    "creation_date": creation_date,
                    "last_modified_date": last_modified_date,
                    "file_ext": file_extension,
                    "filesize": filesize,
                    "import_time": import_time
                }

                json_data["files"].append(json_to_write)

            json_db.seek(0) # Seek to the beginning of the file
            json.dump(json_data, json_db) # Add the new data
            json_db.truncate()

    def commence_import(self):
        """
        Commence the import and begin importing the files
        """
        self.logger.info("Preparing for import")
        self._initialize_json()
        self.logger.info("Preparation Finished. Commencing import")
        gathered_files = self._gather_files()
        self.logger.info("Finished gathering files, now importing...")
        self._generate_json(gathered_files)
        self.logger.info("Import finished!")

# Example Usage
#if __name__ == '__main__':
#    a = BackendImporter("PATH_TO_IMPORT_HERE", "./", False)
#    a.commence_import()