# Open Asterisk
# CLI Module
import os
import asyncio

from modules.exporters import sqlite_exporter
from modules.exporters import csv_exporter
from modules.breach_data import combolist
from tqdm import tqdm

COMBOLIST_FOLDER = "D:\\DATA_LEAKS\\TEST_SAMPLE\\COMBOLISTS"

# Process Folder Using SQL Exporter (asyncronous)
def process_folder(folder):
    # Create a list of files in the folder
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files_processed = 0
    # Create a data_exporter object for the sql database
    data_exporter = sqlite_exporter.SQLiteExporter('db.sql')
    # Create an Extractor to Extract the data
    extractor = combolist.CombolistExtractor()
    # Create a progress bar
    with tqdm(total=len(files), desc="Importing dumps", position=1) as pbar:
        for file in files:
            try:
                tqdm.write(f"[OPEN ASTERISK] PROCESSING {file}")
                # Extract Data From The File
                data = extractor.extract_data(os.path.join(folder, file))
                # Run the Before Function before starting the extractor
                asyncio.run(data_exporter.before())
                # Try to Create a table with the first dict value
                asyncio.run(data_exporter.create_table('combolists', data[0]))
                # Add All of the extracted data to the SQL table
                asyncio.run(data_exporter.add_bulk_data('combolists', data))
                # Update the number of files processed
                files_processed += 1
                # Update the progress bar
                pbar.update()
            except Exception as e:
                tqdm.write(f"[OPEN ASTERISK] ERROR WHEN PROCESSING {file}: {e}")
                pass
            
    # After the extraction has finished, run the after function
    asyncio.run(data_exporter.after())
    
    # Write the number of processed files to the terminal
    tqdm.write(f"[OPEN ASTERISK] PROCESSED {files_processed} DUMPS")
    
# Process Folder Using CSV Exporter
def process_folder_csv(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files_processed = 0
    # Create the export options
    data_exporter = csv_exporter.CSVexporter('combos.csv')
    # Run the function before beginning the export
    data_exporter.before()
    # Create the extractor to extract the information from the dump
    extractor = combolist.CombolistExtractor()
    # Create the progress bar
    with tqdm(total=len(files), desc="Importing dumps", position=1) as pbar:
        for file in files:
            try:
                # Process the files
                tqdm.write(f"[OPEN ASTERISK] PROCESSING {file}")
                # Extract the data
                data = extractor.extract_data(os.path.join(folder, file))
                # Create a table for the data using a dict from the extracted
                # Data
                data_exporter.create_table(data[0])
                for data_entries in data:
                    # Iterate over the data dict and insert the data
                    data_exporter.add_data(data_entries)
                # Update the number of files processed
                files_processed += 1
                # Update the Progress Bar
                pbar.update()
            except Exception as e:
                tqdm.write(f"[OPEN ASTERISK] ERROR WHEN PROCESSING {file}: {e}")
                pass
    # Run the After Function after all the data has been extracted
    data_exporter.after()
    
    # Print how many files were processed to the terminal
    tqdm.write(f"[OPEN ASTERISK] PROCESSED {files_processed} DUMPS")

if __name__ == '__main__':
    # Run The Folder Extractor
    process_folder_csv(COMBOLIST_FOLDER)