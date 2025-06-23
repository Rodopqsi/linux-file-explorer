import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
import json
import shutil
import mimetypes
from datetime import datetime
import re

class DependencyManager:
    """Gestor de dependencias automático"""
    
    REQUIRED_PACKAGES = {
        'apt': [
            'python3-pil',          # Para imágenes
            'python3-pil.imagetk',  # Para mostrar imágenes en tkinter
            'vlc',                  # Para reproducir videos/audio
            'eog',                  # Visor de imágenes
            'evince',               # Para PDFs
            'gedit',                # Editor de texto
            'network-manager',      # Para WiFi
            'pulseaudio-utils',     # Para control de volumen
            'imagemagick',          # Para manipulación de imágenes
            'ffmpeg',               # Para multimedia
            'unzip',                # Para archivos comprimidos
            'p7zip-full',           # Para más formatos comprimidos
        ],
        'pacman': [
            'python-pillow',
            'vlc',
            'eog',
            'evince',
            'gedit',
            'networkmanager',
            'pulseaudio',
            'imagemagick',
            'ffmpeg',
            'unzip',
            'p7zip',
        ],
        'dnf': [
            'python3-pillow',
            'python3-pillow-tk',
            'vlc',
            'eog',
            'evince',
            'gedit',
            'NetworkManager',
            'pulseaudio-utils',
            'ImageMagick',
            'ffmpeg',
            'unzip',
            'p7zip',
        ]
    }
    
    @staticmethod
    def detect_package_manager():
        """Detecta el gestor de paquetes del sistema"""
        managers = {
            'apt': '/usr/bin/apt',
            'pacman': '/usr/bin/pacman',
            'dnf': '/usr/bin/dnf',
            'yum': '/usr/bin/yum'
        }
        
        for manager, path in managers.items():
            if os.path.exists(path):
                return manager
        return None
    
    @staticmethod
    def install_dependencies():
        """Instala todas las dependencias necesarias"""
        manager = DependencyManager.detect_package_manager()
        if not manager:
            messagebox.showerror("Error", "No se pudo detectar el gestor de paquetes")
            return False
        
        packages = DependencyManager.REQUIRED_PACKAGES.get(manager, [])
        if not packages:
            messagebox.showwarning("Advertencia", f"Gestor de paquetes {manager} no soportado")
            return False
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel()
        progress_window.title("Instalando Dependencias")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        
        label = tk.Label(progress_window, text="Instalando dependencias necesarias...")
        label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        text_widget = tk.Text(progress_window, height=4, width=50)
        text_widget.pack(pady=5, padx=20, fill='both', expand=True)
        
        def install_thread():
            try:
                # Actualizar repositorios
                if manager == 'apt':
                    subprocess.run(['sudo', 'apt', 'update'], check=True, 
                                    capture_output=True, text=True)
                    cmd = ['sudo', 'apt', 'install', '-y'] + packages
                elif manager == 'pacman':
                    subprocess.run(['sudo', 'pacman', '-Sy'], check=True,
                                    capture_output=True, text=True)
                    cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
                elif manager == 'dnf':
                    cmd = ['sudo', 'dnf', 'install', '-y'] + packages
                
                # Instalar paquetes
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, text=True)
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        text_widget.insert(tk.END, output)
                        text_widget.see(tk.END)
                        text_widget.update()
                
                if process.returncode == 0:
                    progress_bar.stop()
                    label.config(text="¡Instalación completada!")
                    messagebox.showinfo("Éxito", "Todas las dependencias se instalaron correctamente")
                else:
                    progress_bar.stop()
                    label.config(text="Error en la instalación")
                    messagebox.showerror("Error", "Hubo un problema instalando las dependencias")
                
            except Exception as e:
                progress_bar.stop()
                label.config(text="Error en la instalación")
                messagebox.showerror("Error", f"Error: {str(e)}")
            finally:
                progress_window.destroy()
        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
        return True

class WiFiManager:
    """Gestor de conexiones WiFi"""
    
    @staticmethod
    def scan_networks():
        """Escanea redes WiFi disponibles"""
        try:
            result = subprocess.run(['nmcli', 'dev', 'wifi', 'list'], 
                                    capture_output=True, text=True, check=True)
            networks = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    ssid = parts[1] if parts[1] != '--' else 'Red oculta'
                    signal = parts[5] if len(parts) > 5 else '0'
                    security = 'WPA' if '*' in line else 'Abierta'
                    networks.append({
                        'ssid': ssid,
                        'signal': signal,
                        'security': security
                    })
            
            return networks
        except subprocess.CalledProcessError:
            return []
    
    @staticmethod
    def connect_to_network(ssid, password=None):
        """Se conecta a una red WiFi"""
        try:
            if password:
                cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
            else:
                cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, "Conectado exitosamente"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e.stderr}"
    
    @staticmethod
    def disconnect():
        """Desconecta de la red WiFi actual"""
        try:
            subprocess.run(['nmcli', 'dev', 'disconnect', 'wlan0'], 
                            capture_output=True, text=True, check=True)
            return True, "Desconectado"
        except subprocess.CalledProcessError:
            return False, "Error al desconectar"
    
    @staticmethod
    def get_current_connection():
        """Obtiene información de la conexión actual"""
        try:
            result = subprocess.run(['nmcli', 'dev', 'status'], 
                                    capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 4 and 'wifi' in parts[1] and 'connected' in parts[2]:
                    return parts[3]
            return None
        except subprocess.CalledProcessError:
            return None

class VolumeManager:
    """Gestor de volumen del sistema"""
    
    @staticmethod
    def get_volume():
        """Obtiene el volumen actual"""
        try:
            result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], 
                                    capture_output=True, text=True, check=True)
            # Extraer porcentaje del resultado
            match = re.search(r'(\d+)%', result.stdout)
            if match:
                return int(match.group(1))
            return 50
        except subprocess.CalledProcessError:
            return 50
    
    @staticmethod
    def set_volume(volume):
        """Establece el volumen del sistema"""
        try:
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'], 
                            check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def toggle_mute():
        """Alterna el estado de silencio"""
        try:
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'], 
                            check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def is_muted():
        """Verifica si está silenciado"""
        try:
            result = subprocess.run(['pactl', 'get-sink-mute', '@DEFAULT_SINK@'], 
                                    capture_output=True, text=True, check=True)
            return 'yes' in result.stdout.lower()
        except subprocess.CalledProcessError:
            return False

