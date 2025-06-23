#!/bin/bash

# Explorador de Archivos Linux - Instalador Automático
# Autor: Rodolfo Tav
# Versión: 1.0

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ÉXITO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ADVERTENCIA]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para detectar la distribución
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="centos"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    
    print_status "Distribución detectada: $DISTRO"
}

# Función para detectar el gestor de paquetes
detect_package_manager() {
    if command -v apt > /dev/null 2>&1; then
        PKG_MANAGER="apt"
        PKG_INSTALL="apt install -y"
        PKG_UPDATE="apt update"
    elif command -v pacman > /dev/null 2>&1; then
        PKG_MANAGER="pacman"
        PKG_INSTALL="pacman -S --noconfirm"
        PKG_UPDATE="pacman -Sy"
    elif command -v dnf > /dev/null 2>&1; then
        PKG_MANAGER="dnf"
        PKG_INSTALL="dnf install -y"
        PKG_UPDATE="dnf check-update"
    elif command -v yum > /dev/null 2>&1; then
        PKG_MANAGER="yum"
        PKG_INSTALL="yum install -y"
        PKG_UPDATE="yum check-update"
    elif command -v zypper > /dev/null 2>&1; then
        PKG_MANAGER="zypper"
        PKG_INSTALL="zypper install -y"
        PKG_UPDATE="zypper refresh"
    else
        print_error "No se pudo detectar un gestor de paquetes soportado"
        exit 1
    fi
    
    print_status "Gestor de paquetes: $PKG_MANAGER"
}

# Función para verificar si se ejecuta como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script necesita permisos de administrador"
        print_status "Por favor ejecute: sudo $0"
        exit 1
    fi
}

# Función para verificar conectividad
check_connectivity() {
    print_status "Verificando conectividad a internet..."
    if ! ping -c 1 google.com > /dev/null 2>&1; then
        print_error "No hay conexión a internet"
        exit 1
    fi
    print_success "Conexión a internet verificada"
}

# Función para actualizar repositorios
update_repositories() {
    print_status "Actualizando repositorios..."
    case $PKG_MANAGER in
        "apt")
            $PKG_UPDATE
            ;;
        "pacman")
            $PKG_UPDATE
            ;;
        "dnf"|"yum")
            $PKG_UPDATE || true  # dnf check-update retorna 100 si hay actualizaciones
            ;;
        "zypper")
            $PKG_UPDATE
            ;;
    esac
    print_success "Repositorios actualizados"
}

# Función para instalar Python y pip
install_python() {
    print_status "Instalando Python y herramientas..."
    
    case $PKG_MANAGER in
        "apt")
            $PKG_INSTALL python3 python3-pip python3-venv python3-tk python3-pil python3-pil.imagetk python3-psutil
            ;;
        "pacman")
            $PKG_INSTALL python python-pip python-virtualenv tk python-pillow python-psutil
            ;;
        "dnf"|"yum")
            $PKG_INSTALL python3 python3-pip python3-virtualenv python3-tkinter python3-pillow python3-pillow-tk python3-psutil
            ;;
        "zypper")
            $PKG_INSTALL python3 python3-pip python3-virtualenv python3-tk python3-Pillow python3-psutil
            ;;
    esac
    
    print_success "Python instalado correctamente"
}

# Función para instalar dependencias multimedia
install_multimedia() {
    print_status "Instalando herramientas multimedia..."
    
    case $PKG_MANAGER in
        "apt")
            $PKG_INSTALL vlc eog evince gimp imagemagick ffmpeg gstreamer1.0-plugins-base \
                        gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
                        audacious rhythmbox totem libreoffice-impress libreoffice-writer libreoffice-calc
            ;;
        "pacman")
            $PKG_INSTALL vlc eog evince gimp imagemagick ffmpeg gstreamer gst-plugins-base \
                        gst-plugins-good gst-plugins-bad gst-plugins-ugly audacious rhythmbox totem \
                        libreoffice-fresh
            ;;
        "dnf"|"yum")
            $PKG_INSTALL vlc eog evince gimp ImageMagick ffmpeg gstreamer1-plugins-base \
                        gstreamer1-plugins-good gstreamer1-plugins-bad-free audacious rhythmbox totem \
                        libreoffice
            ;;
        "zypper")
            $PKG_INSTALL vlc eog evince gimp ImageMagick ffmpeg gstreamer-plugins-base \
                        gstreamer-plugins-good gstreamer-plugins-bad audacious rhythmbox totem \
                        libreoffice
            ;;
    esac
    
    print_success "Herramientas multimedia instaladas"
}

