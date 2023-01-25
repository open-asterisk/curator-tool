# Open Asterisk
# Module Template
import abc

class Exporter(abc.ABC):
    """
    Abstract class for exporting data. Subclasses should implement methods for
    connecting to a data source, creating tables, and adding data.
    """

    @staticmethod
    @abc.abstractmethod
    def before():
        """
        Connect to the data source. Or do anything important
        before the module starts
        """
        pass

    @classmethod
    @abc.abstractmethod
    def create_table(cls):
        """
        Create a table in the data source.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def add_data(cls):
        """
        Add data to the table in the data source.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def after(cls):
        """
        Close the connection to the data source if necessary.
        Also perform any necessary actions once the module has finished.
        """
        pass

class aExporter(abc.ABC):
    """
    Abstract class for exporting data. Subclasses should implement methods for
    connecting to a data source, creating tables, and adding data.
    """
    
    @staticmethod
    @abc.abstractmethod
    async def before():
        """
        Connect to the data source. Or do anything important
        before the module starts
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    async def create_table(cls):
        """
        Create a table in the data source.
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def add_data(cls):
        """
        Add data to the table in the data source.
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    async def after(cls):
        """
        Close the connection to the data source if necessary.
        Also perform any necessary actions once the module has finished.
        """
        pass

class Extractor(abc.ABC):
    """
    Abstract class for creating data extractors. Subclasses should implement methods
    for checking the file, processing the file, and finally returning data
    """
    
    @staticmethod
    @abc.abstractmethod
    def check_file():
        """
        Check if the file meets the criteria to be processed
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    def extract_data(cls):
        """
        check the file to see if it meets the criteria to be processed
        if not, raise an exception.
        Extract data from the file and return it
        """
        pass