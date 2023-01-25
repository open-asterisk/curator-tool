# Open Asterisk
# CLI Module
import os
import asyncio

from modules.exporters import sqlite_exporter
from modules.breach_data import combolist
from tqdm import tqdm

COMBOLIST_FOLDER = "D:\\DATA_LEAKS\\Databases\\COMBOLISTS"

def process_folder(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files_processed = 0
    with tqdm(total=len(files), desc="Importing dumps", position=1) as pbar:
        for file in files:
            try:
                tqdm.write(f"[OPEN ASTERISK] PROCESSING {file}")
                extractor = combolist.CombolistExtractor()
                data = extractor.extract_data(os.path.join(folder, file))
                data_exporter = sqlite_exporter.SQLiteExporter('db.sql')
                asyncio.run(data_exporter.before())
                asyncio.run(data_exporter.create_table('combolists', data[0]))
                asyncio.run(data_exporter.add_bulk_data('combolists', data))
                asyncio.run(data_exporter.after())
                files_processed += 1
                pbar.update()
            except Exception as e:
                tqdm.write(f"[OPEN ASTERISK] ERROR WHEN PROCESSING {file}: {e}")
                pass

    tqdm.write(f"[OPEN ASTERISK] PROCESSED {files_processed} DUMPS")

if __name__ == '__main__':
    process_folder(COMBOLIST_FOLDER)