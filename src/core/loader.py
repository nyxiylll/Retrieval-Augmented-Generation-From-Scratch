from src.core.document import Document
from abc import ABC , abstractmethod
from pathlib import Path
from charset_normalizer import from_path
from src.core.exception import LoaderError
import logging 

logger = logging.getLogger(__name__)
class BaseLoader(ABC):


    @abstractmethod
    def load(self):
        pass


class TextLoader(BaseLoader):

    SUPPORTED_TYPE = {".txt"}
    MAX_FILE_SIZE = 50 * 1024 * 1024 #50MB

    def __init__(self,
                file_path : str | Path,
                encoding : str | None = None,
                auto_encoding : bool = False
                ):
        self.file_path = Path(file_path)
        self.encoding = encoding 
        self.auto_encoding = auto_encoding

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"No such file {self.file_path}"
                )

        if not self.file_path.is_file():
            raise LoaderError(
                f"{self.file_path} is not a valid file"
            )

        if self.file_path.suffix.lower() not in self.SUPPORTED_TYPE:
            raise LoaderError(
                f"File type not supported {self.file_path.suffix}"
            )

        size = self.file_path.stat().st_size
        if size > self.MAX_FILE_SIZE:
            raise LoaderError(
                f"File size exeeds the limit"
            )

    def load(self) -> Document:

        used_encoding = self.encoding or "utf-8"

        try: 

            text = self._read(used_encoding)

        except (UnicodeDecodeError,LookupError) as e:
            if not self.auto_encoding :
                raise LoaderError(
                    f"Failed to decode file {self.file_path}"
                    f"{used_encoding}"
                ) from e 

            used_encoding = self._detect_endoding()

            try:

                text = self._read(used_encoding)

            except (UnicodeDecodeError,LookupError) as e2:
                raise LoaderError(
                    f"Auto encoder detected {used_encoding} still failed"
                ) from e2

        except OSError as e:
            raise LoaderError(
                f"Failed to read file {self.file_path}"
            ) from e

        if not text.strip():
            logger.warning(f"Loaded File is empty {self.file_path}")

        return Document(
            content = text,
            metadata = {
                "file_path" : str(self.file_path),
                "file_type" : self.file_path.suffix,
                "encoding" : used_encoding,
                "text_length" : len(text)
            }
        )

    def _read(self,encoding : str) -> str:
        with open(self.file_path,"r",encoding=encoding) as f:
            return f.read()

    def _detect_endoding(self) -> str:
        result = from_path(self.file_path).best()
        if not result:
            raise LoaderError(
                f"Cound not detect encoding"
            )
        return result.encoding
