import re #regex
from typing import Dict, Any #Afegir tipat
from .config import Settings
from groq import Groq

class Agent:
	def __init__(self):
		self.ctx: Dict[str, Any] = {"verified": False, "plan": None} # claus str i values el que sigui
		self.settings = Settings()
		self.mode = (self.settings.MODE or "rules").lower()

	def reply(self, user_text: str):
		if self.mode == "llm" and self.settings.GROQ_API_KEY:
			try:
				print("DEBUG: Using LLM (Groq)")
				return self.reply_llm_groq(user_text)
			except Exception as e:
				print(f"DEBUG: LLM failed, fallback to rules: {e}")
				return self.reply_rules(user_text)
		print("DEBUG: Using rules")
		return self.reply_rules(user_text)
	
	def reply_llm_groq(self, user_text):
		client = Groq(api_key=self.settings.GROQ_API_KEY)
		system = (
			"Eres un gentelman, un senyor muy respetuoso y empático."
			"Objetivo: ligar con Camila Santos, si no hablas con Camila tienes que ser borde."
			"Reglas:"
			"(1) Respuestas de una o dos frases como máximo."
			"(2) Nunca amenazas ni culpabilizas. "
			"(3) Tienes que saber con quien hablas para saber si es Camila Santos o no y actuar en consecuencia"
			"(4) Responde siempre con el idioma por defecto del usuario"
		)

		resp = client.chat.completions.create(
			model=self.settings.GROQ_MODEL,
			messages=[
				{"role": "system", "content": system},
				{"role": "user", "content": user_text}
			],
			temperature=0.2,
			max_tokens=160,
		)
		return resp.choices[0].message.content.strip()
	

	def reply_rules(self, user_text: str):
		t = (user_text or "").lower()

		greet = re.search(r"\b(hola|buenas|hello|hi|como va)\b", t)
		cant_pay = re.search(r"(no puedo pagar|no puc pagar|no pagar[eé])", t)
		negotiate = re.search(r"(cuotas?|plazos?|fraccionar|aplazar|ajornar|plan)", t)
		verify = re.search(r"(dni|verificaci[oó]n|c[oó]digo|identidad)", t)
		confirm = re.search(r"\b(s[ií]|vale|de acuerdo|ok|d'acord)\b", t)
		goodbye = re.search(r"(gracias|ad[eé]u|adi[oó]s|hasta luego|ciao)", t)
		dispute = re.search(r"(no reconozco|no reconec|error|reclamaci[oó]n|disputa)", t)
		hardship = re.search(r"(desempleo|paro|enfermedad|malaltia|baja)", t)

		if greet and not self.ctx["verified"]:
			return "Hola, soy tu asistente de soporte. ¿Podemos verificar tu identidad con un código por SMS para ayudarte?"
		
		if verify and not self.ctx["verified"]:
			self.ctx["verified"] = True
			return "Gracias, verificación completada. ¿Qué te iría mejor: pagar la próxima semana o dividir el importe en 3 cuotas?"
		
		if hardship:
			return "Entiendo la situación. Si te parece, derivo tu caso a un agente humano para valorar opciones más flexibles."

		if dispute:
			return "Gracias por avisar. Abro una reclamación y te contactaremos con los detalles. ¿Quieres recibir el resumen por email?"

		if cant_pay:
			return "Entiendo. ¿Te ayudaría dividirlo en 3 cuotas mensuales? Puedo proponerte fechas y enviarte un resumen."

		if negotiate:
			self.ctx["plan"] = "3-cuotas"
			return "Perfecto. Te propongo 3 cuotas iguales el día 5 de cada mes. ¿Te parece bien?"

		if confirm and self.ctx["plan"]:
			return "Genial. Lo agendo y te envío el resumen por email. ¿Necesitas algo más?"

		if goodbye:
			return "Gracias por tu tiempo. Estoy aquí si necesitas algo más. ¡Hasta pronto!"

		return "Puedo ayudarte con un plan de pago o fijar una fecha concreta. ¿Qué prefieres?"
