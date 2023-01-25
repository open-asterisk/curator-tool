# Open asterisk
# Microsoft Office Data Extractor
import os
import asyncio
from sqlite_exporter import SQLiteExporter
from module import Extractor

class MicrosoftOfficeExtractor(Extractor):
    """
    Microsoft Office Metadata Extractor
    Extracts metadata from Microsoft Office Documents

    Args:
        Extractor (class): Extractor Base Class
    """

    name = "Microsoft Office Metadata Extractor"
    author = "ef1500"
    version = "1.0"

    def check_file(self, file: str):
        """Check if the file meets
        the criteria to be used by the module

        Args:
            file (str): the file in question
        """
        accepted = [".docx", ".xlsx", ".pptx"]
        _, file_ext = os.path.splitext(file.lower())
        return file_ext in accepted

    def extract_data(self, file: str):
        """Extract the metadata from the office
        document

        Args:
            file (str): file in question
        """
        if self.check_file(file) is False:
            raise ValueError("Invalid File Type. Must be a .docx, .xlsx or .pptx file.")

        import zipfile
        from dataclasses import dataclass, asdict
        from xml.etree import ElementTree as ET

        @dataclass
        class OfficeDocument:
            """
            Storage dataclass for the metadata
            """
            title: str = "None"
            subject: str = "None"
            creator: str = "None"
            keywords: str = "None"
            description: str = "None"
            lastmodifiedby: str = "None"
            revision: str = "1"
            version: str = "1"
            created: str = "None"
            modified: str = "None"

        office_document = OfficeDocument()
        with zipfile.ZipFile(file) as docx_zip:
            core_props = docx_zip.read('docProps/core.xml')
            ET.register_namespace("", "http://purl.org/dc/elements/1.1/")
            root = ET.fromstring(core_props)
            mapping = {
                '{http://purl.org/dc/elements/1.1/}title': 'title',
                '{http://purl.org/dc/elements/1.1/}subject': 'subject',
                '{http://purl.org/dc/elements/1.1/}creator': 'creator',
                '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}keywords': 'keywords',
                '{http://purl.org/dc/elements/1.1/}description': 'description',
                '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}revision': 'revision',
                '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy': 'lastmodifiedby',
                '{http://purl.org/dc/terms/}created': 'created',
                '{http://purl.org/dc/terms/}modified': 'modified',
            }
            for child in root:
                field_name = mapping.get(child.tag)
                if child.text is not None:
                    setattr(office_document, field_name, child.text)

            return asdict(office_document)

# Debug Run
#if __name__ == '__main__':
#    m = MicrosoftOfficeExtractor()
#    ex = SQLiteExporter('db.sql')
#    d = m.extract_data("./modules/metadata/AUTOUPDATE.docx")
#    asyncio.run(ex.before())
#    asyncio.run(ex.create_table("metadata", d))
#    asyncio.run(ex.add_data("metadata", d))
#    asyncio.run(ex.after())
#    print(d)