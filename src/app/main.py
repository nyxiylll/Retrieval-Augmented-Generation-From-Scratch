from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
from pathlib import Path

UPLOAD_DIR = Path("Uploaded_Files")
UPLOAD_DIR.mkdir(exist_ok=True)

class QueryRequest(BaseModel):
    session_id : int
    query : str


app = FastAPI()


@app.get("/health_check")
async def check():
    return {"Message" : "Working"}

@app.post("/file_upload")
async def file_upload(file : UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename

        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
        return {"Message" : "Done"}
    except:
        raise 


@app.post("/query")
async def query(request: QueryRequest):
    pass

@app.get("/uploaded_files")
async def uploaded_files(session_id : int):
    pass


@app.delete("/delete_files")
async def delete_files(session_id : int , file_name : str):
    pass
