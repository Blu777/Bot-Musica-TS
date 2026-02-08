#!/usr/bin/env python3
"""
Bot de Música para TeamSpeak 3 con Audio Real
Integrado con TS3AudioBot para transmisión de audio
"""

import os
import time
import logging
import requests
import yt_dlp
from queue import Queue
from threading import Thread
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TS3AudioBotAPI:
    """Cliente para la API de TS3AudioBot"""
    
    def __init__(self, api_url, api_key=None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def _request(self, method, endpoint, **kwargs):
        """Realizar petición HTTP"""
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.request(
                method, 
                url, 
                headers=self.headers,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a TS3AudioBot: {e}")
            return None
    
    def play(self, url):
        """Reproducir URL (YouTube, SoundCloud, etc.)"""
        return self._request('POST', '/api/bot/play', json={'url': url})
    
    def stop(self):
        """Detener reproducción"""
        return self._request('POST', '/api/bot/stop')
    
    def pause(self):
        """Pausar reproducción"""
        return self._request('POST', '/api/bot/pause')
    
    def volume(self, level):
        """Ajustar volumen (0-100)"""
        return self._request('POST', f'/api/bot/volume/{level}')
    
    def skip(self):
        """Saltar a la siguiente canción"""
        return self._request('POST', '/api/bot/next')
    
    def get_status(self):
        """Obtener estado actual del bot"""
        return self._request('GET', '/api/bot/status')
    
    def get_current_track(self):
        """Obtener información de la canción actual"""
        return self._request('GET', '/api/bot/current')
    
    def send_message(self, message):
        """Enviar mensaje al canal"""
        return self._request('POST', '/api/bot/message', json={'message': message})


class TSMusicBotComplete:
    """Bot de música completo con audio real"""
    
    def __init__(self):
        # Configuración de TS3AudioBot API
        self.audiobot_api_url = os.getenv('TS3AUDIOBOT_API', 'http://localhost:58913')
        self.audiobot_api_key = os.getenv('TS3AUDIOBOT_API_KEY', '')
        self.audiobot = TS3AudioBotAPI(self.audiobot_api_url, self.audiobot_api_key)
        
        # Configuración general
        self.download_path = '/app/downloads'
        self.queue = Queue()
        self.current_track = None
        self.is_playing = False
        self.auto_play = True
        
        # Configuración de yt-dlp para obtener info
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'extract_flat': False,
        }
    
    def get_video_info(self, query):
        """Obtener información del video sin descargar"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                return {
                    'title': video.get('title', 'Unknown'),
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', 'Unknown'),
                    'url': video.get('webpage_url', query),
                    'thumbnail': video.get('thumbnail', ''),
                }
        except Exception as e:
            logger.error(f"Error al obtener info: {e}")
            return None
    
    def format_duration(self, seconds):
        """Formatear duración en formato MM:SS"""
        if not seconds:
            return "?:??"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"
    
    def add_to_queue(self, query, requester="Unknown"):
        """Agregar canción a la cola"""
        logger.info(f"Procesando: {query}")
        
        # Obtener información
        track_info = self.get_video_info(query)
        if not track_info:
            logger.error("No se pudo obtener información del video")
            return None
        
        track_info['requester'] = requester
        
        # Si no hay nada reproduciéndose, reproducir directamente
        if not self.is_playing and self.queue.empty():
            return self.play_now(track_info)
        else:
            # Agregar a la cola
            self.queue.put(track_info)
            logger.info(f"Agregado a la cola: {track_info['title']}")
            return track_info
    
    def play_now(self, track_info):
        """Reproducir canción inmediatamente"""
        logger.info(f"Reproduciendo: {track_info['title']}")
        
        # Usar TS3AudioBot para reproducir
        result = self.audiobot.play(track_info['url'])
        
        if result:
            self.current_track = track_info
            self.is_playing = True
            
            # Enviar mensaje al canal
            duration = self.format_duration(track_info.get('duration'))
            message = f"🎵 Reproduciendo: {track_info['title']} [{duration}] - Pedido por {track_info['requester']}"
            self.audiobot.send_message(message)
            
            return track_info
        else:
            logger.error("Error al reproducir con TS3AudioBot")
            return None
    
    def skip_current(self):
        """Saltar canción actual"""
        if self.is_playing:
            logger.info("Saltando canción actual")
            self.audiobot.skip()
            self.is_playing = False
            return True
        return False
    
    def stop_playback(self):
        """Detener reproducción"""
        logger.info("Deteniendo reproducción")
        self.audiobot.stop()
        self.is_playing = False
        self.current_track = None
    
    def get_queue_list(self):
        """Obtener lista de canciones en cola"""
        queue_list = []
        if self.current_track:
            queue_list.append({
                'position': 0,
                'current': True,
                **self.current_track
            })
        
        for i, track in enumerate(list(self.queue.queue), 1):
            queue_list.append({
                'position': i,
                'current': False,
                **track
            })
        
        return queue_list
    
    def monitor_playback(self):
        """Monitorear estado de reproducción y reproducir siguiente"""
        logger.info("Iniciando monitor de reproducción")
        
        while True:
            try:
                # Verificar estado actual
                status = self.audiobot.get_status()
                
                if status:
                    # Si no está reproduciendo y hay cola, reproducir siguiente
                    if not status.get('playing', False) and not self.queue.empty():
                        logger.info("Reproduciendo siguiente canción de la cola")
                        next_track = self.queue.get()
                        self.play_now(next_track)
                    elif not status.get('playing', False):
                        self.is_playing = False
                        self.current_track = None
                
                time.sleep(2)  # Verificar cada 2 segundos
                
            except Exception as e:
                logger.error(f"Error en monitor: {e}")
                time.sleep(5)
    
    def handle_text_command(self, command, args, sender="Unknown"):
        """Manejar comandos de texto"""
        command = command.lower()
        
        if command == "!play" or command == "!p":
            if not args:
                return "❌ Uso: !play <url o búsqueda>"
            
            track = self.add_to_queue(args, sender)
            if track:
                duration = self.format_duration(track.get('duration'))
                if self.is_playing:
                    pos = self.queue.qsize()
                    return f"✅ Agregado a la cola (#{pos}): {track['title']} [{duration}]"
                else:
                    return f"▶️ Reproduciendo: {track['title']} [{duration}]"
            else:
                return "❌ Error al procesar la canción"
        
        elif command == "!skip" or command == "!s":
            if self.skip_current():
                return "⏭️ Canción saltada"
            else:
                return "❌ No hay nada reproduciéndose"
        
        elif command == "!stop":
            self.stop_playback()
            # Limpiar cola
            while not self.queue.empty():
                self.queue.get()
            return "⏹️ Reproducción detenida y cola limpiada"
        
        elif command == "!pause":
            self.audiobot.pause()
            return "⏸️ Reproducción pausada/reanudada"
        
        elif command == "!queue" or command == "!q":
            queue = self.get_queue_list()
            if not queue:
                return "📭 La cola está vacía"
            
            msg = "📋 Cola de reproducción:\n"
            for item in queue:
                duration = self.format_duration(item.get('duration'))
                prefix = "▶️" if item['current'] else f"{item['position']}."
                msg += f"{prefix} {item['title']} [{duration}] - {item['requester']}\n"
            
            return msg
        
        elif command == "!np" or command == "!now":
            if self.current_track:
                duration = self.format_duration(self.current_track.get('duration'))
                return f"🎵 Reproduciendo: {self.current_track['title']} [{duration}]"
            else:
                return "❌ No hay nada reproduciéndose"
        
        elif command == "!volume" or command == "!vol":
            if not args or not args.isdigit():
                return "❌ Uso: !volume <0-100>"
            
            level = int(args)
            if 0 <= level <= 100:
                self.audiobot.volume(level)
                return f"🔊 Volumen ajustado a {level}%"
            else:
                return "❌ El volumen debe estar entre 0 y 100"
        
        elif command == "!help" or command == "!h":
            return """
🎵 Comandos del Bot de Música:
!play <url/búsqueda> - Reproducir canción
!skip - Saltar canción actual
!stop - Detener y limpiar cola
!pause - Pausar/Reanudar
!queue - Ver cola de reproducción
!np - Canción actual
!volume <0-100> - Ajustar volumen
!help - Mostrar esta ayuda
            """.strip()
        
        return None
    
    def run(self):
        """Iniciar el bot"""
        logger.info("=" * 50)
        logger.info("Bot de Música para TeamSpeak con Audio Real")
        logger.info("Integrando con TS3AudioBot...")
        logger.info("=" * 50)
        
        # Verificar conexión con TS3AudioBot
        status = self.audiobot.get_status()
        if not status:
            logger.error("❌ No se pudo conectar con TS3AudioBot")
            logger.error(f"API URL: {self.audiobot_api_url}")
            logger.error("Asegúrate de que TS3AudioBot esté ejecutándose")
            return
        
        logger.info("✅ Conectado con TS3AudioBot")
        
        # Iniciar monitor de reproducción
        monitor_thread = Thread(target=self.monitor_playback, daemon=True)
        monitor_thread.start()
        
        logger.info("✅ Bot iniciado correctamente")
        logger.info("Esperando comandos...")
        
        # Enviar mensaje de inicio
        self.audiobot.send_message("🎵 MusicBot está listo! Usa !help para ver los comandos")
        
        # Mantener vivo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Deteniendo bot...")
            self.audiobot.send_message("👋 MusicBot se está desconectando...")


if __name__ == '__main__':
    bot = TSMusicBotComplete()
    bot.run()