class FileOpener:
    """Gestor para abrir diferentes tipos de archivos"""
    
    OPENERS = {
        'image': ['eog', 'feh', 'gpicview', 'ristretto'],
        'video': ['vlc', 'mpv', 'totem'],
        'audio': ['vlc', 'audacious', 'rhythmbox'],
        'pdf': ['evince', 'okular', 'mupdf'],
        'text': ['gedit', 'kate', 'mousepad', 'nano'],
        'archive': ['file-roller', 'ark', 'xarchiver']
    }
    
    @staticmethod
    def get_file_type(filepath):
        """Determina el tipo de archivo"""
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            return 'unknown'
        
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type.startswith('text/'):
            return 'text'
        elif mime_type in ['application/zip', 'application/x-rar', 'application/x-7z-compressed']:
            return 'archive'
        else:
            return 'unknown'
    
    @staticmethod
    def open_file(filepath):
        """Abre un archivo con la aplicación apropiada"""
        file_type = FileOpener.get_file_type(filepath)
        
        if file_type == 'unknown':
            # Usar xdg-open como fallback
            try:
                subprocess.Popen(['xdg-open', filepath])
                return True
            except:
                return False
        
        openers = FileOpener.OPENERS.get(file_type, [])
        
        for opener in openers:
            if shutil.which(opener):
                try:
                    subprocess.Popen([opener, filepath])
                    return True
                except:
                    continue
        
        # Fallback a xdg-open
        try:
            subprocess.Popen(['xdg-open', filepath])
            return True
        except:
            return False

