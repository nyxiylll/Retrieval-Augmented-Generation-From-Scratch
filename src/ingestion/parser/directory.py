from src.ingestion.parser.base import BaseLoader
from src.ingestion.parser.pdf import PDFLoader
from src.ingestion.parser.text import TextLoader
from pathlib import Path
import logging 
import glob 

logger = logging.getLogger(__name__)


class DirectoryLoader(BaseLoader):

    def __init__(self,
                directory_path : str | Path,
                text_encoding : str | None = None,
                text_auto_encoding : bool | None = None,
                include_filetype : list[str] | None = None,
                loaders = list[str]
                ):

        self.directory = Path(directory_path)
        self.text_encoding = text_encoding
        self.text_auto_encoding = text_auto_encoding
        self.file_types = include_filetype
        self.loader = loaders

        if not self.directory.exists:
            raise FileNotFoundError(
                f"Directory named {self.directory} not found"
            )




    def _list(self):
        pass

#PROJECT_PATH =  Path(__file__).resolve().parent.parent.parent.parent
#
#if __name__ == "__main__":
#    file_path = Path(PROJECT_PATH / "f")
#    if file_path.is_dir():
#        files = glob.glob(file_path,recursive=True)
#        print(files)
#        print(True)
#    else:
#        print(False)
#    print(file_path)
