from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

engine = create_engine("sqlite:///database.db", echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


class TextRequest(BaseModel):
    text: str


class AnalysisResponse(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    char_count: int
    word_count: int
    sentence_count: int
    text: str
    created_at: datetime = Field(default_factory=datetime.now)


@app.post("/analyze")
def analyze(request: TextRequest):
    text = request.text

    char_count = len(text)
    word_count = len(text.split())
    sentence_count = text.count(".")

    result = AnalysisResponse(
        char_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
        text=text,
    )

    with Session(engine) as session:
        session.add(result)
        session.commit()
        session.refresh(result)

    return result


@app.get("/analyses")
def get_all_analyses():
    with Session(engine) as session:
        return session.exec(select(AnalysisResponse)).all()


@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int):
    with Session(engine) as session:
        analysis = session.get(AnalysisResponse, analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Wrong id!")
        return analysis


@app.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int):
    with Session(engine) as session:
        analysis = session.get(AnalysisResponse, analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Wrong id!")
        session.delete(analysis)
        session.commit()
        return {"message:": f"Analysis with id {analysis_id} was deleted!"}
