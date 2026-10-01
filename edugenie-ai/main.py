from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="EduGenie AI",
    description="Google Gemini Powered Educational Assistant",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static and template directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Root Endpoint: Web Interface
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EduGenie AI"}

# Q&A - GET API using Gemini
@app.get("/qa")
async def answer_question(question: str = Query(...)):
    try:
        from qna import answer_question_with_gemini
        answer = answer_question_with_gemini(question)
        return {"answer": answer}
    except Exception as error:
        return JSONResponse(
            content={"error": f"Feature dependency unavailable: {error}"},
            status_code=503
        )

# Explanation - POST API (supports both with and without trailing slash)
@app.post("/explain/")
@app.post("/explain")
async def explain_api(request: Request):
    try:
        from explanation_module import explain_topic
        data = await request.json()
    except Exception as error:
        return dependency_error(error)
    topic = data.get("topic")
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    return {"topic": topic, "explanation": explain_topic(topic)}

# Summarization - POST API (supports both with and without trailing slash)
@app.post("/summarize/")
@app.post("/summarize")
async def summarize_api(request: Request):
    try:
        from summary_module import summarize_text
        data = await request.json()
    except Exception as error:
        return dependency_error(error)
    text = data.get("text")
    if not text:
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)
    return {"summary": summarize_text(text)}

# Quiz Generation - POST API (supports both with and without trailing slash)
@app.post("/quiz")
@app.post("/quiz/")
async def quiz_api(request: Request):
    try:
        from quiz_module import generate_quiz
        data = await request.json()
    except Exception as error:
        return dependency_error(error)
    text = data.get("text")
    if not text:
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)
    return JSONResponse(content={"quiz": generate_quiz(text)})

# Learning Recommendations - GET API
@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str = Query(...)):
    try:
        from learning_path import get_learning_recommendations
        return {
            "topic": topic,
            "recommendation": get_learning_recommendations(topic)
        }
    except Exception as error:
        return dependency_error(error)

def dependency_error(error: Exception):
    return JSONResponse(
        content={"error": f"Feature dependency unavailable: {error}"},
        status_code=503
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
