from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	ELEVENLABS_API_KEY: str # variable obligatòria
	VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
	TTS_MODEL_ID: str = "eleven_multilingual_v2"

	MODE: str = "llm"
	GROQ_API_KEY: str | None = None
	GROQ_MODEL: str = "llama-3.1-8b-instant"

	OPENAI_API_KEY: str | None = None
	LLM_MODEL: str = "llama-3.1-8b-instant"

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"