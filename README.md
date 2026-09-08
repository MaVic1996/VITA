# V.I.T.A.

**Virtual Intelligent Task Assistant** es un asistente personal de terminal en español. Puede conversar, gestionar Google Calendar, recordar preferencias del usuario y operar mediante texto o voz.

## Funcionalidades

- Gestión de eventos de Google Calendar: listar, crear, modificar y eliminar.
- Comprensión de fechas relativas en español: `hoy`, `mañana`, `el jueves`, `la semana que viene`, etc.
- Preferencias persistentes: nombre, zona horaria, idioma y duración predeterminada de eventos.
- Confirmación explícita antes de modificar o eliminar eventos.
- Entrada de voz con Whisper.cpp.
- Salida de voz local con Piper.
- Modos de uso por texto, archivo de audio, grabación temporizada y conversación por voz.

## Requisitos

- Python 3.11 o superior.
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.
- [Ollama](https://ollama.com/) en ejecución con un modelo compatible con tool calling. La configuración actual usa `gemma4`.
- Una cuenta de Google y credenciales OAuth de escritorio para Google Calendar.
- [Whisper.cpp](https://github.com/ggml-org/whisper.cpp) compilado y un modelo multilingüe.
- Micrófono y altavoz para los modos de voz.

En Linux, `sounddevice` necesita PortAudio. En sistemas Debian/Ubuntu suele bastar con:

```bash
sudo apt install libportaudio2 portaudio19-dev
```

## Instalación

Clona el repositorio e instala las dependencias:

```bash
git clone <URL_DEL_REPOSITORIO>
cd VITA
uv sync
```

El proyecto incluye Piper como dependencia Python. `uv sync` instala el ejecutable `piper` dentro de `.venv/bin/`.

### 1. Configurar Ollama

Instala y arranca Ollama siguiendo su documentación. Después descarga el modelo configurado:

```bash
ollama pull gemma4
```

Por defecto V.I.T.A. se conecta a `http://localhost:11434`. Puedes cambiar el modelo y la URL en `.env`.

### 2. Configurar Google Calendar

1. En [Google Cloud Console](https://console.cloud.google.com/), crea o selecciona un proyecto.
2. Habilita **Google Calendar API**.
3. Crea unas credenciales OAuth de tipo **Desktop app**.
4. Descarga el archivo JSON y guárdalo como:

   ```text
   credentials/google_client_secret.json
   ```

En el primer uso que requiera Calendar, se abrirá el flujo de autorización en el navegador. Tras completarlo se generará `credentials/token.json`.

Si revocas el acceso o el token deja de ser válido, renómbralo y vuelve a iniciar V.I.T.A.:

```bash
mv credentials/token.json credentials/token.json.bak
uv run vita
```

### 3. Instalar Whisper.cpp

Whisper.cpp se mantiene fuera del repositorio de V.I.T.A. Compílalo siguiendo su documentación oficial. Una instalación básica es:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
cmake -B build
cmake --build build --config Release
bash ./models/download-ggml-model.sh small
```

El modelo `small` es multilingüe y ofrece un buen equilibrio entre calidad y velocidad para español. En una Raspberry Pi puede convenir usar `base` o `small` según sus recursos.

### 4. Descargar una voz de Piper

Desde la raíz de V.I.T.A. descarga una voz española:

```bash
mkdir -p models/piper
uv run python -m piper.download_voices \
  --data-dir models/piper \
  es_ES-davefx-medium
```

Esto descarga el modelo `.onnx` y su archivo `.onnx.json`, ambos necesarios. Puedes escuchar otras voces en las [muestras de Piper](https://rhasspy.github.io/piper-samples/).

## Configuración

Copia el archivo de ejemplo y completa las rutas absolutas de tu máquina:

```bash
cp .env.example .env
```

Ejemplo para macOS o Linux:

```dotenv
# Ollama
VITA_OLLAMA_MODEL=gemma4
VITA_OLLAMA_BASE_URL=http://localhost:11434

# Whisper.cpp
VITA_WHISPER_EXECUTABLE=/ruta/a/whisper.cpp/build/bin/whisper-cli
VITA_WHISPER_MODEL=/ruta/a/whisper.cpp/models/ggml-small.bin

# Piper
VITA_PIPER_EXECUTABLE=/ruta/a/VITA/.venv/bin/piper
VITA_PIPER_MODEL=/ruta/a/VITA/models/piper/es_ES-davefx-medium.onnx
```

`.env`, los modelos, audios, credenciales y la base de datos local están excluidos de Git.

## Uso

### Modo texto

```bash
uv run vita
```

Escribe `salir` para cerrar la sesión.

### Enviar un archivo de audio

```bash
uv run vita --audio files/consulta.wav
```

### Grabar durante un tiempo fijo

```bash
uv run vita --record 5
```

### Conversación por voz

```bash
uv run vita --voice
```

Pulsa Intro para iniciar y detener cada grabación. V.I.T.A. transcribe el audio, ejecuta las herramientas necesarias y reproduce su respuesta con Piper. Escribe `salir` para terminar.

## Desarrollo y calidad

Ejecuta la suite de pruebas y el linter antes de hacer cambios:

```bash
uv run pytest -q
uv run ruff check .
```

Para que Ruff aplique sus correcciones automáticas:

```bash
uv run ruff check --fix .
```

## Estructura relevante

```text
src/vita/
├── agent/          # Bucle conversacional, prompt y confirmaciones
├── calendar/       # Cliente de Google Calendar
├── dates/          # Resolución de fechas relativas
├── llm/            # Cliente de Ollama
├── memory/         # Preferencias persistentes en SQLite
├── speech/
│   ├── recording/      # Captura de micrófono
│   ├── transcription/  # Whisper.cpp
│   ├── synthesis/      # Piper
│   └── playback/       # Reproducción de WAV
└── tools/          # Herramientas disponibles para el agente
```

## Notas

- Piper funciona de forma local y es adecuado para macOS, Linux y equipos ARM como Raspberry Pi. Revisa la licencia de Piper y de cada voz antes de distribuir el proyecto.
- Ollama está desacoplado de la entrada/salida de audio: Whisper.cpp y Piper pueden seguir siendo locales aunque el modelo conversacional se ejecute en otro equipo o servicio compatible.
- La API de Google Calendar puede crear y consultar eventos. Las modificaciones y eliminaciones requieren confirmación explícita.
