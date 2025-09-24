const chat = document.getElementById("chat");
const input = document.getElementById("textInput")
const sendBtn = document.getElementById("sendBtn")
const micBtn = document.getElementById("micBtn")
const player = document.getElementById("player")

function addBuble(role, text) {
	const div = document.createElement("div");
	div.className = `buble ${role}`
	div.textContent = text;
	chat.appendChild(div)
	chat.scrollTop = chat.scrollHeight;
}

async function ask(text, language = 'es-ES') {
	addBuble("user", text)
	input.value = "";

	// Agent: POST /api/reply
	const r = await fetch("/api/reply", {
		method: "POST",
		headers: {"Content-Type":"application/json"},
		body: JSON.stringify({ text, language })
	});
	const data = await r.json();
	const reply = data.reply_text || "(sin respuesta)";
	addBuble("agent", reply);


	// TTS: POST /api/tts
	const t = await fetch("/api/tts", {
		method: "POST",
		headers: {"Content-Type":"application/json"},
		body: JSON.stringify({text: reply, language})
	});
	const audio = await t.json();
	if (audio.audio_url) {
		player.src = audio.audio_url;
		player.play().catch(()=>{});
	}
}

sendBtn.onclick = () => {
	const text = input.value.trim();
	if (text)
		ask(text);
};

input.addEventListener("keydown", (e) => {
	if (e.key === "Enter")
		sendBtn.click();
});

// STT: gravar i enviar a /api/stt
let mediaStream = null;
let mediaRecorder = null;
let chunks = [];
let recording = false;

async function ensureStream() {
	if (!mediaStream) {
		mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true});
	}
}

micBtn.onclick = async () => {
	if (!recording) {
		try {
			await ensureStream();
			chunks = [];
			mediaRecorder = new MediaRecorder(mediaStream, { mimeType: "audio/webm"});
			mediaRecorder.ondataavailable = (e) => { 
				if (e.data.size > 0) 
					chunks.push(e.data);
			};
			mediaRecorder.onstop = async () => {
				const blob = new Blob(chunks, { type: "audio/webm" });
				const fd = new FormData();
				fd.append("file", blob, "clip.webm");
				fd.append("language", "es-ES"); //ja el detectarem al back

				const res = await fetch("/api/stt", {
					method: "POST",
					body: fd
				});
				const { text, language } = await res.json();
				const finalText = text && text.trim() ? text.trim() : "[no entendido / silencio]";

				ask(finalText, language);

				micBtn.textContent = "🎤 Hablar";
				recording = false;
			};
			mediaRecorder.start();
			recording = true;
			micBtn.textContent = "⏹️ Parar";
		} catch (err) {
			console.error(err);
			alert("No se puede acceder al micro :(")
		}
	} else {
		mediaRecorder.stop();
		micBtn.textContent = "🎤 Hablar";
	}
}