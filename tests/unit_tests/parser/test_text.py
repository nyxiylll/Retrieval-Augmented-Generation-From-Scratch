import pytest
from src.ingestion.parser.text import TextLoader
from src.core.document import Document
from pathlib import Path


def test_text_loader(tmp_path):
    file = Path(tmp_path / "notes.txt")

    file.write_text("Helloo!")
    loader = TextLoader(file)
    document = loader.load()
    assert isinstance(document[0],Document) == True
    assert document[0].content == "Helloo!"

def test_file_not_exist():

    with pytest.raises(FileNotFoundError):
        TextLoader("uw.txt")