# Función para instalar herramientas de archivos
install_file_tools() {
    print_status "Instalando herramientas de gestión de archivos..."
    
    case $PKG_MANAGER in
        "apt")
            $PKG_INSTALL file-roller unzip p7zip-full p7zip-rar unrar-free gedit mousepad \
                        kate nano vim file tree mlocate xdg-utils
            ;;
        "pacman")
            $PKG_INSTALL file-roller unzip p7zip unrar gedit mousepad kate nano vim file tree mlocate xdg-utils
            ;;
        "dnf"|"yum")
            $PKG_INSTALL file-roller unzip p7zip p7zip-plugins unrar gedit mousepad kate nano vim \
                        file tree mlocate xdg-utils
            ;;
        "zypper")
            $PKG_INSTALL file-roller unzip p7zip unrar gedit mousepad kate nano vim \
                        file tree mlocate xdg-utils
            ;;
    esac
    
    print_success "Herramientas de archivos instaladas"
}

# Función para instalar herramientas de red
install_network_tools() {
    print_status "Instalando herramientas de red..."
    
    case $PKG_MANAGER in
        "apt")
            $PKG_INSTALL network-manager network-manager-gnome wireless-tools wpasupplicant \
                        pulseaudio pulseaudio-utils pavucontrol alsa-utils
            ;;
        "pacman")
            $PKG_INSTALL networkmanager network-manager-applet wireless_tools wpa_supplicant \
                        pulseaudio pulseaudio-alsa pavucontrol alsa-utils
            ;;
        "dnf"|"yum")
            $PKG_INSTALL NetworkManager NetworkManager-wifi wireless-tools wpa_supplicant \
                        pulseaudio pulseaudio-utils pavucontrol alsa-utils
            ;;
        "zypper")
            $PKG_INSTALL NetworkManager NetworkManager-applet wireless-tools wpa_supplicant \
                        pulseaudio pavucontrol alsa-utils
            ;;
    esac
    
    # Habilitar NetworkManager si no está activo
    if command -v systemctl > /dev/null 2>&1; then
        systemctl enable NetworkManager
        systemctl start NetworkManager
    fi
    
    print_success "Herramientas de red instaladas"
}

# Función para instalar herramientas del sistema
install_system_tools() {
    print_status "Instalando herramientas del sistema..."
    
    case $PKG_MANAGER in
        "apt")
            $PKG_INSTALL htop neofetch curl wget git terminator gnome-terminal \
                        gnome-system-monitor baobab gparted
            ;;
        "pacman")
            $PKG_INSTALL htop neofetch curl wget git terminator gnome-terminal \
                        gnome-system-monitor baobab gparted
            ;;
        "dnf"|"yum")
            $PKG_INSTALL htop neofetch curl wget git terminator gnome-terminal \
                        gnome-system-monitor baobab gparted
            ;;
        "zypper")
            $PKG_INSTALL htop neofetch curl wget git terminator gnome-terminal \
                        gnome-system-monitor baobab gparted
            ;;
    esac
    
    print_success "Herramientas del sistema instaladas"
}

# Función para descargar e instalar el explorador de archivos
install_file_explorer() {
    print_status "Instalando Explorador de Archivos Linux..."
    
    INSTALL_DIR="/opt/linux-file-explorer"
    mkdir -p $INSTALL_DIR
    
    print_status "Copiando archivos del explorador..."
    cp ./file_explorer.py $INSTALL_DIR/
    
    cat > $INSTALL_DIR/launch.sh << 'EOF'
#!/bin/bash
cd /opt/linux-file-explorer
python3 file_explorer.py
EOF

    chmod +x $INSTALL_DIR/file_explorer.py
    chmod +x $INSTALL_DIR/launch.sh

    create_desktop_shortcut
    create_menu_entry

    print_success "Explorador de archivos instalado en $INSTALL_DIR"
}

# Función para crear acceso directo en el escritorio
create_desktop_shortcut() {
    print_status "Creando acceso directo en el escritorio..."
    
    # Buscar el directorio del escritorio del usuario actual
    if [ -n "$SUDO_USER" ]; then
        USER_HOME=$(eval echo ~$SUDO_USER)
        DESKTOP_DIR="$USER_HOME/Escritorio"
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$USER_HOME/Desktop"
        fi
    else
        DESKTOP_DIR="$HOME/Desktop"
    fi
    
    if [ -d "$DESKTOP_DIR" ]; then
        cat > "$DESKTOP_DIR/Explorador-Archivos-Linux.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Explorador de Archivos Linux
Comment=Explorador de archivos completo para nuevos usuarios de Linux
Exec=/opt/linux-file-explorer/launch.sh
Icon=folder
Terminal=false
StartupNotify=true
Categories=System;FileTools;FileManager;
EOF
        
        chmod +x "$DESKTOP_DIR/Explorador-Archivos-Linux.desktop"
        
        # Cambiar propietario si se ejecutó con sudo
        if [ -n "$SUDO_USER" ]; then
            chown $SUDO_USER:$SUDO_USER "$DESKTOP_DIR/Explorador-Archivos-Linux.desktop"
        fi
        
        print_success "Acceso directo creado en el escritorio"
    fi
}

