# 🚀 Guía Rápida de Inicio

## Paso 1: Preparar archivos

Asegúrate de tener todos estos archivos en una carpeta:

```
ts3-music-bot/
├── Dockerfile
├── docker-compose-with-audio.yml
├── bot_complete.py
├── requirements.txt
├── .env.example
└── start.sh
```

## Paso 2: Configurar

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar con tus datos
nano .env
```

**Configuración mínima necesaria:**

```env
TS3_HOST=tu-servidor.teamspeak.com    # Tu servidor TeamSpeak
TS3_CHANNEL=Music                      # Canal donde estará el bot
BOT_NICKNAME=MusicBot                  # Nombre del bot
```

## Paso 3: Ejecutar script automático

```bash
# Hacer ejecutable
chmod +x start.sh

# Ejecutar
./start.sh
```

El script automáticamente:
- ✅ Verifica Docker
- ✅ Crea directorios necesarios
- ✅ Construye las imágenes
- ✅ Inicia el bot

## Paso 4: Verificar que funciona

```bash
# Ver logs
docker-compose -f docker-compose-with-audio.yml logs -f
```

Deberías ver algo como:
```
✅ Conectado con TS3AudioBot
✅ Bot iniciado correctamente
```

## Paso 5: Probar en TeamSpeak

Conéctate a tu servidor TeamSpeak y escribe en el chat:

```
!play despacito
```

¡El bot debería reproducir música! 🎵

---

## 🎵 Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `!play <url o búsqueda>` | Reproducir música |
| `!skip` | Saltar canción actual |
| `!stop` | Detener y limpiar cola |
| `!pause` | Pausar/Reanudar |
| `!queue` | Ver cola de reproducción |
| `!np` | Canción actual |
| `!volume <0-100>` | Ajustar volumen |
| `!help` | Ver ayuda |

---

## 📋 Comandos de Docker útiles

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose-with-audio.yml logs -f

# Ver solo logs del bot Python
docker-compose -f docker-compose-with-audio.yml logs -f music-bot-controller

# Ver solo logs de TS3AudioBot
docker-compose -f docker-compose-with-audio.yml logs -f ts3audiobot

# Detener el bot
docker-compose -f docker-compose-with-audio.yml down

# Reiniciar el bot
docker-compose -f docker-compose-with-audio.yml restart

# Reconstruir (si cambias código)
docker-compose -f docker-compose-with-audio.yml build --no-cache
docker-compose -f docker-compose-with-audio.yml up -d
```

---

## ❓ Problemas comunes

### El bot no se conecta

1. Verifica que `TS3_HOST` sea correcto
2. Asegúrate de que el servidor TeamSpeak esté accesible
3. Revisa los logs: `docker-compose -f docker-compose-with-audio.yml logs -f`

### Error "TS3AudioBot API not responding"

```bash
# Verifica que TS3AudioBot esté corriendo
docker-compose -f docker-compose-with-audio.yml ps

# Reinicia los contenedores
docker-compose -f docker-compose-with-audio.yml restart
```

### El bot no reproduce audio

1. Verifica que TS3AudioBot esté conectado al servidor
2. Mira los logs de TS3AudioBot: 
   ```bash
   docker-compose -f docker-compose-with-audio.yml logs ts3audiobot
   ```

### Actualizar yt-dlp

```bash
# Reconstruir imagen
docker-compose -f docker-compose-with-audio.yml build --no-cache

# Reiniciar
docker-compose -f docker-compose-with-audio.yml up -d
```

---

## 🔄 Actualizar el bot

Si haces cambios en `bot_complete.py`:

```bash
# Reconstruir solo el bot Python
docker-compose -f docker-compose-with-audio.yml build music-bot-controller

# Reiniciar
docker-compose -f docker-compose-with-audio.yml up -d
```

---

## 📊 Monitoreo

Ver estado de los contenedores:
```bash
docker-compose -f docker-compose-with-audio.yml ps
```

Ver uso de recursos:
```bash
docker stats
```

---

## 🛑 Detener completamente

```bash
# Detener y eliminar contenedores
docker-compose -f docker-compose-with-audio.yml down

# Detener y eliminar TODO (incluyendo volúmenes)
docker-compose -f docker-compose-with-audio.yml down -v
```

---

## ✅ Checklist de verificación

- [ ] Docker y Docker Compose instalados
- [ ] Archivo `.env` configurado con tus datos
- [ ] Puerto 58913 disponible (para API de TS3AudioBot)
- [ ] Servidor TeamSpeak accesible
- [ ] Todos los archivos presentes en la carpeta

¡Listo! Tu bot debería estar funcionando. 🎉
