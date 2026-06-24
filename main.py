from pydantic import BaseModel

from fastapi import FastAPI, HTTPException

analyses_bd = []

app = FastAPI()


class TextRequest(BaseModel):
    text: str


class AnalysisResponse(BaseModel):
    id: int
    char_count: int
    word_count: int
    sentence_count: int


@app.post("/analyze")
async def analyze(request: TextRequest):
    text = request.text

    char_count = len(text)
    word_count = len(text.split())
    sentence_count = text.count(".")
    analysis_id = len(analyses_bd) + 1

    result = AnalysisResponse(
        char_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
        id=analysis_id,
    )
    analyses_bd.append(result)

    return result


@app.get("/get_all_analyses")
async def analyzes():
    return analyses_bd


@app.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    for analysis in analyses_bd:
        if analysis.id == analysis_id:
            return analysis
    raise HTTPException(status_code=404, detail="wrong ID")
