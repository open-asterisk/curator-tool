# Abstract Plugin for open asterisk
# ef1500

# The objective of this file is to allow for a basic plugin class that will allow
# anyone to write their own plugins if they want.

import os
from abc import ABC

class AbstractPlugin(ABC):
    
    def __init__(self, authors=["None"], description="", version="", category=[None], 
                 associated_file_extensions=[None]):        
        """
        Here you should set up the basic information for your plugin.This includes stuff like
        the plugin name, description, authors, etc.
        """
        
        self.plugin_name = self.__class__.__name__
        self.authors = authors
        self.description = description
        self.version = version
        self.category = category
        self.associated_file_extensions = associated_file_extensions
        
    def query_info(self):
        """Used when creating the plugins.json file, returns the relavent JSON information"""
        plugin_information = {
            self.plugin_name: {
                "location": os.path.dirname(os.path.abspath(__file__)),
                "description": self.description,
                "authors": self.authors,
                "version": self.version,
                "category": self.category,
                "associated_file_extensions": self.associated_file_extensions
            }
        }
        return plugin_information
    
    # TODO: Potentially add a way to check the document?
        
    def process_document(self, full_path, filename, creation_date, last_modified_date, file_ext,
                         filesize, import_time):
        """Here, you want to set up the function that converts your document into usable data.
        you are going to want to return this data as JSON.
        
        The JSON you return should look like so:
        "ExamplePlugin" : {
            "data": YOUR DATA HERE
        }

        Args:
            full_path (str): file path to the file
            filename (int): name of the file
            creation_date (int): unix time of the document's creation
            last_modified_date (int): unix timestamp of the last modified date
            file_ext (str): file extension
            filesize (int): size of the file
            import_time (int): the ime the file was imported
        """
        pass