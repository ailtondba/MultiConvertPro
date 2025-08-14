#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Janela Principal

Este módulo contém a classe MainWindow que implementa a interface
principal da aplicação MultiConvert Pro.

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QListWidget, QComboBox, QProgressBar, QLabel,
    QFrame, QSplitter, QGroupBox, QStatusBar, QMenuBar, QToolBar
)
from PySide6.QtCore import Qt, QSize, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent
import traceback

# Importar o motor de conversão
from core.converters.main_converter import MainConverter


class DragDropWidget(QFrame):
    """Widget personalizado para área de arrastar e soltar."""
    
    # Signal para comunicar arquivos soltos
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget de drag & drop."""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        
        # Layout
        layout = QVBoxLayout()
        
        # Label principal
        self.main_label = QLabel("📎 Arraste seus arquivos aqui")
        self.main_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.main_label.setFont(font)
        
        # Label secundário
        self.sub_label = QLabel("✨ ou clique em 'Adicionar Arquivos' para começar")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("color: #6c8cd5; font-size: 12px; font-style: italic;")
        
        layout.addWidget(self.main_label)
        layout.addWidget(self.sub_label)
        
        self.setLayout(layout)
        
        # Estilo
        self.setStyleSheet("""
            DragDropWidget {
                border: 2px dashed #4a90e2;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fbff, stop:1 #e8f4fd);
                color: #2c5aa0;
            }
            DragDropWidget:hover {
                border-color: #0078d4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f4fd, stop:1 #d0e8fc);
                border-width: 3px;
            }
        """)
    
    def dragEnterEvent(self, event):
        """Evento quando arquivos são arrastados sobre o widget."""
        if event.mimeData().hasUrls():
            # Verificar se há pelo menos um arquivo local
            has_files = any(url.isLocalFile() for url in event.mimeData().urls())
            if has_files:
                event.acceptProposedAction()
                # Mudar visual para indicar que pode soltar
                self.setStyleSheet("""
                    DragDropWidget {
                        border: 3px solid #0078d4;
                        border-radius: 15px;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #d0e8fc, stop:1 #b8dffb);
                        color: #1a4480;
                    }
                """)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Evento quando o drag sai do widget."""
        # Restaurar visual normal
        self.setStyleSheet("""
            DragDropWidget {
                border: 2px dashed #4a90e2;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fbff, stop:1 #e8f4fd);
                color: #2c5aa0;
            }
            DragDropWidget:hover {
                border-color: #0078d4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f4fd, stop:1 #d0e8fc);
                border-width: 3px;
            }
        """)
    
    def dropEvent(self, event):
        """Evento quando arquivos são soltos no widget."""
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        
        if files:
            # Emitir signal com os arquivos
            self.files_dropped.emit(files)
            event.acceptProposedAction()
            
            # Restaurar visual normal
            self.setStyleSheet("""
                DragDropWidget {
                    border: 2px dashed #4a90e2;
                    border-radius: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8fbff, stop:1 #e8f4fd);
                    color: #2c5aa0;
                }
                DragDropWidget:hover {
                    border-color: #0078d4;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e8f4fd, stop:1 #d0e8fc);
                    border-width: 3px;
                }
            """)
        else:
            event.ignore()


class ConversionWorker(QThread):
    """Worker thread para executar conversões sem travar a UI."""
    
    progress_updated = Signal(int, str)  # progresso, mensagem
    conversion_finished = Signal(bool, str)  # sucesso, mensagem
    
    def __init__(self, converter, file_paths, output_dir, target_format, quality):
        super().__init__()
        self.converter = converter
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.target_format = target_format
        self.quality = quality
        self.should_stop = False
    
    def run(self):
        """Executa a conversão em thread separada com tratamento de erro robusto."""
        try:
            # Inicia a conversão
            success = self.converter.start_conversion(
                self.file_paths, self.output_dir, self.target_format, self.quality
            )
            
            if not success:
                self.conversion_finished.emit(False, "Falha ao iniciar conversão")
                return
            
            # Processa jobs um por um
            while self.converter.is_converting and not self.should_stop:
                success, has_more = self.converter.process_next_job()
                
                if not has_more:
                    break
                
                # Pequena pausa para não sobrecarregar
                self.msleep(100)
            
            if self.should_stop:
                self.converter.stop_conversion()
                self.conversion_finished.emit(False, "Conversão interrompida")
            else:
                summary = self.converter.get_conversion_summary()
                if summary['failed'] == 0:
                    self.conversion_finished.emit(True, f"Conversão concluída! {summary['completed']} arquivo(s) convertido(s).")
                else:
                    self.conversion_finished.emit(False, f"Conversão finalizada com {summary['failed']} erro(s).")
                    
        except Exception as e:
            # CAPTURA QUALQUER ERRO FATAL QUE POSSA CAUSAR CRASH
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! ERRO FATAL CAPTURADO NA THREAD DE CONVERSÃO !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            
            # Imprime o erro completo com a linha exata onde aconteceu
            traceback.print_exc()
            
            # Emite um sinal para a UI informando sobre o crash
            error_message = f"Erro fatal na thread: {type(e).__name__}: {str(e)}"
            self.conversion_finished.emit(False, error_message)
    
    def stop(self):
        """Para a conversão."""
        self.should_stop = True


