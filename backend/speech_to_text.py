import tempfile # crear directoris i fitxers temporals
import subprocess
from pathlib import Path
from typing import Optional
from langdetect import detect
import speech_recognition as sr


# Reb bytes i els posa en un fitxer temporal
def _bytes_to_tempfile(data: bytes, suffix: str) -> Path:
	tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
	tmp.write(data)
	tmp.flush() # força que totes les dades del buffer s'escriguin al disc
	tmp.close()
	return Path(tmp.name)

# crea el fitxer temporal en un .wav (quan no rebem un WAV)
def _convert_to_wav(src_path: Path) -> Path:
	dst_path = src_path.with_suffix(".wav")
	# ffmpeg -y -i input -ac 1 -ar 16000 output.wav
	cmd = [
		"ffmpeg",
        "-y",
        "-i", str(src_path),
        "-ac", "1",
        "-ar", "16000",
        str(dst_path)
	]
	proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if proc.returncode != 0:
		raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='ignore')}")
	return dst_path

# Reb bytes d'audio i els converteix a WAV 16kHz mono i transcriu
# Torna text
def transcribe_bytes(data: bytes, content_type: Optional[str], language: str = "es-ES") -> str:
	suffix = ".webm"
	if content_type:
		if "wav" in content_type:
			suffix = ".wav"
		elif "ogg" in content_type:
			suffix = ".ogg"
		elif "m4a" in content_type:
			suffix = ".m4a"
		elif "webm" in content_type:
			suffix = ".webm"

	src = _bytes_to_tempfile(data, suffix=suffix)
	wav_path = src if src.suffix == ".wav" else _convert_to_wav(src)
	try:
		r = sr.Recognizer()
		with sr.AudioFile(str(wav_path)) as source:
			audio = r.record(source)
		text = r.recognize_google(audio, language=language) # STT amb google
		text = text.strip()
		text, detected_lang = detect_language(text, audio, language)#text pot canviar si l'idioma estava malament

		return text, detected_lang

	except Exception:
		return "", 'es-ES'
	finally:
		try:
			src.unlink(missing_ok=True)
		except Exception:
			pass
		if wav_path != src:
			try:
				wav_path.unlink(missing_ok=True)
			except Exception:
				pass

		
def detect_language(text, audio, lang_default):
	lang_map = {
		'es': 'es-ES',
		'en': 'en-US', 
		'fr': 'fr-FR',
		'de': 'de-DE',
		'it': 'it-IT',
		'pt': 'pt-BR'
	}

	try:
		detected_lang = detect(text)
		detected_lang = lang_map.get(detected_lang, 'es-ES')# default es-ES

		if detected_lang != lang_default and detected_lang in lang_map.values():
			try:
				r = sr.Recognizer()
				text = r.recognize_google(audio, language=detected_lang)
				text = text.strip()
			except:
				detected_lang = lang_default
	except:
		detected_lang = 'es-ES'

	return text, detected_lang
