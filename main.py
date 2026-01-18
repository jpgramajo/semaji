import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import time
import os
import queue
import subprocess
import requests
import json
import threading
from datetime import datetime

# --- CONFIGURACIÓN ---
WHISPER_MODEL = "medium"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:12b"
MAX_CONTEXT_PAIRS = 24

# Configuración de voz (TTS)
SPEECH_VOLUME = 16
SPEECH_SPEED = 150

# PROMPT DEL SISTEMA (Simulado como interacción inicial)
SYSTEM_PROMPT = (
    "Eres una inteligencia artificial amable y concisa. Responde siempre en español. "
    "Tus respuestas deben ser cortas y directas, máximo dos oraciones. "
    "IMPORTANTE: No uses ningún tipo de formato Markdown (nada de asteriscos, negritas, "
    "listas o símbolos especiales). Habla de forma natural y fluida."
)

# Delimitadores para fragmentar el habla y sus pausas
DELIMITERS = {
    ".": 0.5, "?": 0.6, "!": 0.5, ",": 0.2, ";": 0.3, ":": 0.3, ")": 0.2
}

# Tiempos de hardware
CLICK_THRESHOLD = 0.4
SAMPLE_RATE = 16000
CHANNELS = 1
OUTPUT_FILENAME = "ultima_grabacion.wav"
START_DELAY = 0.3
END_TRIM_SECONDS = 0.5
DEBOUNCE_TIME = 1.5

# Archivos de efectos
START_EFFECT = "start_record_effect.wav"
END_EFFECT = "end_record_effect.wav"
# ---------------------

audio_queue = queue.Queue()
speech_queue = queue.Queue()
chat_history = []
is_ai_busy = False # Flag para saber si la IA está pensando o hablando

def find_pro_device():
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if "PRO" in dev['name']: return i
    return None

def find_pro_device_id():
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if "PRO" in dev['name']:
            if "hw:" in dev['name']:
                try: return dev['name'].split("hw:")[1].split(",")[0]
                except: pass
            return str(i)
    return None

def set_hardware_volume(card_id):
    try:
        subprocess.run(f"amixer -c {card_id} sset PCM 100% --quiet", shell=True)
        subprocess.run(f"amixer -c {card_id} sset Speaker 100% --quiet", shell=True)
        subprocess.run(f"amixer -c {card_id} sset Playback 100% --quiet", shell=True)
    except Exception: pass

def speech_worker():
    """Hilo de voz: procesa frases y gestiona el estado de ocupado."""
    global is_ai_busy
    card_id = find_pro_device_id()
    if not card_id: return
    device_target = f"plughw:{card_id}"
    
    while True:
        phrase_data = speech_queue.get()
        if phrase_data is None: break
        
        text, pause_duration = phrase_data
        text = text.strip()
        
        if text:
            set_hardware_volume(card_id)
            clean_text = text.replace('"', '\\"').replace('*', '')
            # Usamos -q en aplay para evitar logs innecesarios
            cmd = f'espeak-ng -a {SPEECH_VOLUME} -v es+m3 -s {SPEECH_SPEED} "{clean_text}" --stdout | aplay -D {device_target} -q'
            os.system(cmd)
            time.sleep(pause_duration)
        
        speech_queue.task_done()
        
        # Si la cola está vacía, marcamos que la IA ya no está ocupada
        if speech_queue.empty():
            time.sleep(0.2) # Pequeño margen extra
            is_ai_busy = False

def init_chat_history():
    global chat_history
    print(f"--- [SISTEMA] Configurando historial... ---")
    chat_history = [
        {"role": "user", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Entendido. Responderé de forma corta y amigable."}
    ]

def warm_up_model():
    print(f"--- [SISTEMA] Despertando a {OLLAMA_MODEL}... ---")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": "Responde con un Ok simple."}],
        "stream": False
    }
    try:
        requests.post(OLLAMA_URL, json=payload, timeout=40)
        print(f"--- [SISTEMA] Modelo cargado con éxito. ---")
        return True
    except Exception: return False

