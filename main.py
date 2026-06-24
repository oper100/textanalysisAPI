from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

analyses_bd = []
next_id = 0

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
    global next_id
    text = request.text

    char_count = len(text)
    word_count = len(text.split())
    sentence_count = text.count(".")
    next_id += 1

    result = AnalysisResponse(
        char_count=char_count,
        word_count=word_count,
        sentence_count=sentence_count,
        id=next_id,
    )
    analyses_bd.append(result)

    return result


@app.get("/analyses")
async def get_all_analyses():
    return analyses_bd


@app.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    for analysis in analyses_bd:
        if analysis.id == analysis_id:
            return analysis
    raise HTTPException(status_code=404, detail="wrong ID")


@app.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int):
    for analysis in analyses_bd:
        if analysis.id == analysis_id:
            analyses_bd.remove(analysis)
            return {"message": "Analysis deleted"}
    raise HTTPException(status_code=404, detail="wrong ID")