class FileExplorer:
    """Explorador de archivos principal"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Archivos Linux")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.current_path = Path.home()
        self.history = [self.current_path]
        self.history_index = 0
        self.bookmarks = []
        self.clipboard = None
        self.clipboard_operation = None  # 'copy' or 'cut'
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_menubar()
        self.create_toolbar()
        self.create_main_frame()
        self.create_status_bar()
        
        # Cargar configuración
        self.load_config()
        
        # Actualizar vista inicial
        self.refresh_view()
        
        # Configurar eventos
        self.setup_events()
    
    def setup_style(self):
        """Configura el estilo de la aplicación"""
        style = ttk.Style()
        
        # Configurar temas
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Personalizar colores
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def create_menubar(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nueva Carpeta", command=self.create_folder, accelerator="Ctrl+N")
        file_menu.add_command(label="Nuevo Archivo", command=self.create_file)
        file_menu.add_separator()
        file_menu.add_command(label="Copiar", command=self.copy_file, accelerator="Ctrl+C")
        file_menu.add_command(label="Cortar", command=self.cut_file, accelerator="Ctrl+X")
        file_menu.add_command(label="Pegar", command=self.paste_file, accelerator="Ctrl+V")
        file_menu.add_separator()
        file_menu.add_command(label="Eliminar", command=self.delete_file, accelerator="Del")
        file_menu.add_command(label="Renombrar", command=self.rename_file, accelerator="F2")
        file_menu.add_separator()
        file_menu.add_command(label="Propiedades", command=self.show_properties)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Actualizar", command=self.refresh_view, accelerator="F5")
        view_menu.add_command(label="Mostrar Archivos Ocultos", command=self.toggle_hidden_files)
        view_menu.add_separator()
        view_menu.add_command(label="Ir a Carpeta Personal", command=self.go_home)
        view_menu.add_command(label="Ir a Escritorio", command=self.go_desktop)
        view_menu.add_command(label="Ir a Documentos", command=self.go_documents)
        view_menu.add_command(label="Ir a Descargas", command=self.go_downloads)
        
        # Menú Marcadores
        bookmarks_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Marcadores", menu=bookmarks_menu)
        bookmarks_menu.add_command(label="Agregar Marcador", command=self.add_bookmark)
        bookmarks_menu.add_command(label="Gestionar Marcadores", command=self.manage_bookmarks)
        
        # Menú Sistema
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=system_menu)
        system_menu.add_command(label="Gestión WiFi", command=self.open_wifi_manager)
        system_menu.add_command(label="Control de Volumen", command=self.open_volume_control)
        system_menu.add_separator()
        system_menu.add_command(label="Terminal", command=self.open_terminal)
        system_menu.add_command(label="Monitor del Sistema", command=self.open_system_monitor)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Instalar Dependencias", command=self.install_dependencies)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill='x', padx=5, pady=2)
        
        # Botones de navegación
        ttk.Button(toolbar_frame, text="←", command=self.go_back, width=3).pack(side='left', padx=1)
        ttk.Button(toolbar_frame, text="→", command=self.go_forward, width=3).pack(side='left', padx=1)
        ttk.Button(toolbar_frame, text="↑", command=self.go_up, width=3).pack(side='left', padx=1)
        ttk.Button(toolbar_frame, text="🏠", command=self.go_home, width=3).pack(side='left', padx=1)
        ttk.Button(toolbar_frame, text="🔄", command=self.refresh_view, width=3).pack(side='left', padx=1)
        
        # Separador
        ttk.Separator(toolbar_frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Barra de dirección
        ttk.Label(toolbar_frame, text="Ruta:").pack(side='left', padx=2)
        self.address_bar = ttk.Entry(toolbar_frame)
        self.address_bar.pack(side='left', fill='x', expand=True, padx=2)
        self.address_bar.bind('<Return>', self.navigate_to_address)
        
        # Botón ir
        ttk.Button(toolbar_frame, text="Ir", command=self.navigate_to_address).pack(side='left', padx=2)
        
        # Separador
        ttk.Separator(toolbar_frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Buscador
        ttk.Label(toolbar_frame, text="Buscar:").pack(side='left', padx=2)
        self.search_entry = ttk.Entry(toolbar_frame, width=20)
        self.search_entry.pack(side='left', padx=2)
        self.search_entry.bind('<Return>', self.search_files)
        ttk.Button(toolbar_frame, text="🔍", command=self.search_files, width=3).pack(side='left', padx=1)
    
    def create_main_frame(self):
        """Crea el marco principal con panel lateral y vista de archivos"""
        # Frame principal con panel
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=2)
        
        # Panel lateral
        self.create_sidebar(main_paned)
        
        # Vista de archivos
        self.create_file_view(main_paned)
    
    def create_sidebar(self, parent):
        """Crea el panel lateral con accesos rápidos"""
        sidebar_frame = ttk.Frame(parent)
        parent.add(sidebar_frame, weight=1)
        
        # Título
        ttk.Label(sidebar_frame, text="Accesos Rápidos", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Lista de accesos rápidos
        self.sidebar_tree = ttk.Treeview(sidebar_frame, show='tree', selectmode='browse')
        self.sidebar_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Poblar sidebar
        self.populate_sidebar()
        
        # Eventos
        self.sidebar_tree.bind('<Double-1>', self.on_sidebar_double_click)
    
    def populate_sidebar(self):
        """Puebla el panel lateral con accesos rápidos"""
        # Limpiar
        for item in self.sidebar_tree.get_children():
            self.sidebar_tree.delete(item)
        
        # Lugares comunes
        places = [
            ("🏠 Inicio", str(Path.home())),
            ("🖥️ Escritorio", str(Path.home() / "Desktop")),
            ("📁 Documentos", str(Path.home() / "Documents")),
            ("⬇️ Descargas", str(Path.home() / "Downloads")),
            ("🎵 Música", str(Path.home() / "Music")),
            ("🖼️ Imágenes", str(Path.home() / "Pictures")),
            ("🎬 Videos", str(Path.home() / "Videos")),
            ("💾 Raíz", "/"),
            ("🖴 Media", "/media"),
            ("🔧 Temp", "/tmp"),
        ]
        
        for name, path in places:
            if os.path.exists(path):
                self.sidebar_tree.insert('', 'end', text=name, values=(path,))
        
        # Separador
        self.sidebar_tree.insert('', 'end', text="─" * 20, values=("",))
        
        # Marcadores
        for bookmark in self.bookmarks:
            name = f"⭐ {os.path.basename(bookmark)}"
            self.sidebar_tree.insert('', 'end', text=name, values=(bookmark,))
    
    def create_file_view(self, parent):
        """Crea la vista principal de archivos"""
        file_frame = ttk.Frame(parent)
        parent.add(file_frame, weight=3)
        
        # Treeview para archivos
        columns = ('Nombre', 'Tamaño', 'Tipo', 'Modificado')
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show='tree headings')
        
        # Configurar columnas
        self.file_tree.heading('#0', text='', anchor='w')
        self.file_tree.column('#0', width=30, minwidth=30)
        
        for col in columns:
            self.file_tree.heading(col, text=col, anchor='w')
            if col == 'Nombre':
                self.file_tree.column(col, width=300, minwidth=200)
            elif col == 'Tamaño':
                self.file_tree.column(col, width=100, minwidth=80)
            elif col == 'Tipo':
                self.file_tree.column(col, width=150, minwidth=100)
            else:
                self.file_tree.column(col, width=150, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(file_frame, orient='vertical', command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(file_frame, orient='horizontal', command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.file_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Eventos
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        self.file_tree.bind('<Button-3>', self.show_context_menu)
        
        # Menú contextual
        self.create_context_menu()
    
    def create_context_menu(self):
        """Crea el menú contextual"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Abrir", command=self.open_selected_file)
        self.context_menu.add_command(label="Abrir con...", command=self.open_with)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cortar", command=self.cut_file)
        self.context_menu.add_command(label="Copiar", command=self.copy_file)
        self.context_menu.add_command(label="Pegar", command=self.paste_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Eliminar", command=self.delete_file)
        self.context_menu.add_command(label="Renombrar", command=self.rename_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Propiedades", command=self.show_properties)
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill='x', side='bottom')
        
        # Información de archivos
        self.status_label = ttk.Label(self.status_bar, text="Listo")
        self.status_label.pack(side='left', padx=5)
        
        # Separador
        ttk.Separator(self.status_bar, orient='vertical').pack(side='right', fill='y', padx=5)
        
        # Control de volumen
        volume_frame = ttk.Frame(self.status_bar)
        volume_frame.pack(side='right', padx=5)
        
        ttk.Label(volume_frame, text="🔊").pack(side='left')
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, orient='horizontal', 
                                        length=100, command=self.on_volume_change)
        self.volume_scale.pack(side='left', padx=2)
        self.volume_scale.set(VolumeManager.get_volume())
        
        # WiFi status
        self.wifi_label = ttk.Label(self.status_bar, text="📶 WiFi")
        self.wifi_label.pack(side='right', padx=5)
        self.wifi_label.bind('<Button-1>', lambda e: self.open_wifi_manager())
        
        # Actualizar estado WiFi
        self.update_wifi_status()
    
    def setup_events(self):
        """Configura los eventos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.create_folder())
        self.root.bind('<Control-c>', lambda e: self.copy_file())
        self.root.bind('<Control-x>', lambda e: self.cut_file())
        self.root.bind('<Control-v>', lambda e: self.paste_file())
        self.root.bind('<Delete>', lambda e: self.delete_file())
        self.root.bind('<F2>', lambda e: self.rename_file())
        self.root.bind('<F5>', lambda e: self.refresh_view())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Alt-Left>', lambda e: self.go_back())
        self.root.bind('<Alt-Right>', lambda e: self.go_forward())
        self.root.bind('<Alt-Up>', lambda e: self.go_up())
    
    def refresh_view(self):
        """Actualiza la vista de archivos"""
        # Limpiar vista
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Actualizar barra de dirección
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, str(self.current_path))
        
        try:
            # Obtener archivos y carpetas
            items = []
            
            # Primero las carpetas
            for item in self.current_path.iterdir():
                if item.name.startswith('.') and not getattr(self, 'show_hidden', False):
                    continue
                
                try:
                    stat = item.stat()
                    size = self.format_size(stat.st_size) if item.is_file() else ""
                    file_type = "Carpeta" if item.is_dir() else self.get_file_type(item)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'is_dir': item.is_dir(),
                        'size': size,
                        'type': file_type,
                        'modified': modified,
                        'icon': '📁' if item.is_dir() else self.get_file_icon(item)
                    })
                except (PermissionError, OSError):
                    continue
            
            # Ordenar: carpetas primero, luego por nombre
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            # Insertar en el treeview
            for item in items:
                self.file_tree.insert('', 'end', 
                                    text=item['icon'],
                                    values=(item['name'], item['size'], item['type'], item['modified']),
                                    tags=('directory' if item['is_dir'] else 'file',))
            
            # Actualizar contador de archivos
            total_items = len(items)
            dirs = sum(1 for item in items if item['is_dir'])
            files = total_items - dirs
            self.status_label.config(text=f"{total_items} elementos ({dirs} carpetas, {files} archivos)")
            
        except PermissionError:
            messagebox.showerror("Error", "No tiene permisos para acceder a esta carpeta")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la carpeta: {str(e)}")
    
    def get_file_icon(self, filepath):
        """Obtiene el icono apropiado para un archivo"""
        file_type = FileOpener.get_file_type(str(filepath))
        icons = {
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'pdf': '📄',
            'text': '📝',
            'archive': '📦',
            'unknown': '📄'
        }
        return icons.get(file_type, '📄')
    
    def get_file_type(self, filepath):
        """Obtiene una descripción del tipo de archivo"""
        if filepath.is_dir():
            return "Carpeta"
        
        suffix = filepath.suffix.lower()
        types = {
            '.txt': 'Archivo de texto',
            '.pdf': 'Documento PDF',
            '.doc': 'Documento Word',
            '.docx': 'Documento Word',
            '.jpg': 'Imagen JPEG',
            '.jpeg': 'Imagen JPEG',
            '.png': 'Imagen PNG',
            '.gif': 'Imagen GIF',
            '.mp4': 'Video MP4',
            '.avi': 'Video AVI',
            '.mp3': 'Audio MP3',
            '.wav': 'Audio WAV',
            '.zip': 'Archivo ZIP',
            '.tar': 'Archivo TAR',
            '.gz': 'Archivo comprimido',
            '.py': 'Archivo Python',
            '.js': 'Archivo JavaScript',
            '.html': 'Página web',
            '.css': 'Hoja de estilo',
        }
        return types.get(suffix, f'Archivo {suffix[1:].upper()}' if suffix else 'Archivo')
    
    def format_size(self, size):
        """Formatea el tamaño de archivo en formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    # Métodos de navegación
    def go_back(self):
        """Va hacia atrás en el historial"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = Path(self.history[self.history_index])
            self.refresh_view()
    
    def go_forward(self):
        """Va hacia adelante en el historial"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = Path(self.history[self.history_index])
            self.refresh_view()
    
    def go_up(self):
        """Sube un nivel en la jerarquía de carpetas"""
        if self.current_path.parent != self.current_path:
            self.navigate_to_path(self.current_path.parent)
    
    def go_home(self):
        """Va a la carpeta personal"""
        self.navigate_to_path(Path.home())
    
    def go_desktop(self):
        """Va al escritorio"""
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            self.navigate_to_path(desktop)
    
    def go_documents(self):
        """Va a documentos"""
        documents = Path.home() / "Documents"
        if documents.exists():
            self.navigate_to_path(documents)
    
    def go_downloads(self):
        """Va a descargas"""
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            self.navigate_to_path(downloads)
    
    def navigate_to_path(self, path):
        """Navega a una ruta específica"""
        path = Path(path)
        if path.exists() and path.is_dir():
            self.current_path = path
            
            # Actualizar historial
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            
            if not self.history or self.history[-1] != path:
                self.history.append(path)
                self.history_index = len(self.history) - 1
            
            self.refresh_view()
            return True
        return False
    
    def navigate_to_address(self, event=None):
        """Navega a la dirección ingresada en la barra"""
        address = self.address_bar.get().strip()
        if address:
            success = self.navigate_to_path(address)
            if not success:
                messagebox.showerror("Error", f"No se puede acceder a: {address}")
                self.address_bar.delete(0, tk.END)
                self.address_bar.insert(0, str(self.current_path))
    
    # Eventos de archivos
    def on_file_double_click(self, event):
        """Maneja doble clic en archivos"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            filename = item['values'][0]
            filepath = self.current_path / filename
            
            if filepath.is_dir():
                self.navigate_to_path(filepath)
            else:
                self.open_file(filepath)
    
    def on_sidebar_double_click(self, event):
        """Maneja doble clic en el panel lateral"""
        selection = self.sidebar_tree.selection()
        if selection:
            item = self.sidebar_tree.item(selection[0])
            path = item['values'][0] if item['values'] else None
            if path and path != "":
                self.navigate_to_path(path)
    
    def show_context_menu(self, event):
        """Muestra el menú contextual"""
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_selected_files(self):
        """Obtiene los archivos seleccionados"""
        selection = self.file_tree.selection()
        files = []
        for item in selection:
            filename = self.file_tree.item(item)['values'][0]
            filepath = self.current_path / filename
            files.append(filepath)
        return files
    
    # Operaciones de archivos
    def open_selected_file(self):
        """Abre el archivo seleccionado"""
        files = self.get_selected_files()
        if files:
            self.open_file(files[0])
    
    def open_file(self, filepath):
        """Abre un archivo con la aplicación apropiada"""
        if not FileOpener.open_file(str(filepath)):
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {filepath.name}")
    
    def open_with(self):
        """Abre archivo con aplicación específica"""
        files = self.get_selected_files()
        if not files:
            return
        
        app = simpledialog.askstring("Abrir con", "Ingrese el comando de la aplicación:")
        if app:
            try:
                subprocess.Popen([app, str(files[0])])
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir con {app}: {str(e)}")
    
    def create_folder(self):
        """Crea una nueva carpeta"""
        name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if name:
            new_folder = self.current_path / name
            try:
                new_folder.mkdir(exist_ok=False)
                self.refresh_view()
            except FileExistsError:
                messagebox.showerror("Error", "Ya existe una carpeta con ese nombre")
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear carpeta: {str(e)}")
    
    def create_file(self):
        """Crea un nuevo archivo"""
        name = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo:")
        if name:
            new_file = self.current_path / name
            try:
                new_file.touch(exist_ok=False)
                self.refresh_view()
            except FileExistsError:
                messagebox.showerror("Error", "Ya existe un archivo con ese nombre")
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear archivo: {str(e)}")
    
    def copy_file(self):
        """Copia archivos seleccionados"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = 'copy'
            self.status_label.config(text=f"Copiados {len(files)} elementos")
    
    def cut_file(self):
        """Corta archivos seleccionados"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = 'cut'
            self.status_label.config(text=f"Cortados {len(files)} elementos")
    
    def paste_file(self):
        """Pega archivos del portapapeles"""
        if not self.clipboard:
            return
        
        try:
            for file_path in self.clipboard:
                dest_path = self.current_path / file_path.name
                
                # Evitar sobrescribir
                counter = 1
                while dest_path.exists():
                    name_parts = file_path.stem, counter, file_path.suffix
                    if file_path.is_dir():
                        dest_path = self.current_path / f"{name_parts[0]} ({name_parts[1]})"
                    else:
                        dest_path = self.current_path / f"{name_parts[0]} ({name_parts[1]}){name_parts[2]}"
                    counter += 1
                
                if self.clipboard_operation == 'copy':
                    if file_path.is_dir():
                        shutil.copytree(file_path, dest_path)
                    else:
                        shutil.copy2(file_path, dest_path)
                elif self.clipboard_operation == 'cut':
                    shutil.move(str(file_path), str(dest_path))
            
            if self.clipboard_operation == 'cut':
                self.clipboard = None
                self.clipboard_operation = None
            
            self.refresh_view()
            self.status_label.config(text="Operación completada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la operación: {str(e)}")
    
    def delete_file(self):
        """Elimina archivos seleccionados"""
        files = self.get_selected_files()
        if not files:
            return
        
        file_list = "\n".join([f.name for f in files])
        if messagebox.askyesno("Confirmar eliminación", 
                                f"¿Está seguro de eliminar estos elementos?\n\n{file_list}"):
            try:
                for file_path in files:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                
                self.refresh_view()
                self.status_label.config(text=f"Eliminados {len(files)} elementos")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def rename_file(self):
        """Renombra el archivo seleccionado"""
        files = self.get_selected_files()
        if not files:
            return
        
        old_name = files[0].name
        new_name = simpledialog.askstring("Renombrar", f"Nuevo nombre para '{old_name}':", 
                                            initialvalue=old_name)
        if new_name and new_name != old_name:
            try:
                new_path = files[0].parent / new_name
                files[0].rename(new_path)
                self.refresh_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al renombrar: {str(e)}")
    
    def show_properties(self):
        """Muestra propiedades del archivo seleccionado"""
        files = self.get_selected_files()
        if not files:
            return
        
        file_path = files[0]
        try:
            stat = file_path.stat()
            
            # Crear ventana de propiedades
            props_window = tk.Toplevel(self.root)
            props_window.title(f"Propiedades - {file_path.name}")
            props_window.geometry("400x300")
            props_window.resizable(False, False)
            
            # Información
            info_frame = ttk.LabelFrame(props_window, text="Información General")
            info_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(info_frame, text=f"Nombre: {file_path.name}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(info_frame, text=f"Tipo: {self.get_file_type(file_path)}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(info_frame, text=f"Ubicación: {file_path.parent}").pack(anchor='w', padx=5, pady=2)
            
            if file_path.is_file():
                ttk.Label(info_frame, text=f"Tamaño: {self.format_size(stat.st_size)}").pack(anchor='w', padx=5, pady=2)
            
            # Fechas
            dates_frame = ttk.LabelFrame(props_window, text="Fechas")
            dates_frame.pack(fill='x', padx=10, pady=5)
            
            created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            accessed = datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            
            ttk.Label(dates_frame, text=f"Creado: {created}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(dates_frame, text=f"Modificado: {modified}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(dates_frame, text=f"Accedido: {accessed}").pack(anchor='w', padx=5, pady=2)
            
            # Permisos
            perms_frame = ttk.LabelFrame(props_window, text="Permisos")
            perms_frame.pack(fill='x', padx=10, pady=5)
            
            mode = stat.st_mode
            permissions = []
            if mode & 0o400: permissions.append("Lectura (propietario)")
            if mode & 0o200: permissions.append("Escritura (propietario)")
            if mode & 0o100: permissions.append("Ejecución (propietario)")
            if mode & 0o040: permissions.append("Lectura (grupo)")
            if mode & 0o020: permissions.append("Escritura (grupo)")
            if mode & 0o010: permissions.append("Ejecución (grupo)")
            if mode & 0o004: permissions.append("Lectura (otros)")
            if mode & 0o002: permissions.append("Escritura (otros)")
            if mode & 0o001: permissions.append("Ejecución (otros)")
            
            for perm in permissions:
                ttk.Label(perms_frame, text=f"• {perm}").pack(anchor='w', padx=5, pady=1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener propiedades: {str(e)}")
    
    # Búsqueda
    def search_files(self, event=None):
        """Busca archivos en la carpeta actual"""
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_view()  # Restaurar vista normal
            return
        
        # Limpiar vista
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            matches = []
            for item in self.current_path.rglob(f"*{query}*"):
                if item.name.startswith('.') and not getattr(self, 'show_hidden', False):
                    continue
                
                try:
                    stat = item.stat()
                    size = self.format_size(stat.st_size) if item.is_file() else ""
                    file_type = "Carpeta" if item.is_dir() else self.get_file_type(item)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    matches.append({
                        'name': str(item.relative_to(self.current_path)),
                        'path': str(item),
                        'is_dir': item.is_dir(),
                        'size': size,
                        'type': file_type,
                        'modified': modified,
                        'icon': '📁' if item.is_dir() else self.get_file_icon(item)
                    })
                except (PermissionError, OSError):
                    continue
            
            # Mostrar resultados
            for match in matches:
                self.file_tree.insert('', 'end',
                                    text=match['icon'],
                                    values=(match['name'], match['size'], match['type'], match['modified']),
                                    tags=('directory' if match['is_dir'] else 'file',))
            
            self.status_label.config(text=f"Encontrados {len(matches)} elementos para '{query}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
        # Insertar resultados
            matches.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            for match in matches:
                self.file_tree.insert('', 'end',
                                    text=match['icon'],
                                    values=(match['name'], match['size'], match['type'], match['modified']),
                                    tags=('directory' if match['is_dir'] else 'file',))
            
            self.status_label.config(text=f"Encontrados {len(matches)} elementos para '{query}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    # Marcadores
    def add_bookmark(self):
        """Añade la carpeta actual a marcadores"""
        if str(self.current_path) not in self.bookmarks:
            self.bookmarks.append(str(self.current_path))
            self.save_config()
            self.populate_sidebar()
            messagebox.showinfo("Marcador", f"Marcador añadido: {self.current_path.name}")
        else:
            messagebox.showinfo("Marcador", "Esta carpeta ya está en marcadores")
    
    def manage_bookmarks(self):
        """Abre ventana para gestionar marcadores"""
        if not self.bookmarks:
            messagebox.showinfo("Marcadores", "No hay marcadores guardados")
            return
        
        # Crear ventana
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Gestionar Marcadores")
        bookmarks_window.geometry("500x300")
        bookmarks_window.resizable(True, True)
        
        # Lista de marcadores
        frame = ttk.Frame(bookmarks_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Marcadores guardados:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        listbox = tk.Listbox(frame, selectmode='single')
        listbox.pack(fill='both', expand=True, pady=(0, 10))
        
        # Poblar lista
        for bookmark in self.bookmarks:
            display_name = f"{os.path.basename(bookmark)} ({bookmark})"
            listbox.insert(tk.END, display_name)
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x')
        
        def go_to_bookmark():
            selection = listbox.curselection()
            if selection:
                bookmark_path = self.bookmarks[selection[0]]
                if os.path.exists(bookmark_path):
                    self.navigate_to_path(bookmark_path)
                    bookmarks_window.destroy()
                else:
                    messagebox.showerror("Error", "El marcador ya no existe")
        
        def remove_bookmark():
            selection = listbox.curselection()
            if selection:
                removed_bookmark = self.bookmarks.pop(selection[0])
                listbox.delete(selection[0])
                self.save_config()
                self.populate_sidebar()
                messagebox.showinfo("Marcador", f"Marcador eliminado: {os.path.basename(removed_bookmark)}")
        
        ttk.Button(button_frame, text="Ir a", command=go_to_bookmark).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Eliminar", command=remove_bookmark).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cerrar", command=bookmarks_window.destroy).pack(side='right')
    
    # Gestión WiFi
    def open_wifi_manager(self):
        """Abre el gestor de WiFi"""
        wifi_window = tk.Toplevel(self.root)
        wifi_window.title("Gestión WiFi")
        wifi_window.geometry("600x400")
        wifi_window.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(wifi_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Estado actual
        status_frame = ttk.LabelFrame(main_frame, text="Estado Actual")
        status_frame.pack(fill='x', pady=(0, 10))
        
        current_conn = WiFiManager.get_current_connection()
        status_text = f"Conectado a: {current_conn}" if current_conn else "Desconectado"
        self.wifi_status_label = ttk.Label(status_frame, text=status_text, font=('Arial', 11))
        self.wifi_status_label.pack(pady=10)
        
        # Botones de control
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(pady=5)
        
        ttk.Button(control_frame, text="Escanear Redes", 
                    command=lambda: self.scan_wifi_networks(networks_tree)).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Desconectar", 
                    command=lambda: self.disconnect_wifi(wifi_window)).pack(side='left', padx=5)
        
        # Lista de redes
        networks_frame = ttk.LabelFrame(main_frame, text="Redes Disponibles")
        networks_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview para redes
        columns = ('SSID', 'Señal', 'Seguridad')
        networks_tree = ttk.Treeview(networks_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        for col in columns:
            networks_tree.heading(col, text=col)
            if col == 'SSID':
                networks_tree.column(col, width=250, minwidth=200)
            elif col == 'Señal':
                networks_tree.column(col, width=100, minwidth=80)
            else:
                networks_tree.column(col, width=120, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(networks_frame, orient='vertical', command=networks_tree.yview)
        networks_tree.configure(yscrollcommand=scrollbar.set)
        
        networks_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Evento doble clic
        networks_tree.bind('<Double-1>', lambda e: self.connect_to_wifi(networks_tree, wifi_window))
        
        # Botones inferiores
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Conectar", 
                    command=lambda: self.connect_to_wifi(networks_tree, wifi_window)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Actualizar", 
                    command=lambda: self.scan_wifi_networks(networks_tree)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cerrar", command=wifi_window.destroy).pack(side='right')
        
        # Escanear redes al abrir
        self.scan_wifi_networks(networks_tree)
    
    def scan_wifi_networks(self, tree_widget):
        """Escanea y muestra redes WiFi"""
        # Limpiar lista
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        
        def scan_thread():
            networks = WiFiManager.scan_networks()
            
            # Actualizar en el hilo principal
            def update_ui():
                for network in networks:
                    signal_bars = "📶" * min(4, int(network['signal']) // 25 + 1)
                    tree_widget.insert('', 'end', values=(
                        network['ssid'],
                        f"{signal_bars} {network['signal']}%",
                        network['security']
                    ))
                
                if not networks:
                    tree_widget.insert('', 'end', values=("No se encontraron redes", "", ""))
            
            tree_widget.after(0, update_ui)
        
        thread = threading.Thread(target=scan_thread)
        thread.daemon = True
        thread.start()
    
    def connect_to_wifi(self, tree_widget, parent_window):
        """Conecta a la red WiFi seleccionada"""
        selection = tree_widget.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una red para conectar")
            return
        
        item = tree_widget.item(selection[0])
        ssid = item['values'][0]
        security = item['values'][2]
        
        if ssid == "No se encontraron redes":
            return
        
        password = None
        if 'WPA' in security or 'WEP' in security:
            password = simpledialog.askstring("Contraseña WiFi", 
                                                f"Ingrese la contraseña para '{ssid}':", 
                                                show='*', parent=parent_window)
            if password is None:  # Usuario canceló
                return
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel(parent_window)
        progress_window.title("Conectando...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.transient(parent_window)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Conectando a {ssid}...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        def connect_thread():
            success, message = WiFiManager.connect_to_network(ssid, password)
            
            def update_result():
                progress_bar.stop()
                progress_window.destroy()
                
                if success:
                    messagebox.showinfo("Éxito", f"Conectado exitosamente a {ssid}")
                    self.update_wifi_status()
                    parent_window.destroy()
                else:
                    messagebox.showerror("Error", f"No se pudo conectar: {message}")
            
            progress_window.after(0, update_result)
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
    
    def disconnect_wifi(self, parent_window):
        """Desconecta del WiFi actual"""
        if messagebox.askyesno("Confirmar", "¿Desea desconectarse de la red WiFi?", parent=parent_window):
            success, message = WiFiManager.disconnect()
            if success:
                messagebox.showinfo("Éxito", "Desconectado exitosamente")
                self.update_wifi_status()
                parent_window.destroy()
            else:
                messagebox.showerror("Error", f"Error al desconectar: {message}")
    
    def update_wifi_status(self):
        """Actualiza el estado del WiFi en la barra de estado"""
        current_conn = WiFiManager.get_current_connection()
        if current_conn:
            self.wifi_label.config(text=f"📶 {current_conn}")
        else:
            self.wifi_label.config(text="📶 Sin conexión")
    
    # Control de volumen
    def open_volume_control(self):
        """Abre el control de volumen avanzado"""
        volume_window = tk.Toplevel(self.root)
        volume_window.title("Control de Volumen")
        volume_window.geometry("400x200")
        volume_window.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(volume_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Control de Volumen del Sistema", 
                    font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Control de volumen
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(fill='x', pady=10)
        
        ttk.Label(volume_frame, text="🔊 Volumen:", font=('Arial', 12)).pack(anchor='w')
        
        self.volume_var = tk.IntVar(value=VolumeManager.get_volume())
        volume_scale = ttk.Scale(volume_frame, from_=0, to=100, orient='horizontal',
                                variable=self.volume_var, length=300,
                                command=self.on_volume_control_change)
        volume_scale.pack(fill='x', pady=5)
        
        # Etiqueta de porcentaje
        self.volume_percent_label = ttk.Label(volume_frame, text=f"{self.volume_var.get()}%", 
                                            font=('Arial', 11))
        self.volume_percent_label.pack()
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        mute_text = "🔇 Dessilenciar" if VolumeManager.is_muted() else "🔇 Silenciar"
        self.mute_button = ttk.Button(button_frame, text=mute_text, command=self.toggle_mute_advanced)
        self.mute_button.pack(side='left')
        
        ttk.Button(button_frame, text="Cerrar", command=volume_window.destroy).pack(side='right')
    
    def on_volume_control_change(self, value):
        """Maneja cambios en el control de volumen avanzado"""
        volume = int(float(value))
        VolumeManager.set_volume(volume)
        self.volume_percent_label.config(text=f"{volume}%")
        self.volume_scale.set(volume)  # Actualizar control en barra de estado
    
    def toggle_mute_advanced(self):
        """Alterna silencio en control avanzado"""
        VolumeManager.toggle_mute()
        is_muted = VolumeManager.is_muted()
        mute_text = "🔇 Dessilenciar" if is_muted else "🔇 Silenciar"
        self.mute_button.config(text=mute_text)
    
    def on_volume_change(self, value):
        """Maneja cambios en el control de volumen de la barra de estado"""
        volume = int(float(value))
        VolumeManager.set_volume(volume)
    
    # Herramientas del sistema
    def open_terminal(self):
        """Abre terminal en la carpeta actual"""
        terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'lxterminal', 'xterm']
        
        for terminal in terminals:
            if shutil.which(terminal):
                try:
                    if terminal in ['gnome-terminal', 'xfce4-terminal']:
                        subprocess.Popen([terminal, '--working-directory', str(self.current_path)])
                    elif terminal == 'konsole':
                        subprocess.Popen([terminal, '--workdir', str(self.current_path)])
                    else:
                        subprocess.Popen([terminal], cwd=str(self.current_path))
                    return
                except:
                    continue
        
        messagebox.showerror("Error", "No se pudo abrir terminal")
    
    def open_system_monitor(self):
        """Abre monitor del sistema"""
        monitors = ['gnome-system-monitor', 'ksysguard', 'xfce4-taskmanager', 'htop']
        
        for monitor in monitors:
            if shutil.which(monitor):
                try:
                    if monitor == 'htop':
                        # Abrir htop en terminal
                        terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']
                        for terminal in terminals:
                            if shutil.which(terminal):
                                if terminal == 'gnome-terminal':
                                    subprocess.Popen([terminal, '--', 'htop'])
                                elif terminal == 'konsole':
                                    subprocess.Popen([terminal, '-e', 'htop'])
                                else:
                                    subprocess.Popen([terminal, '-e', 'htop'])
                                return
                    else:
                        subprocess.Popen([monitor])
                        return
                except:
                    continue
        
        messagebox.showerror("Error", "No se pudo abrir monitor del sistema")
    
    # Configuración
    def toggle_hidden_files(self):
        """Alterna mostrar archivos ocultos"""
        self.show_hidden = not getattr(self, 'show_hidden', False)
        self.refresh_view()
        status = "mostrados" if self.show_hidden else "ocultos"
        self.status_label.config(text=f"Archivos ocultos {status}")
    
    def load_config(self):
        """Carga configuración desde archivo"""
        config_file = Path.home() / '.file_explorer_config.json'
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.bookmarks = config.get('bookmarks', [])
                    self.show_hidden = config.get('show_hidden', False)
        except:
            self.bookmarks = []
            self.show_hidden = False
    
    def save_config(self):
        """Guarda configuración a archivo"""
        config_file = Path.home() / '.file_explorer_config.json'
        try:
            config = {
                'bookmarks': self.bookmarks,
                'show_hidden': getattr(self, 'show_hidden', False)
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    # Instalación de dependencias
    def install_dependencies(self):
        """Instala dependencias necesarias"""
        if messagebox.askyesno("Instalar Dependencias", 
                                "¿Desea instalar todas las dependencias necesarias?\n" +
                                "Esto incluye visores de imágenes, reproductores de video, " +
                                "editores de texto y herramientas del sistema.\n\n" +
                                "Se requieren permisos de administrador."):
            DependencyManager.install_dependencies()
    
    # Acerca de
    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = """
            Explorador de Archivos Linux v1.0

            Diseñado especialmente para usuarios nuevos de Linux.

            Características:
            • Exploración completa de archivos y carpetas
            • Gestión de WiFi integrada
            • Control de volumen del sistema
            • Instalación automática de dependencias
            • Soporte para múltiples formatos de archivo
            • Marcadores y accesos rápidos
            • Búsqueda de archivos
            • Terminal integrado

            Desarrollado con Python y Tkinter
            Autor: Asistente Claude

            © 2024 - Software Libre
        """
        
        messagebox.showinfo("Acerca de", about_text.strip())

def main():
    """Función principal"""
    # Verificar que estamos en Linux
    if sys.platform not in ['linux', 'linux2']:
        print("Error: Esta aplicación está diseñada solo para sistemas Linux")
        sys.exit(1)
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Configurar tema oscuro si está disponible
    try:
        root.tk.call('source', '/usr/share/themes/Adwaita-dark/gtk-3.0/gtk.css')
    except:
        pass
    
    # Crear aplicación
    app = FileExplorer(root)
    
    # Configurar cierre
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()