import csv
import os
from modules.module import Exporter

class CSVexporter(Exporter):
    """
    CSV Exporter Module For the Open Asterisk Curator Tool
    Converts Databases to CSV
    """

    name = "CSV Exporter"
    author = "ef1500"
    version = "1.0"

    def __init__(self, csvfile):
        # Create an object for the CSVfile
        self.csvfile = csvfile

    def before(self):
        """
        Connect to the data source or do anything important before
        The Exporter Starts
        """
        # Announce that the Exporter Started
        print(f"[{self.name}] EXPORTER STARTED!")

    def create_table(self, data_dict):
        """Create the CSV Table

        Args:
            data_dict (dict): for writing to the CSV
        """
        # Try to open the CSV file and create a header
        try:
            if not os.path.isfile(self.csvfile):
                with open(self.csvfile, 'w+', encoding='utf-8', newline='') as csv_file:
                    # Create a CSV Writer object
                    csvwriter = csv.DictWriter(csv_file, [header for header in data_dict.keys()])
                    # Write the header to the csv file
                    csvwriter.writeheader()
            else:
                pass
        except Exception as ex:
            print(f"[{self.name}] ERROR CREATING TABLE: {ex}")

    def add_data(self, data_dict):
        """Write data to the csv file

        Args:
            data_dict (dict): dict of data to write to the csv file
        """
        # Add data to the csv
        try:
            with open(self.csvfile, 'a+', encoding='utf-8', newline='') as csv_file:
                # Create CSV writer object
                csvwriter = csv.DictWriter(csv_file, [header for header in data_dict.keys()])

                # Write the dict to the CSV File
                csvwriter.writerow(data_dict)

        except Exception as ex:
            print(f"[{self.name}] ERROR INSERTING DATA: {ex}")

    def after(self):
        """
        Do stuff after the exporter has finished its job
        Maybe logging stuff?
        """
        pass
