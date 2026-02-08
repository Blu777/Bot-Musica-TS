#!/bin/bash

echo "======================================"
echo "🎵 Bot de Música para TeamSpeak"
echo "Con Audio Real - Instalación Completa"
echo "======================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker instalado${NC}"
echo ""

# Crear directorios
echo "📁 Creando directorios necesarios..."
mkdir -p downloads cache ts3audiobot-config ts3audiobot-data

# Verificar archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Creado .env desde .env.example${NC}"
    else
        echo "Creando archivo .env básico..."
        cat > .env << 'EOF'
# Configuración del servidor TeamSpeak 3
TS3_HOST=localhost
TS3_CHANNEL=Music
BOT_NICKNAME=MusicBot
TS3_SERVER_PASSWORD=
EOF
    fi
    
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edita el archivo .env con tus datos de TeamSpeak${NC}"
    echo ""
    echo "Configuración mínima requerida:"
    echo "  TS3_HOST=tu-servidor-ts3.com"
    echo "  TS3_CHANNEL=Music"
    echo ""
    
    read -p "¿Quieres editar .env ahora? (s/n): " edit_now
    
    if [ "$edit_now" = "s" ] || [ "$edit_now" = "S" ]; then
        ${EDITOR:-nano} .env
    else
        echo -e "${RED}Recuerda editar .env antes de iniciar el bot${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}✅ Archivo .env configurado${NC}"
echo ""

# Verificar archivos necesarios
required_files=("docker-compose-with-audio.yml" "bot_complete.py" "Dockerfile" "requirements.txt")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${RED}❌ Archivos faltantes:${NC}"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Asegúrate de tener todos los archivos en esta carpeta."
    exit 1
fi

echo -e "${GREEN}✅ Todos los archivos presentes${NC}"
echo ""

# Construir imágenes
echo "🔨 Construyendo imagen Docker..."
docker-compose -f docker-compose-with-audio.yml build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al construir la imagen${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
echo ""

# Preguntar si iniciar
read -p "¿Quieres iniciar el bot ahora? (s/n): " start_now

if [ "$start_now" = "s" ] || [ "$start_now" = "S" ]; then
    echo ""
    echo "🚀 Iniciando bot..."
    docker-compose -f docker-compose-with-audio.yml up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ ¡Bot iniciado correctamente!${NC}"
        echo ""
        echo "📋 Comandos útiles:"
        echo "  Ver logs:      docker-compose -f docker-compose-with-audio.yml logs -f"
        echo "  Detener bot:   docker-compose -f docker-compose-with-audio.yml down"
        echo "  Reiniciar bot: docker-compose -f docker-compose-with-audio.yml restart"
        echo ""
        echo "🎵 Comandos del bot en TeamSpeak:"
        echo "  !play <url o búsqueda> - Reproducir música"
        echo "  !skip - Saltar canción"
        echo "  !queue - Ver cola"
        echo "  !help - Ver todos los comandos"
        echo ""
        echo "Conectándote a tu servidor TeamSpeak para probarlo..."
        sleep 3
        echo ""
        echo "📊 Mostrando logs (Ctrl+C para salir):"
        docker-compose -f docker-compose-with-audio.yml logs -f
    else
        echo -e "${RED}❌ Error al iniciar el bot${NC}"
        exit 1
    fi
else
    echo ""
    echo "Para iniciar el bot manualmente:"
    echo "  docker-compose -f docker-compose-with-audio.yml up -d"
    echo ""
fi
