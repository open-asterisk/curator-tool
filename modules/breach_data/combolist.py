from itertools import islice
from modules.module import Extractor
from modules.exporters.sqlite_exporter import SQLiteExporter
import re

class CombolistExtractor(Extractor):
    
    name = "Combolist Extractor"
    author = "ef1500"
    version = "1.0"
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    
    def check_file(self, file):
        """
        Check if the file at the given file path is a valid combolist file.
        """
        try:
            with open(file, encoding='utf-8') as f:
                for line in list(islice(f, 5)):
                    if not line.strip():
                        continue
                    if not re.search(':', line):
                        raise ValueError("Invalid file format")
        except Exception as e:
            raise ValueError(f'[{self.name}] Invalid file format : {e}')
        
    def extract_data(self, file_path):
        """
        Extract the data from the combolist file at the given file path.
        """
        self.check_file(file_path)
        data = []
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if self.email_pattern.match(line.split(':')[0]):
                    data.append({'email': line.split(':')[0],
                                 'username' : "None",
                                 'password' : line.split(':')[1]})
                else:
                    data.append({'email' : "None",
                                 'username' : line.split(':')[0],
                                 'password' : line.split(':')[1]})
        return data
