# Semaji: Interactua con LLMs de forma natural y privada

Semaji (del swahili: "el que habla") es un asistente de voz pensado para que charlar con un LLM se sienta fluido y real. A diferencia de otros sistemas, Semaji funciona totalmente en tu equipo (offline), por lo que tus conversaciones no salen de tu dispositivo y las respuestas son más rápidas al no depender de internet.

El proyecto se enfoca en que la charla sea orgánica: la IA puede "hablar" mientras sigue "pensando", evitando esas pausas largas que cortan la comunicación.

## 🌟 El objetivo: Una charla más natural
No buscamos solo un asistente que interactue, sino un compañero capaz de:
* Mantener conversaciones coherentes y con contexto.
* Interactuar con su entorno (usar herramientas para controlar luces, archivos o sensores).
* Ver y escuchar (multimodalidad) para entender mejor lo que pasa a su alrededor.

## 🚀 Probado en hardware real
Este sistema ha sido probado con éxito en una NVIDIA Jetson AGX Xavier Dev Kit (32GB), logrando que modelos como Gemma 3 (12B) y Whisper funcionen al mismo tiempo sin problemas.

## ✨ ¿Qué hace ahora?
* Micrófono siempre activo: No hay errores al abrir o cerrar el audio; siempre está listo para escucharte.
* Voz rápida: Empieza a hablar en cuanto detecta un signo de puntuación, lo que hace la respuesta mucho más ágil.
* Privacidad total: Todo se queda en tu RAM. No hay rastreo ni envío de datos a nubes externas.

## 🗺️ Lo que viene (Hoja de ruta)
1. Voces más reales: Cambiar el tono robótico por voces con más emoción y naturalidad.
2. Uso de herramientas: Que la IA pueda ejecutar acciones reales en tu computadora o casa.
3. Visión: Añadir cámaras para que el agente pueda ver lo que le estás mostrando.

## 🛠️ Requisitos
* Ollama (con modelo gemma3:12b).
* Whisper (para entender lo que dices).
* Dispositivo de audio "PRO".

## 💻 Instalación
1. Clona el repo:
   git clone https://github.com/tu-usuario/semaji.git
2. Instala lo necesario:
   pip install sounddevice soundfile numpy openai-whisper requests
3. Ejecuta:
   python3 voice_ai_stable.py

Semaji - Tu voz, tus datos, tu hardware.
