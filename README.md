# Bot de Música para TeamSpeak 3

Bot de música para TeamSpeak 3 que usa yt-dlp para reproducir música de YouTube y otras plataformas. Listo para ejecutar en Docker.

## Características

- ✅ Descarga y reproduce música de YouTube y más de 1000 sitios soportados por yt-dlp
- ✅ Cola de reproducción
- ✅ Comandos por chat
- ✅ Containerizado con Docker
- ✅ yt-dlp siempre actualizado
- ✅ Fácil de configurar y desplegar

## Requisitos Previos

- Docker y Docker Compose instalados
- Servidor TeamSpeak 3 con acceso ServerQuery
- Credenciales de administrador del servidor TS3

## Instalación

### 1. Clonar o descargar el proyecto

```bash
# Si tienes los archivos
cd ts3-music-bot
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus datos:

```bash
cp .env.example .env
nano .env
```

Configura las siguientes variables:

```env
TS3_HOST=tu-servidor.teamspeak.com
TS3_PORT=10011
TS3_USER=serveradmin
TS3_PASSWORD=tu_password_serverquery
TS3_SERVER_ID=1
TS3_CHANNEL_ID=1
BOT_NICKNAME=MusicBot
```

### 3. Obtener credenciales ServerQuery

Para obtener las credenciales necesitas acceso al servidor TS3:

1. Conéctate a tu servidor TS3 con permisos de administrador
2. Ve a Tools → ServerQuery Login
3. Copia el usuario y contraseña generados
4. El puerto por defecto es 10011

### 4. Construir y ejecutar

```bash
# Construir la imagen
docker-compose build

# Iniciar el bot
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Comandos del Bot

Una vez que el bot esté conectado al canal de TeamSpeak, puedes usar estos comandos:

- `!play <url o búsqueda>` - Reproduce una canción de YouTube u otra plataforma
  - Ejemplo: `!play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
  - Ejemplo: `!play despacito`

- `!skip` - Salta la canción actual

- `!queue` - Muestra la cola de reproducción

- `!np` - Muestra la canción que se está reproduciendo actualmente

- `!help` - Muestra la lista de comandos

## Estructura del Proyecto

```
.
├── Dockerfile              # Imagen Docker del bot
├── docker-compose.yml      # Configuración de Docker Compose
├── bot.py                  # Código principal del bot
├── requirements.txt        # Dependencias de Python
├── .env.example           # Ejemplo de configuración
├── downloads/             # Directorio para archivos descargados
└── cache/                 # Caché de yt-dlp
```

## Actualizar yt-dlp

Para actualizar yt-dlp a la última versión:

```bash
# Reconstruir la imagen
docker-compose build --no-cache

# Reiniciar el bot
docker-compose up -d
```

## Mantenimiento

### Ver logs
```bash
docker-compose logs -f
```

### Detener el bot
```bash
docker-compose down
```

### Reiniciar el bot
```bash
docker-compose restart
```

### Limpiar descargas antiguas
```bash
rm -rf downloads/*
```

## Resolución de Problemas

### El bot no se conecta

1. Verifica que las credenciales ServerQuery sean correctas
2. Asegúrate de que el puerto 10011 esté accesible
3. Revisa los logs: `docker-compose logs -f`

### Error al descargar música

1. Verifica que yt-dlp esté actualizado (reconstruye la imagen)
2. Algunos videos pueden estar bloqueados geográficamente
3. Revisa los logs para ver el error específico

### El bot se desconecta constantemente

1. Verifica la estabilidad de tu conexión de red
2. Asegúrate de que el servidor TS3 no tenga límites de conexiones ServerQuery
3. Revisa los logs del servidor TS3

## Notas Importantes

⚠️ **Nota sobre la reproducción de audio**: Este bot actualmente descarga las canciones pero la reproducción real de audio en TeamSpeak requiere integración adicional con el sistema de audio de TS3. Esto puede lograrse mediante:

1. **SinusBot**: Usar la API de SinusBot como backend
2. **TS3AudioBot**: Integración con TS3AudioBot
3. **Streaming directo**: Implementar streaming de audio directamente

El código actual es una base funcional que maneja la descarga, cola y comandos. Para audio real, considera integrar con alguna de las soluciones anteriores.

## Personalización

### Modificar comandos

Edita el método `handle_command()` en `bot.py` para agregar o modificar comandos.

### Cambiar formato de audio

Modifica `ydl_opts` en `bot.py`:

```python
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'opus',  # Cambiar a opus, m4a, etc.
    'preferredquality': '128',  # Cambiar calidad
}],
```

### Agregar más plataformas

yt-dlp soporta más de 1000 sitios automáticamente. Solo pasa la URL:

- SoundCloud
- Bandcamp
- Vimeo
- Twitch
- Y muchos más

## Licencia

MIT License - Siéntete libre de usar y modificar este proyecto.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Soporte

Si tienes problemas o preguntas, revisa los logs del contenedor y los issues del repositorio.
