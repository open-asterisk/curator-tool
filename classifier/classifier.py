# Python File Classifier
# Author: ef1500
# For starters, we can classify some files rather easily
# CSV, SQL, JSON, and the likes are rather easy to parse and work with
# However, when dealing with text dumps, we must develop a solution
# to work through this obstacle.
from datetime import datetime

import os
import json
import logging
import importlib

class FileClassifier:

    METHODS = ['exts', 'ml', 'mixed']
    # --------- [METHODS] --------
    # exts - Only Classify based on File extensions
    # ml - Only classify with the ML model (Todo)
    # mixed - use a combination of both the ML model and mixed model (Todo)
    
    def __init__(self, json_db, method='exts',
                 print_db_info=True, classifier_model=None, external_plugin_list=None):
        """Initialize the classifier

        Args:
            json_db (str): location of the json database. usually it is "./backendimporter_db.json".
            method (str, optional): Method of classification. Defaults to 'exts'.
            classifier_model (str, optional): Location of the model to use. Defaults to None.
            external_plugin_list (str, optional): Location of an external plugin list to use instead
            of the internal one
        """

        # Check if a valid method was specified
        if method not in self.METHODS:
            raise ValueError("Invalid Classification Method. Options are exts, ml, or mixed.")

        self.version = "dev-1.0"

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[open_asterisk/{}] %(message)s'.format(self.__class__.__name__))
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.json_db = json_db
        self.method = method
        self.print_db_info = print_db_info
        self.classifier_model = classifier_model
        self.internal_plugin_list = "./curator-tool/plugins.json"
        # Add a check for the internal plugin list that checks the last update and notifies the user
        # To update the plugin list if the the last update time is over two weeks, and notify them
        # that they can use python3 curator_tool.py --update_plugin_list to update the list
        self.external_plugin_list = external_plugin_list

        # Create a method map for mapping classifications to their respective
        # functions in the class
        self.method_map = {
            "exts": self._exts_classification,
            "ml": self._ml_classification,
            "mixed": self._mixed_classification
        }

        self._plugin_database_cache = None # Location of the plugin database
        self._plugin_list_cache = None # Contents of plugin database file
        self._plugin_map_cache = {} # Plugin map that maps file exts to plugins

        self._database = None # Contents of the backend database
        
        self._plugin_categories = ["metadata", "curator", "extractor"]
        self._plugin_folder_location = "./curator-tool/plugins/"
        self._plugin_database_location = "./curator-tool/"
        self._plugin_database_filename = "plugins.json"
        
    def _generate_plugin_list(self):
        # Generate our list of plugins
        self.logger.info(f"Generating {self._plugin_database_filename}")
        plugin_files = [plugin_file for plugin_file in 
                        os.listdir(self._plugin_folder_location) if plugin_file.endswith(".py")]
        self.logger.info(f"Found {len(plugin_files)-1} plugin(s)")
        
        plugin_data = []
        
        # Iterate over them all
        for plugin_file in plugin_files:
            if not plugin_file.startswith("abstract"):
            
                plugin_path = os.path.join(self._plugin_folder_location, plugin_file)
                spec = importlib.util.spec_from_file_location(plugin_file[:-3], plugin_path)
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
                
                # Create an instance of the plugin and get its metadata
                plugin = getattr(plugin_module, plugin_module.__name__)()
                plugin_info = plugin.query_info()
                
                plugin_data.append(plugin_info)
            
        # Generate the JSON
        json_to_write = {
            "file_information": {
                "last_update": int((datetime.now() - datetime(1970, 1, 1)).total_seconds()),
                "total_plugins": len(plugin_data)
            },
            "plugin_categories": self._plugin_categories,
            "plugins": plugin_data
        }
        
        json_plugin_database_path = os.path.join(self._plugin_database_location,
                                                 self._plugin_database_filename)
        with open(json_plugin_database_path, "w", encoding="utf-8") as plugin_db:
            json_data = json.dumps(json_to_write)
            plugin_db.write(json_data)
            
        self.logger.info("Finished generating plugins database")
        

    def _basic_check(self):
        # Check if all the files exist so we can alert the user before we get started
        # First, check the JSON Database
        if not os.path.isfile(self.json_db):
            raise FileNotFoundError("JSON Database Not Found.")
        
        json_plugin_database_path = os.path.join(self._plugin_database_location,
                                                 self._plugin_database_filename)
        if not os.path.isfile(json_plugin_database_path) and not self.external_plugin_list:
            self.logger.info("Internal plugin database not found, creating it")
            self._generate_plugin_list()

        # Now, Check the Classifier Model, if Specified 
        if self.classifier_model and not os.path.isfile(self.classifier_model):
            raise FileNotFoundError("Classifier Model Not Found.")

        # Next, check the Internal or external plugin database
        plugin_database = self.external_plugin_list or self.internal_plugin_list
        if not os.path.isfile(plugin_database):
            raise FileNotFoundError("Plugin Database Not Found.")

    def _load_plugin_database(self):
        # Load the proper database into the class
        self.logger.info("Loading plugin database")
        if self._plugin_database_cache is None:
            self._plugin_database_cache = self.external_plugin_list or self.internal_plugin_list

        # Load the plugin list into the plugin list cache
        with open(self._plugin_database_cache, encoding="utf-8", mode="r") as json_db:
            self._plugin_list_cache = json.load(json_db)

        num_plugins = self._plugin_list_cache["file_information"]["total_plugins"]
        self.logger.info(f"Finished loading plugin database. The database contains {num_plugins} plugin(s).")

    def _generate_plugin_map(self):
        # Generate a plugin map for each plugin in the database
        self.logger.info("Generating plugin map")

        # Iterate over each of the plugins
        for index, plugin in enumerate(self._plugin_list_cache["plugins"]):
            # Now iterate through all of the associated file extensions
            plugin_name = list(plugin.keys())[0]
            for extension in self._plugin_list_cache["plugins"][index][plugin_name]["associated_file_extensions"]:
                # Map each extension to a list of plugins
                if extension not in self._plugin_map_cache:
                    self._plugin_map_cache[extension] = []
                self._plugin_map_cache[extension].append(plugin)

        # We're finished!
        self.logger.info("Finished Generating Plugin Map")

    def _load_database(self):
        # Load database, may want to somehow make this more efficent
        # Because if we have 90 thousand+ files, it might get cumbersome.

        self.logger.info("Loading backend database")

        # Open the file and put it in the "_database" private variable.
        with open(self.json_db, encoding="utf-8", mode="r") as json_db:
            self._database = json.load(json_db)

        self.logger.info("Finished loading backend database")

    def _print_database_info(self):
        # Print misc. database info that might be useful to the user
        database_authors = ",".join(self._database["header"]["authors"])
        database_description = self._database["header"]["description"]
        database_version = self._database["header"]["version"]

        print(f"[DB Information] Authors: {database_authors}")
        print(f"[DB Information] Description: {database_description}")
        print(f"[DB Information] Database Version: {database_version}")

    def _exts_classification(self):
        # exts classification
        self.logger.info("Beginning etxs classification")

        # Iterate over the nested JSON in the database
        for index, gathered_file in enumerate(self._database["files"]):
            file_extension = gathered_file["file_ext"]

            # Get plugins for the specified extension
            plugins = self._plugin_map_cache.get(file_extension, [])

            # Since we aren't using ML, we can't provide any extra options,
            # This is about as much as we can do in this department.
            # We Provide the plugin DB so we don't get mixed up when
            # Loading databases
            json_to_write = {
                "plugins": plugins,
                "plugin_db": self._plugin_database_cache
            }

            # write the JSON
            self._database["files"][index]["classifier"] = json_to_write

        self.logger.info("exts classification finished. Recreating DB.")

        # Now actually write it
        with open(self.json_db, encoding="utf-8", mode="w") as json_file_db:
            json.dump(self._database, json_file_db)

        self.logger.info("Finished recreating DB. Process Complete.")

    def _ml_classification(self):
        # Not Implemented Yet
        pass

    def _mixed_classification(self):
        # Not Implemented Yet
        pass

    def begin_classifier(self):
        """Begin the classification process"""
        self.logger.info("Preparing for classification")
        # Check that all files are present
        self._basic_check()
        # Load the plugin database
        self._load_plugin_database()
        # generate the plugin map
        self._generate_plugin_map()
        # load the file database
        self._load_database()
        # Print the database information if specified
        if self.print_db_info:
            self._print_database_info()
        # Preperation is finished. Let's go.
        self.logger.info("Preparation finished.")
        self.method_map[self.method]()

# if __name__ == '__main__':
#    test = FileClassifier("C:\\Users\\srcol\\OneDrive\\Desktop\\Coding Projects\\open_a_2_experiment\\backendimporter_db.json", 'exts', True, None, "C:\\Users\\srcol\\OneDrive\\Desktop\\Coding Projects\\open_a_2_experiment\\curator-tool\\plugins.json")
#    test.begin_classifier()