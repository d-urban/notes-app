from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import database

app = FastAPI()

database.init_db()


class NoteRequest(BaseModel):
    title: str
    body: str
    subtitle: str = ""


@app.get("/")
def serve_frontend():
    return FileResponse("index.html")


@app.get("/notes")
def get_notes():
    return database.get_all_notes()


@app.post("/notes", status_code=201)
def create_note(note: NoteRequest):
    return database.create_note(note.title, note.body, note.subtitle)


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteRequest):
    database.update_note(note_id, note.title, note.body, note.subtitle)
    return {"message": "Note updated"}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    database.delete_note(note_id)
    return {"message": "Note deleted"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
