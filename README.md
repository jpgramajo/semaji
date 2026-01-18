# Semaji: Interacción Conversacional Fluida y Procesamiento Local

Semaji (del swahili: "Aquel que habla") es un agente de IA diseñado para lograr una comunicación fluida y natural por audio sin depender de servidores externos. El proyecto busca facilitar diálogos dinámicos que ocurren íntegramente de forma local, permitiendo que la inteligencia resida en tu propio hardware con una latencia mínima y privacidad absoluta.

A través de una arquitectura optimizada para la concurrencia, Semaji permite una interacción orgánica donde la IA procesa el lenguaje y ejecuta la voz de forma simultánea. Al funcionar totalmente offline, se eliminan los tiempos de espera por red y se garantiza que cada conversación sea privada, rápida y siempre disponible, incluso sin conexión a internet.

## 🛠️ Especificaciones Técnicas y Arquitectura

El sistema utiliza una arquitectura de hilos concurrentes (*Multi-threading*) para maximizar el rendimiento del hardware y mantener la estabilidad del flujo de audio:

* **Motor de Inferencia LLM**: Optimizado para **Gemma 3 (12B)** a través de Ollama. Implementa una técnica de inyección de *System Prompt* mediante simulación de historial, asegurando respuestas concisas, amigables y libres de sintaxis Markdown para facilitar la lectura del TTS.
* **Reconocimiento de Voz (STT)**: Uso de **OpenAI Whisper** (modelo medium recomendado) para una transcripción precisa de la voz del usuario en tiempo real.
* **Síntesis de Voz por Streaming (TTS)**: Basada en **espeak-ng**. El sistema fragmenta el texto generado por el LLM en cuanto detecta signos de puntuación (. , ? !), permitiendo que la IA hable mientras sigue procesando el resto de la respuesta.
* **Gestión de Audio Estable**: Flujo de entrada de micrófono persistente mediante **PortAudio/ALSA**, evitando errores de hardware al alternar entre captura y reproducción.

## 🚀 Pruebas en Hardware (Edge Computing)

Semaji ha sido probado con éxito en entornos de alto rendimiento, demostrando estabilidad y baja latencia en:
* **Dispositivo**: NVIDIA Jetson AGX Xavier Dev Kit.
* **Memoria**: 32GB LPDDR4x.
* **Rendimiento**: Ejecución paralela de Gemma 3 12B y Whisper sin degradación térmica o de memoria significativa.

## 🗺️ Hoja de Ruta (Roadmap)

La visión de Semaji es evolucionar hacia un agente totalmente autónomo:
1. **Voz Natural de Alta Fidelidad**: Migración hacia motores de TTS neuronales con entonación emocional.
2. **Orquestación de Herramientas (Tool Use)**: Capacidad para que el agente ejecute acciones en el sistema operativo o controle dispositivos externos.
3. **Multimodalidad Avanzada**: Integración de visión en tiempo real para que el agente pueda comprender el entorno físico del usuario.

## ⚙️ Instalación y Requisitos

1. **Dependencias del sistema**: Requiere `Ollama`, `espeak-ng` y `aplay`.
2. **Python Setup**:
   ```bash
   pip install sounddevice soundfile numpy openai-whisper requests
   ```
3. **Ejecución**:
   ```bash
   python3 voice_ai_stable.py
   ```

Semaji — Tu voz, tus datos, tu hardware.