def get_ollama_stream(user_input):
    global chat_history, is_ai_busy
    is_ai_busy = True # IA empieza a procesar
    
    chat_history.append({"role": "user", "content": user_input})
    if len(chat_history) > (MAX_CONTEXT_PAIRS * 2):
        chat_history = chat_history[:2] + chat_history[-(MAX_CONTEXT_PAIRS * 2 - 2):]

    payload = {"model": OLLAMA_MODEL, "messages": chat_history, "stream": True}
    full_response_content = ""
    current_buffer = ""

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60)
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                full_response_content += content
                current_buffer += content

                for char in current_buffer:
                    if char in DELIMITERS:
                        idx = current_buffer.find(char)
                        speech_queue.put((current_buffer[:idx+1], DELIMITERS[char]))
                        current_buffer = current_buffer[idx+1:]
                        break
        
        if current_buffer.strip():
            speech_queue.put((current_buffer, 0.5))

        chat_history.append({"role": "assistant", "content": full_response_content})
    except Exception as e:
        print(f"Error LLM: {e}")
        is_ai_busy = False

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

def play_effect(filename, device_id):
    try:
        if os.path.exists(filename):
            data, fs = sf.read(filename)
            sd.play(data, fs, device=device_id)
            sd.wait()
    except: pass

def main():
    global is_ai_busy
    threading.Thread(target=speech_worker, daemon=True).start()
    init_chat_history()
    
    if not warm_up_model(): return

    pro_index = find_pro_device()
    stt_model = whisper.load_model(WHISPER_MODEL)
    print("--- [LISTO] El micrófono se mantendrá abierto continuamente. ---")

    is_recording = False
    recording_buffer = []
    last_trigger_time = 0
    
    # El stream NO se cierra ni se detiene nunca
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                            device=pro_index, callback=audio_callback)

    try:
        with stream:
            while True:
                try:
                    data_chunk = audio_queue.get(timeout=0.1)
                except queue.Empty: continue

                # Si la IA está ocupada hablando, ignoramos el audio capturado
                if is_ai_busy and not is_recording:
                    continue

                max_val = np.max(np.abs(data_chunk))
                current_time = time.time()

                if max_val > CLICK_THRESHOLD and (current_time - last_trigger_time) > DEBOUNCE_TIME:
                    last_trigger_time = current_time
                    
                    if not is_recording:
                        # Si el usuario pulsa mientras la IA hablaba, silenciar cola
                        is_ai_busy = False
                        while not speech_queue.empty():
                            try: speech_queue.get_nowait()
                            except: break
                        
                        print(f"\n--- GRABANDO ---")
                        play_effect(START_EFFECT, pro_index)
                        with audio_queue.mutex: audio_queue.queue.clear()
                        time.sleep(START_DELAY)
                        is_recording = True
                        recording_buffer = []
                    else:
                        print(f"--- PROCESANDO ---")
                        is_recording = False
                        is_ai_busy = True # Marcamos como ocupado para no detectar ecos
                        
                        play_effect(END_EFFECT, pro_index)
                        
                        if len(recording_buffer) > 0:
                            full_audio = np.concatenate(recording_buffer, axis=0)
                            trim_samples = int(END_TRIM_SECONDS * SAMPLE_RATE)
                            if len(full_audio) > trim_samples:
                                full_audio = full_audio[:-trim_samples]
                            
                            sf.write(OUTPUT_FILENAME, full_audio, SAMPLE_RATE)
                            
                            result = stt_model.transcribe(OUTPUT_FILENAME)
                            text = result['text'].strip()
                            
                            if text:
                                print(f"USUARIO: {text}")
                                # Inicia hilo de Ollama para no bloquear el bucle principal
                                threading.Thread(target=get_ollama_stream, args=(text,), daemon=True).start()
                            else:
                                print("No detectado.")
                                is_ai_busy = False
                        
                        recording_buffer = []
                        # Limpiar audio acumulado durante el procesamiento
                        with audio_queue.mutex: audio_queue.queue.clear()

                if is_recording:
                    recording_buffer.append(data_chunk)

    except KeyboardInterrupt:
        print("\nCerrando...")

if __name__ == "__main__":
    main()