# Función para crear entrada en el menú de aplicaciones
create_menu_entry() {
    print_status "Creando entrada en el menú de aplicaciones..."
    
    mkdir -p /usr/share/applications
    
    cat > /usr/share/applications/linux-file-explorer.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Explorador de Archivos Linux
Comment=Explorador de archivos completo para nuevos usuarios de Linux
Exec=/opt/linux-file-explorer/launch.sh
Icon=folder
Terminal=false
StartupNotify=true
Categories=System;FileTools;FileManager;
Keywords=explorador;archivos;gestor;linux;
EOF
    
    print_success "Entrada creada en el menú de aplicaciones"
}

# Función para instalar dependencias Python
install_python_dependencies() {
    print_status "Instalando dependencias de Python..."
    
    pip3 install --upgrade pip
    pip3 install pillow psutil
    
    print_success "Dependencias de Python instaladas"
}

# Función para crear desinstalador
create_uninstaller() {
    print_status "Creando desinstalador..."
    
    cat > /opt/linux-file-explorer/uninstall.sh << 'EOF'
#!/bin/bash

# Desinstalador del Explorador de Archivos Linux

echo "Desinstalando Explorador de Archivos Linux..."

# Eliminar archivos de aplicación
sudo rm -rf /opt/linux-file-explorer

# Eliminar entrada del menú
sudo rm -f /usr/share/applications/linux-file-explorer.desktop

# Eliminar acceso directo del escritorio (buscar en directorios comunes)
for user_dir in /home/*; do
    if [ -d "$user_dir" ]; then
        rm -f "$user_dir/Desktop/Explorador-Archivos-Linux.desktop"
        rm -f "$user_dir/Escritorio/Explorador-Archivos-Linux.desktop"
    fi
done

echo "Desinstalación completada"
EOF
    
    chmod +x /opt/linux-file-explorer/uninstall.sh
    
    print_success "Desinstalador creado en /opt/linux-file-explorer/uninstall.sh"
}

# Función principal de instalación
install_all() {
    print_status "Iniciando instalación completa..."
    
    detect_distro
    detect_package_manager
    check_connectivity
    update_repositories
    
    install_python
    install_multimedia
    install_file_tools
    install_network_tools
    install_system_tools
    install_python_dependencies
    install_file_explorer
    create_uninstaller
    
    print_success "¡Instalación completada exitosamente!"
    print_status "Puede ejecutar el explorador desde:"
    echo "  - Menú de aplicaciones: Explorador de Archivos Linux"
    echo "  - Terminal: /opt/linux-file-explorer/launch.sh"
    echo "  - Acceso directo en el escritorio"
    echo ""
    print_status "Para desinstalar, ejecute: sudo /opt/linux-file-explorer/uninstall.sh"
}

# Función para mostrar ayuda
show_help() {
    echo "Explorador de Archivos Linux - Instalador"
    echo ""
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo "  --uninstall    Desinstalar el explorador"
    echo "  --check        Verificar dependencias"
    echo ""
    echo "Sin opciones: Instalar todo automáticamente"
}

# Función para verificar dependencias
check_dependencies() {
    print_status "Verificando dependencias instaladas..."
    
    # Verificar Python
    if command -v python3 > /dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python encontrado: $PYTHON_VERSION"
    else
        print_error "Python3 no está instalado"
    fi
    
    # Verificar pip
    if command -v pip3 > /dev/null 2>&1; then
        print_success "pip3 encontrado"
    else
        print_error "pip3 no está instalado"
    fi
    
    # Verificar algunas herramientas multimedia
    TOOLS=("vlc" "eog" "evince" "gimp")
    for tool in "${TOOLS[@]}"; do
        if command -v $tool > /dev/null 2>&1; then
            print_success "$tool encontrado"
        else
            print_warning "$tool no está instalado"
        fi
    done
}

# Función para desinstalar
uninstall() {
    if [ -f /opt/linux-file-explorer/uninstall.sh ]; then
        bash /opt/linux-file-explorer/uninstall.sh
    else
        print_error "Desinstalador no encontrado"
        exit 1
    fi
}

# Procesar argumentos de línea de comandos
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --uninstall)
        check_root
        uninstall
        exit 0
        ;;
    --check)
        check_dependencies
        exit 0
        ;;
    "")
        check_root
        install_all
        ;;
    *)
        print_error "Opción desconocida: $1"
        show_help
        exit 1
        ;;
esac