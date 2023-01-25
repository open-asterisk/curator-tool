from itertools import islice
from modules.module import Extractor
import re

class CombolistExtractor(Extractor):
    """
    Combolist extractor used to convert combolists into maliable data
    that can be used by the exporter modules.
    """

    name = "Combolist Extractor"
    author = "ef1500"
    version = "1.0"

    def __init__(self):
        # Define the email pattern, that will be useful later
        self.email_pattern = re.compile(r"^\S+@\S+\.\S+")

    def check_file(self, file):
        """
        Check if the file at the given file path is a valid combolist file.
        """
        try:
            with open(file, encoding='utf-8') as chk_file:
                # Read the first 5 lines to check if it's valid
                for line in list(islice(chk_file, 5)):
                    line = line.strip()
                    if not re.search(':|;', line):
                        # Raise an exception if the check fails
                        raise ValueError(f"[{self.name}] {file}: Invalid file format")
        # Raise an Exception if the check fails
        except ValueError as ex:
            print(f"{ex}")

    def extract_data(self, file_path):
        """
        Extract the data from the combolist file at the given file path.
        """
        # Run the check file function
        self.check_file(file_path)
        # Create a list for all of the converted data
        data = []
        # Open the file to process it
        with open(file_path, encoding='utf-8') as combo_file:
            # Iterate over each line in the combo_file
            for line in combo_file:
                line = line.strip()
                if not line:
                    continue
                # If it matches, then split the data and append the new dict
                # To the data[] list.
                if self.email_pattern.match(line) is not None:
                    data.append({'email': re.split(':|;', line)[0],
                                'username' : "None",
                                'password' : re.split(':|;', line)[1]})
                else:
                    data.append({'email' : "None",
                                'username' : re.split(':|;', line)[0],
                                'password' : re.split(':|;', line)[1]})
        # Return the list of dicts that contains the data
        return data
