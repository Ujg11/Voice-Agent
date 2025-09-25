import re #regex
import uuid
from typing import Dict, Any #Afegir tipat
from .config import Settings
from groq import Groq
from .database import init_db, save_message, get_recent_messages
from .roles import ROLES

class Agent:
	def __init__(self):
		self.ctx: Dict[str, Any] = {"verified": False, "plan": None} # claus str i values el que sigui
		self.settings = Settings()
		self.mode = (self.settings.MODE or "rules").lower()
		self.session_id = str(uuid.uuid4())
		init_db()
		self.ctx["history"] = []

	def reply(self, user_text: str, language: str = "es-ES", role_id: str = "collections_es"):
		if self.mode == "llm" and self.settings.GROQ_API_KEY:
			try:
				print("DEBUG: Using LLM (Groq)")
				reply_text = self.reply_llm_groq(user_text, language, role_id)
			except Exception as e:
				print(f"DEBUG: LLM failed, fallback to rules: {e}")
				reply_text =  self.reply_rules(user_text)
		else:
			reply_text = self.reply_rules(user_text)
		save_message(self.session_id, user_text, reply_text, language)
		self.ctx["history"] = get_recent_messages(self.session_id) # fem update al historial
		return reply_text
	

	def reply_llm_groq(self, user_text, language, role_id):
		client = Groq(api_key=self.settings.GROQ_API_KEY)
		role = ROLES.get(role_id) or ROLES["collections_es"]
		system = role["system"]
		messages = [{"role": "system", "content": system}]

		for m in role.get("fewshots", []):
			messages.append(m)

		for u, a, _lang in self.ctx.get("history", [])[-5:]:
			if u:
				messages.append({"role":"user", "content":u})
			if a:
				messages.append({"role":"assistant","content":a})
		messages.append({"role":"user", "content":user_text})

		resp = client.chat.completions.create(
			model=self.settings.GROQ_MODEL,
			messages=messages,
			temperature=0.3,
			max_tokens=160,
		)
		if resp.choices and len(resp.choices) > 0:
			return resp.choices[0].message.content.strip()
		else:
			return "Lo siento, no pude generar una respuesta."
	

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
