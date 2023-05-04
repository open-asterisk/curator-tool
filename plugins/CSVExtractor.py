import csv
import json
from plugins.abstract_plugin import AbstractPlugin

class CSVExtractor(AbstractPlugin):
    
    def __init__(self):
        super().__init__(
            authors=["ef1500"],
            description="Extracts information from CSV files.",
            version="1.0",
            category=["extractor"],
            associated_file_extensions=[".csv"]
        )
        
    def process_document(self, full_path, filename, creation_date, last_modified_date, file_ext,
                         filesize, import_time):
        """Extracts data from CSV file and returns it as JSON."""
        
        csv_data = []
        
        with open(full_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_data.append(row)
                
        data = {
            "source": filename,
            "creation_date": creation_date,
            "last_modified_date": last_modified_date,
            "filesize": filesize,
            "import_time": import_time,
            "data": {
                "rows": csv_data
            }
        }

        return {self.plugin_name: data}