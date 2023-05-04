import os
import re
from plugins.abstract_plugin import AbstractPlugin

class CombolistExtractor(AbstractPlugin):

    def __init__(self):
        super().__init__(
            authors=["ef1500"],
            description="Extracts email:password combos from text files",
            version="1.0-dev",
            category=["extractor"],
            associated_file_extensions=[".txt"]
        )
        
    # This is where the information from the JSON Database comes into play. The data is passed to this function and the
    # Document is processed.
    def process_document(self, full_path, filename, creation_date, last_modified_date, file_ext, filesize, import_time):
        if file_ext != ".txt":
            return None

        with open(full_path, "r") as f:
            text = f.read()
            
        temp_info = []

        # Use regular expression to find email:password combos
        combos = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b:[A-Za-z0-9!#$%&'*+,-./:;<=>?@^_`{|}~]+", text)
        for combo in combos:
            
            # Split the Combo up by colon
            split_combo = combo.split(':')
            
            try:
                temp_data = {
                    "email": split_combo[0],
                    "password": split_combo[1]
                }
                temp_info.append(temp_data)
            except:
                pass

        if len(combos) == 0:
            return None

        # Log the number of combos extracted
        print(f"{self.plugin_name} extracted {len(combos)} combos from {filename}")

        # Return the combos as JSON
        # Could use a yield here to make things faster (maybe?)
        return {
            self.plugin_name: {
                "data": temp_info,
                "source": filename
            }
        }
 
# Usage       
#if __name__ == "__main__":
    
#    full_path = "D:\\DATA_LEAKS\\TEST_SAMPLE\\COMBOLISTS\\577k RU high Valid Rate.txt"
#    filename = "577k RU high Valid Rate"
#    file_ext = ".txt"
#    ce = CombolistExtractor()
#    e = ce.process_document(full_path, filename, None, None, file_ext, None, None)
#    
#    import json
#    with open("data.json", encoding="utf-8", mode='w') as json_file:
#        json_file.write(json.dumps(e))
#
#
#    print(ce.query_info())
#    print(len(e["CombolistExtractor"]["data"]))