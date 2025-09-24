from fastapi import FastAPI, UploadFile, File, Form #API REST ràpida d'implementar
from fastapi.responses import FileResponse, JSONResponse # Retornar JSON 
from fastapi.staticfiles import StaticFiles # Servir carpeta estàtica
from pathlib import Path
from .text_to_speech import tts_to_file
from .agent import Agent
from .speech_to_text import transcribe_bytes

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "static"
STATIC = ROOT / "static"

agent = Agent()

app = FastAPI(title="Voice Backend")
# Exposem la carpeta perque el navegador pugui descarregar els mp3
app.mount("/static", StaticFiles(directory=STATIC), name="static")

#ping
@app.get("/health")
def health():
	return {"status": "OK"}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

@app.post("/api/tts")
async def api_tts(payload: dict):
	text = (payload or {}).get("text", "").strip()
	language = (payload or {}).get("language", "es-ES")
	if not text:
		return JSONResponse({"error": "missing text"}, status_code=400)
	url = tts_to_file(text, language)
	return JSONResponse({"audio_url": url})

@app.post("/api/reply")
async def api_reply(payload: dict):
	user_text = (payload or "").get("text", "").strip()
	language = (payload or {}).get("language", "es-ES")
	reply_text = agent.reply(user_text, language)
	return JSONResponse({"reply_text": reply_text})

@app.post("/api/stt")
async def api_stt(file: UploadFile = File(...), language: str = Form("es-ES")):
	data = await file.read()
	text, language = transcribe_bytes(data, content_type=file.content_type, language=language)
	return JSONResponse({"text": text, "language": language})

