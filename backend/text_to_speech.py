from pathlib import Path #per crear rures d'arxius
from uuid import uuid4 #per crear noms únics de fitxers
from elevenlabs.client import ElevenLabs
from .config import Settings

settings = Settings()
client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

AUDIO_DIR = Path(__file__).resolve().parents[1]/ "static"/"audio" # carpera on guardarem els mp3
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Rebem text, generem veu (mp3) i retornem la URL de l'mp3 guardat
def tts_to_file(text, language="es-ES"):
	filename = f"{uuid4().hex}.mp3"
	out_path = AUDIO_DIR / filename

	voice_map = {
		"es-ES": settings.VOICE_ID_ES_MALE,  # Española
		"en-US": settings.VOICE_ID_EN,  # Inglesa
		"fr-FR": settings.VOICE_ID_FR,  # Francesa
	}
	voice_id = voice_map.get(language, settings.VOICE_ID_ES_MALE)

	# creem un iterador amb l'audio
	audio_iter = client.text_to_speech.convert(
		text=text,
		voice_id=voice_id,
		model_id=settings.TTS_MODEL_ID,
		output_format="mp3_44100_128", # 44.1 kHz i 128 kbps
	)

	with open(out_path, 'wb') as fd: #'wb' -> write binary
		for chunk in audio_iter:
			if not chunk:
				continue
			fd.write(chunk if isinstance(chunk, (bytes, bytearray)) else bytes(chunk))
	
	return f"/static/audio/{filename}"