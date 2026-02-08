# Cómo Implementar Audio Real en el Bot de TeamSpeak

## ❓ ¿Por qué necesito algo extra para el audio?

TeamSpeak 3 **NO tiene una API oficial para streaming de audio**. Solo permite:
- Enviar mensajes de texto (ServerQuery)
- Mover usuarios
- Gestionar canales
- Pero **NO transmitir audio programáticamente**

## 🎯 3 Soluciones Reales (sin SinusBot)

### Solución 1: Usar TS3AudioBot (Recomendada) ⭐

**TS3AudioBot** es un bot open-source en C# que SÍ puede transmitir audio.

#### Ventajas:
✅ Funciona perfectamente  
✅ Open source y gratis  
✅ Tiene API REST que puedes controlar desde Python  
✅ Soporta yt-dlp nativamente  

#### Implementación:

**docker-compose.yml actualizado:**
```yaml
version: '3.8'

services:
  ts3audiobot:
    image: tsab/ts3audiobot:latest
    container_name: ts3audiobot
    restart: unless-stopped
    volumes:
      - ./ts3audiobot-data:/app/data
      - ./downloads:/app/music
    ports:
      - "58913:58913"  # API REST
    environment:
      - TS3_ADDRESS=${TS3_HOST}
      - TS3_NICKNAME=${BOT_NICKNAME}
      - TS3_CHANNEL=${TS3_CHANNEL}
      - TS3_PASSWORD=${TS3_SERVER_PASSWORD}

  music-controller:
    build: .
    container_name: music-controller
    depends_on:
      - ts3audiobot
    environment:
      - TS3AUDIOBOT_API=http://ts3audiobot:58913
    volumes:
      - ./downloads:/app/downloads
```

**Código Python para controlar TS3AudioBot:**
```python
import requests

class TS3AudioBotController:
    def __init__(self, api_url="http://localhost:58913"):
        self.api_url = api_url
    
    def play(self, url):
        """Reproducir URL"""
        response = requests.post(
            f"{self.api_url}/bot/play",
            json={"url": url}
        )
        return response.json()
    
    def stop(self):
        """Detener reproducción"""
        requests.post(f"{self.api_url}/bot/stop")
    
    def skip(self):
        """Saltar canción"""
        requests.post(f"{self.api_url}/bot/next")
    
    def get_current(self):
        """Obtener canción actual"""
        response = requests.get(f"{self.api_url}/bot/current")
        return response.json()

# Uso:
bot = TS3AudioBotController()
bot.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

---

### Solución 2: Usar Audio Virtual (PulseAudio/ALSA)

Ejecutar un cliente de TeamSpeak real en el contenedor con audio virtual.

#### Pasos:

1. **Instalar cliente TS3 en Docker**
2. **Crear dispositivo de audio virtual**
3. **Pipe audio de ffmpeg al dispositivo virtual**

**Dockerfile extendido:**
```dockerfile
FROM python:3.11-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    pulseaudio \
    teamspeak3-client \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Configurar PulseAudio
RUN pulseaudio --start

# ... resto de configuración
```

**Script para pipe de audio:**
```bash
#!/bin/bash
# Crear sink virtual
pactl load-module module-null-sink sink_name=ts3_input

# Reproducir con ffmpeg
ffmpeg -i song.mp3 -f pulse ts3_input
```

**Problemas:**
❌ Muy complejo  
❌ Requiere cliente gráfico (Xvfb)  
❌ Difícil de mantener  

---

### Solución 3: Implementar Protocolo TS3 Directamente

Usar librerías que implementan el protocolo de voz de TS3.

**Librería recomendada: `ts3-python-bot`**

```python
from ts3bot import TS3Bot, ServerConnection

class MusicBot(TS3Bot):
    def __init__(self):
        super().__init__()
        self.connection = ServerConnection(
            host="ts3.example.com",
            port=9987,
            nickname="MusicBot"
        )
    
    def send_audio(self, audio_data):
        """Enviar datos de audio al servidor"""
        # Codificar con Opus
        encoded = self.opus_encoder.encode(audio_data, 960)
        
        # Enviar paquete UDP
        self.connection.send_voice_packet(encoded)
    
    def play_file(self, filepath):
        """Reproducir archivo"""
        # Leer archivo con ffmpeg
        process = subprocess.Popen([
            'ffmpeg', '-i', filepath,
            '-f', 's16le',
            '-ar', '48000',
            '-ac', '1',
            'pipe:1'
        ], stdout=subprocess.PIPE)
        
        # Leer y enviar en chunks
        while True:
            chunk = process.stdout.read(1920)  # 20ms @ 48kHz
            if not chunk:
                break
            self.send_audio(chunk)
```

**Problemas:**
❌ Muy complejo  
❌ Debes implementar el protocolo de voz  
❌ Requiere manejo de Opus codec  
❌ Problemas de sincronización  

---

## 🏆 Recomendación Final

### Para Producción: **Usa TS3AudioBot (Solución 1)**

Es la forma más confiable y mantenible. Tu bot Python controla TS3AudioBot vía API REST.

**Arquitectura:**
```
Usuario en TS3 → !play comando
       ↓
Bot Python (tu código)
       ↓
TS3AudioBot API
       ↓
TS3AudioBot reproduce en TS3
```

### Para Desarrollo/Testing: **Solución 2 con cliente virtual**

Si quieres aprender o experimentar.

### Para Expertos: **Solución 3 protocolo directo**

Solo si necesitas control total y eres muy experimentado.

---

## 📦 Implementación Completa con TS3AudioBot

Te preparo un `docker-compose.yml` completo que integra todo:

```yaml
version: '3.8'

services:
  # TS3AudioBot - Maneja el audio
  ts3audiobot:
    image: splamy/ts3audiobot:latest
    container_name: ts3audiobot
    restart: unless-stopped
    volumes:
      - ./ts3audiobot:/app/config
      - ./downloads:/app/music
    environment:
      - WEBAPI_ENABLED=true
      - WEBAPI_PORT=58913
    networks:
      - ts3-network

  # Tu bot Python - Maneja comandos y lógica
  music-bot:
    build: .
    container_name: music-bot
    restart: unless-stopped
    depends_on:
      - ts3audiobot
    environment:
      - TS3_HOST=${TS3_HOST}
      - TS3AUDIOBOT_API=http://ts3audiobot:58913
      - BOT_NICKNAME=${BOT_NICKNAME}
    volumes:
      - ./downloads:/app/downloads
    networks:
      - ts3-network

networks:
  ts3-network:
    driver: bridge
```

**Resultado:** Bot funcionando completamente con audio real, sin necesidad de SinusBot comercial.

---

## ❌ SinusBot vs TS3AudioBot

| Característica | SinusBot | TS3AudioBot |
|---------------|----------|-------------|
| Precio | Gratis (limitado) / Pago | 100% Gratis |
| Código | Cerrado | Open Source |
| Personalización | Limitada | Total |
| API | Sí | Sí |
| Docker | Sí | Sí |
| Actualizaciones | Lentas | Activas |

**Conclusión:** No necesitas SinusBot. TS3AudioBot es mejor, gratis y open source.