class MainWindow(QMainWindow):
    """Janela principal da aplicação MultiConvert Pro."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inicializar o conversor
        self.converter = MainConverter()
        self.conversion_worker = None
        
        # Configurar callbacks do conversor
        self.converter.set_progress_callback(self.on_conversion_progress)
        self.converter.set_status_callback(self.on_conversion_status)
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configura a interface da janela principal."""
        # Configurações da janela
        self.setWindowTitle("MultiConvert Pro v1.0.0")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Aplicar estilo geral moderno azul
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f8ff, stop:1 #e6f3ff);
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c5aa0;
                border: 2px solid #4a90e2;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fbff);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                border-radius: 5px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4a90e2);
                color: white;
                border: 1px solid #3a7bd5;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6bb0ff, stop:1 #5ba0f2);
                border-color: #2c5aa0;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7bd5, stop:1 #2c5aa0);
            }
            
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cccccc, stop:1 #bbbbbb);
                color: #666666;
                border-color: #aaaaaa;
            }
            
            QComboBox {
                border: 2px solid #4a90e2;
                border-radius: 6px;
                padding: 6px;
                background: white;
                color: #2c5aa0;
                font-weight: bold;
            }
            
            QComboBox:hover {
                border-color: #0078d4;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a90e2;
                margin-right: 5px;
            }
            
            QListWidget {
                border: 2px solid #4a90e2;
                border-radius: 8px;
                background: white;
                alternate-background-color: #f8fbff;
                selection-background-color: #d0e8fc;
                color: #2c5aa0;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d0e8fc, stop:1 #b8ddf9);
                color: #1a4480;
            }
            
            QProgressBar {
                border: 2px solid #4a90e2;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                color: #2c5aa0;
                background: white;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4a90e2);
                border-radius: 6px;
                margin: 1px;
            }
            
            QLabel {
                color: #2c5aa0;
                font-weight: bold;
            }
            
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f8ff);
                border-top: 1px solid #4a90e2;
                color: #2c5aa0;
            }
            
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f8ff);
                color: #2c5aa0;
                border-bottom: 1px solid #4a90e2;
            }
            
            QMenuBar::item {
                padding: 6px 12px;
                background: transparent;
            }
            
            QMenuBar::item:selected {
                background: #d0e8fc;
                border-radius: 4px;
            }
            
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f8ff);
                border-bottom: 1px solid #4a90e2;
                spacing: 3px;
            }
            
            QToolBar::separator {
                background: #4a90e2;
                width: 1px;
                margin: 5px;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Criar componentes
        self.create_menu_bar()
        self.create_toolbar()
        self.create_drag_drop_area(main_layout)
        self.create_file_list_area(main_layout)
        self.create_conversion_controls(main_layout)
        self.create_progress_area(main_layout)
        self.create_status_bar()
        
        # Configurar drag & drop
        self.setup_drag_drop()
        
    def create_menu_bar(self):
        """Cria a barra de menu."""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        add_action = QAction("&Adicionar Arquivos...", self)
        add_action.setShortcut("Ctrl+O")
        file_menu.addAction(add_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Editar")
        
        clear_action = QAction("&Limpar Lista", self)
        clear_action.setShortcut("Ctrl+L")
        edit_menu.addAction(clear_action)
        
        # Menu Configurações
        settings_menu = menubar.addMenu("&Configurações")
        
        preferences_action = QAction("&Preferências...", self)
        preferences_action.setShortcut("Ctrl+P")
        settings_menu.addAction(preferences_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("&Ajuda")
        
        about_action = QAction("&Sobre...", self)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Cria a barra de ferramentas."""
        toolbar = self.addToolBar("Principal")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Botão Adicionar
        add_action = QAction("Adicionar", self)
        add_action.setToolTip("Adicionar arquivos para conversão")
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # Botão Remover
        remove_action = QAction("Remover", self)
        remove_action.setToolTip("Remover arquivos selecionados")
        toolbar.addAction(remove_action)
        
        toolbar.addSeparator()
        
        # Botão Converter
        convert_action = QAction("Converter", self)
        convert_action.setToolTip("Iniciar conversão")
        toolbar.addAction(convert_action)
        
    def create_drag_drop_area(self, parent_layout):
        """Cria a área de arrastar e soltar."""
        # Grupo para área de drag & drop
        drag_group = QGroupBox("Adicionar Arquivos")
        drag_layout = QVBoxLayout(drag_group)
        
        # Widget de drag & drop
        self.drag_drop_widget = DragDropWidget()
        drag_layout.addWidget(self.drag_drop_widget)
        
        parent_layout.addWidget(drag_group)
        
    def create_file_list_area(self, parent_layout):
        """Cria a área da lista de arquivos."""
        # Splitter para dividir a área
        splitter = QSplitter(Qt.Horizontal)
        
        # Lista de arquivos
        file_group = QGroupBox("Arquivos para Conversão")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        file_layout.addWidget(self.file_list)
        
        # Botões de controle da lista
        list_buttons_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("📁 Adicionar Arquivos")
        self.remove_files_btn = QPushButton("🗑️ Remover Selecionados")
        self.clear_list_btn = QPushButton("🧹 Limpar Lista")
        
        list_buttons_layout.addWidget(self.add_files_btn)
        list_buttons_layout.addWidget(self.remove_files_btn)
        list_buttons_layout.addWidget(self.clear_list_btn)
        list_buttons_layout.addStretch()
        
        file_layout.addLayout(list_buttons_layout)
        
        splitter.addWidget(file_group)
        
        # Painel de configurações
        config_group = QGroupBox("Configurações de Conversão")
        config_layout = QVBoxLayout(config_group)
        
        # Formato de saída
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato de Saída:"))
        
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems([
            "Selecione o formato...",
            "--- Áudio ---",
            "MP3", "WAV", "AAC", "FLAC", "OGG",
            "--- Vídeo ---",
            "MP4", "MKV", "AVI", "MOV", "WEBM",
            "--- Imagem ---",
            "JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP",
            "--- Documento ---",
            "PDF", "DOCX", "TXT", "ODT", "RTF"
        ])
        format_layout.addWidget(self.output_format_combo)
        format_layout.addStretch()
        
        config_layout.addLayout(format_layout)
        
        # Qualidade
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualidade:"))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Automática", "Baixa", "Média", "Alta", "Máxima"
        ])
        self.quality_combo.setCurrentText("Média")
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        
        config_layout.addLayout(quality_layout)
        
        # Pasta de destino
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Pasta de Destino:"))
        
        self.dest_path_label = QLabel("Mesma pasta dos arquivos originais")
        self.dest_path_label.setStyleSheet("color: gray; font-style: italic;")
        dest_layout.addWidget(self.dest_path_label)
        
        self.browse_dest_btn = QPushButton("📂 Procurar...")
        dest_layout.addWidget(self.browse_dest_btn)
        
        config_layout.addLayout(dest_layout)
        
        config_layout.addStretch()
        
        splitter.addWidget(config_group)
        
        # Configurar proporções do splitter
        splitter.setSizes([600, 400])
        
        parent_layout.addWidget(splitter)
        
    def create_conversion_controls(self, parent_layout):
        """Cria os controles de conversão."""
        controls_layout = QHBoxLayout()
        
        # Botão principal de conversão
        self.convert_btn = QPushButton("🚀 Iniciar Conversão")
        self.convert_btn.setMinimumHeight(45)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white;
                border: 2px solid #004578;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #0078d4);
                border-color: #003a5f;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004578, stop:1 #003a5f);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cccccc, stop:1 #bbbbbb);
                color: #666666;
                border-color: #aaaaaa;
            }
        """)
        self.convert_btn.setEnabled(False)  # Desabilitado inicialmente
        
        # Botão de parar
        self.stop_btn = QPushButton("⏹️ Parar")
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: 2px solid #a93226;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
                border-color: #922b21;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a93226, stop:1 #922b21);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cccccc, stop:1 #bbbbbb);
                color: #666666;
                border-color: #aaaaaa;
            }
        """)
        self.stop_btn.setEnabled(False)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.convert_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        parent_layout.addLayout(controls_layout)
        
    def create_progress_area(self, parent_layout):
        """Cria a área de progresso."""
        progress_group = QGroupBox("Progresso")
        progress_layout = QVBoxLayout(progress_group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setVisible(False)  # Oculta inicialmente
        
        # Label de status
        self.status_label = QLabel("Pronto para conversão")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(progress_group)
        
    def create_status_bar(self):
        """Cria a barra de status."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Mensagem inicial
        self.status_bar.showMessage("MultiConvert Pro v1.0.0 - Pronto")
        
        # Label para contagem de arquivos
        self.file_count_label = QLabel("0 arquivos")
        self.status_bar.addPermanentWidget(self.file_count_label)
        
    def setup_connections(self):
        """Configura as conexões de sinais e slots."""
        # Por enquanto, apenas conexões básicas
        # A lógica será implementada posteriormente
        
        # Botões da lista
        self.add_files_btn.clicked.connect(self.on_add_files)
        self.remove_files_btn.clicked.connect(self.on_remove_files)
        self.clear_list_btn.clicked.connect(self.on_clear_list)
        
        # Botão de conversão
        self.convert_btn.clicked.connect(self.on_convert)
        self.stop_btn.clicked.connect(self.on_stop)
        
        # Combo de formato
        self.output_format_combo.currentTextChanged.connect(self.on_format_changed)
        
        # Lista de arquivos
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Botão de procurar pasta
        self.browse_dest_btn.clicked.connect(self.on_browse_destination)
        
        # Drag & Drop
        self.drag_drop_widget.files_dropped.connect(self.on_files_dropped)
        
    # Métodos de callback (implementação funcional)
    def on_add_files(self):
        """Callback para adicionar arquivos."""
        from PySide6.QtWidgets import QFileDialog
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Arquivos para Conversão",
            "",
            "Todos os Arquivos (*.*);;Áudio (*.mp3 *.wav *.flac *.aac *.ogg);;Vídeo (*.mp4 *.avi *.mkv *.mov *.webm);;Imagem (*.jpg *.png *.gif *.bmp *.tiff *.webp);;Documento (*.pdf *.docx *.txt *.odt *.rtf)"
        )
        
        if files:
            for file_path in files:
                # Verificar se o arquivo já está na lista
                existing_items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
                if file_path not in existing_items:
                    self.file_list.addItem(file_path)
            
            self.update_file_count()
            self.status_bar.showMessage(f"{len(files)} arquivo(s) adicionado(s)")
        
    def on_remove_files(self):
        """Callback para remover arquivos."""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.file_list.row(item)
                self.file_list.takeItem(row)
            
            self.update_file_count()
            self.status_bar.showMessage(f"{len(selected_items)} arquivo(s) removido(s)")
        else:
            self.status_bar.showMessage("Nenhum arquivo selecionado para remover")
        
    def on_clear_list(self):
        """Callback para limpar lista."""
        if self.file_list.count() > 0:
            self.file_list.clear()
            self.update_file_count()
            self.status_bar.showMessage("Lista limpa")
    
    def on_files_dropped(self, files):
        """Callback para arquivos soltos via drag & drop."""
        added_files = []
        for file_path in files:
            # Verificar se o arquivo já está na lista
            existing_items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            if file_path not in existing_items:
                self.file_list.addItem(file_path)
                added_files.append(file_path)
        
        if added_files:
            self.update_file_count()
            self.status_bar.showMessage(f"{len(added_files)} arquivo(s) adicionado(s) via drag & drop")
        else:
            self.status_bar.showMessage("Arquivos já estão na lista")
        
    def on_convert(self):
        """Callback para iniciar conversão real."""
        if self.file_list.count() == 0:
            self.status_bar.showMessage("Adicione arquivos antes de converter")
            return
            
        format_text = self.output_format_combo.currentText()
        if not format_text or format_text.startswith("---") or format_text == "Selecione o formato...":
            self.status_bar.showMessage("Selecione um formato de saída")
            return
        
        # Obter lista de arquivos
        file_paths = []
        for i in range(self.file_list.count()):
            file_paths.append(self.file_list.item(i).text())
        
        # Obter pasta de destino
        dest_text = self.dest_path_label.text()
        if dest_text == "Mesma pasta dos arquivos originais":
            # Usar a pasta do primeiro arquivo como padrão
            import os
            output_dir = os.path.dirname(file_paths[0]) if file_paths else ""
        else:
            output_dir = dest_text
        
        # Obter qualidade
        quality = self.quality_combo.currentText()
        if quality == "Automática":
            quality = "Média"
        
        # Validar configuração antes de iniciar
        is_valid, message = self.converter.validate_conversion_setup(file_paths, output_dir, format_text)
        if not is_valid:
            self.status_bar.showMessage(f"Erro: {message}")
            return
        
        # Configurar UI para conversão
        self.convert_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.status_label.setText(f"Iniciando conversão para {format_text}...")
        self.status_bar.showMessage("Conversão iniciada")
        
        # Criar e iniciar worker thread
        self.conversion_worker = ConversionWorker(
            self.converter, file_paths, output_dir, format_text, quality
        )
        
        # Conectar sinais
        self.conversion_worker.progress_updated.connect(self.on_worker_progress)
        self.conversion_worker.conversion_finished.connect(self.on_conversion_finished)
        
        # Iniciar conversão em thread separada
        self.conversion_worker.start()
        
    def on_stop(self):
        """Callback para parar conversão."""
        if self.conversion_worker and self.conversion_worker.isRunning():
            self.conversion_worker.stop()
            self.conversion_worker.wait(3000)  # Aguarda até 3 segundos
        
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Conversão interrompida")
        self.status_bar.showMessage("Conversão parada")
        
    def on_format_changed(self, format_text):
        """Callback para mudança de formato."""
        if format_text and not format_text.startswith("---") and format_text != "Selecione o formato...":
            self.update_convert_button_state()
        
    def on_conversion_progress(self, progress, message):
        """Callback para atualização de progresso do conversor."""
        self.progress_bar.setValue(progress)
        if message:
            self.status_label.setText(message)
    
    def on_conversion_status(self, message):
        """Callback para atualização de status do conversor."""
        self.status_bar.showMessage(message)
    
    def on_worker_progress(self, progress, message):
        """Callback para progresso do worker thread."""
        self.progress_bar.setValue(progress)
        if message:
            self.status_label.setText(message)
    
    def on_conversion_finished(self, success, message):
        """Callback para finalização da conversão."""
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Conversão concluída com sucesso!")
            self.status_bar.showMessage(message)
        else:
            self.status_label.setText("Erro na conversão")
            self.status_bar.showMessage(f"Erro: {message}")
        
        # Limpar worker
        if self.conversion_worker:
            self.conversion_worker.deleteLater()
            self.conversion_worker = None
            
    def on_browse_destination(self):
        """Callback para selecionar pasta de destino."""
        from PySide6.QtWidgets import QFileDialog
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Destino",
            ""
        )
        
        if folder:
            self.dest_path_label.setText(folder)
            self.dest_path_label.setStyleSheet("color: #2c5aa0; font-style: normal; font-weight: bold;")
            self.status_bar.showMessage(f"Pasta de destino: {folder}")
        
    def setup_drag_drop(self):
        """Configura funcionalidade de arrastar e soltar."""
        # A funcionalidade de drag & drop agora está implementada no DragDropWidget
        pass
            
    def on_selection_changed(self):
        """Callback para mudança de seleção na lista."""
        selected_items = self.file_list.selectedItems()
        self.remove_files_btn.setEnabled(len(selected_items) > 0)
        
    def update_file_count(self):
        """Atualiza a contagem de arquivos na barra de status."""
        count = self.file_list.count()
        self.file_count_label.setText(f"{count} arquivo{'s' if count != 1 else ''}")
        self.update_convert_button_state()
        
    def update_convert_button_state(self):
        """Atualiza o estado do botão de conversão."""
        has_files = self.file_list.count() > 0
        has_format = (self.output_format_combo.currentText() and 
                     not self.output_format_combo.currentText().startswith("---") and
                     self.output_format_combo.currentText() != "Selecione o formato...")
        
        self.convert_btn.setEnabled(has_files and has_format)