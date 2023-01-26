import importlib
import inspect
import toml
import sys
import os
import itertools

import asyncio
from tqdm import tqdm
from pathlib import Path

def read_config(config_file):
    """
    This function reads the given configuration file and returns its contents as a dictionary.
    If the file does not exist, it raises an exception.

    Parameters:
        config_file (str): The path to the configuration file.

    Returns:
        dict: The contents of the configuration file as a dictionary.

    Raises:
        Exception: If the provided file is not a valid config file.
    """
    # Check if the file exists
    if not os.path.isfile(config_file):
        raise Exception(f"{config_file} is not a valid config file")
    # Open and read the file
    with open(config_file, 'r', encoding='utf-8') as config_options:
        config_file_contents = toml.loads(config_options.read())
    return config_file_contents

def load_curator_modules(user_config):
    """
    This function loads the curator modules specified in the user config.
    It loads only the modules that are enabled in the config.
    It returns a list of dictionaries, each dictionary containing the name and
    instance of a curator module.

    Parameters:
        user_config (dict): The user config containing the information about the curator modules.

    Returns:
        list: A list of dictionaries, each dictionary containing the name and
        instance of a curator module.
    """
    # Create a list for the modules
    modules = []
    for module in user_config["modules"]:
        if module["enabled"]:
            # Create a container dict for the modules
            module_container = {}
            # import and load the module
            location = module["location"]
            module_name = Path(location).stem
            name = module["name"]
            spec = importlib.util.spec_from_file_location(module_name, location)
            mod = importlib.util.module_from_spec(spec)
            # or mod = __import__(location)
            # create an instance of the class
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            instance = getattr(mod, name)()
            module_container["name"] = name
            module_container["instance"] = instance
            modules.append(module_container)
            # Print to the terminal that the a module has been loaded
            print(f"[OPEN ASTERISK] LOADED {name.upper()} MODULE")
    return modules

def load_exporter_modules(user_config):
    """
    This function loads the exporter modules specified in the user config.
    It loads only the modules that are enabled in the config.
    It returns a list of dictionaries, each dictionary containing the name and 
    instance of an exporter module.

    Parameters:
        user_config (dict): The user config containing the information about the exporter modules.

    Returns:
        list: A list of dictionaries, each dictionary containing the name and 
        instance of an exporter module.
    """
    # Create a list for the exporter modules to go into
    exporter_module_container = []
    # Iterate over the config
    for exporter_module in user_config["exporters"]:
        if exporter_module["enabled"]:
            # Create a container for the exporter
            module_container = {}
            # import and load the exporter
            location = exporter_module["location"]
            module_name = Path(location).stem
            name = exporter_module["name"]
            database = exporter_module["database"]
            spec = importlib.util.spec_from_file_location(module_name, location)
            mod = importlib.util.module_from_spec(spec)
            # or mod = __import__(location)
            # create an instance of the extractor class
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            class_instance = getattr(mod, name)
            instance = class_instance(database)
            # Print to the terminal that the a module has been loaded
            module_container["name"] = name
            module_container["instance"] = instance
            exporter_module_container.append(module_container)
            print(f"[OPEN ASTERISK] LOADED {name.upper()} MODULE")
    return exporter_module_container

def execute_export_module(exporter_module, extractor_module, file):
    try:
        # Extract Data From The File
        data = extractor_module["instance"].extract_data(file)
    except Exception:
        tqdm.write(f"[OPEN ASTERISK/{extractor_module['name']}] ERROR IMPORTING {file}: SKIPPING FILE!")
        return
    exporter_name, exporter = exporter_module.values()
    try:
        if not inspect.iscoroutinefunction(exporter.add_data):
            # Create a table for the data using a dict from the extracted
            # Data Values
            exporter.create_table(data)
            for data_entries in data:
                # Iterate over the data dict and insert the data
                exporter.add_data(data_entries)
        # Update the number of files processed
        if inspect.iscoroutinefunction(exporter.create_table):
            # Run the create table function
            if isinstance(data, list):
                asyncio.run(exporter.create_table(
                    f'{extractor_module["name"].lower()}', data[0]))
                # If an add_data_bulk function exists, then use it instead
                if inspect.iscoroutinefunction(exporter.add_bulk_data):
                    asyncio.run(exporter.add_bulk_data(
                        f'{extractor_module["name"].lower()}', data))
                # Otherwise...
                else:
                    # Iterate slowly over the data entries and add them one
                    # by one until they are all inserted in the database.
                    for data_entries in data:
                        asyncio.run(exporter.add_data(
                            f'{exporter_name.lower()}', data_entries))
            # if the data is not a list, then insert it like this
            if not isinstance(data, list):
                asyncio.run(exporter.create_table(
                    f'{extractor_module["name"].lower()}', data))
                # insert the data
                asyncio.run(exporter.add_data(
                    f'{extractor_module["name"].lower()}', data))
    except Exception as ex:
        tqdm.write(f"[OPEN ASTERISK] ERROR WHEN PROCESSING {file}: {ex}")


def process_folder(user_config, exporter_modules, extractor_modules):
    """
    This function processes the files in the given folder, extracts data from them,
    and exports the data to the specified exporter module.

    Parameters:
        folder (str): The path to the folder containing the files to be processed.
        exporter_modules (list): A list of dictionaries, each containing the name and instance of an exporter module.
        extractor_modules (dict): A dictionary containing the name and instance of an extractor module.

    Returns:
        None
    """
    # Create a list of files in the folder
    folders_to_check = user_config["Dumpfolders"]["folders"]
    # Create a list of files that need to be checked
    files = []
    for folder in folders_to_check:
        files.extend([os.path.join(folder, f) for f in os.listdir(folder)
             if os.path.isfile(os.path.join(folder, f))])

    # Create a variable for the number of files that have been processed so far
    files_processed = 0

    # Create a progress bar
    with tqdm(total=len(files), desc="Importing dumps", position=1) as pbar:
        # Iterate through the files that were discovered
        files_processed = 0
        for file in files:
            tqdm.write(f"[OPEN ASTERISK] PROCESSING {file}")
            for exporter_module, extractor_module in list(itertools.product(exporter_modules,
                                                                            extractor_modules)):
                execute_export_module(exporter_module, extractor_module, file)
                files_processed += 1
            # Update the Progress Bar
            pbar.update()
    print(f"[OPEN ASTERISK] PROCESSED {files_processed} FILES")

if __name__ == '__main__':
    with open("banner.txt", encoding='utf-8') as banner:
        print(banner.read())
    config = read_config("./config.toml")
    curator_modules = load_curator_modules(config)
    exporter_modules = load_exporter_modules(config)
    process_folder(config, exporter_modules, curator_modules)