#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Conversor Universal de Arquivos

Ponto de entrada principal da aplicação.
Este arquivo inicializa a aplicação Qt e carrega a janela principal.

Autor: MultiConvert Pro Team
Versão: 1.0.0
Licença: MIT
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt, QDir
    from PySide6.QtGui import QIcon
except ImportError as e:
    print(f"Erro ao importar PySide6: {e}")
    print("Instale o PySide6 com: pip install PySide6")
    sys.exit(1)

# Importar a janela principal
try:
    from ui.windows.main_window import MainWindow
except ImportError as e:
    print(f"Erro ao importar MainWindow: {e}")
    sys.exit(1)


class MultiConvertApp:
    """Classe principal da aplicação MultiConvert Pro."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        
    def setup_application(self):
        """Configura a aplicação Qt."""
        # Criar aplicação Qt
        self.app = QApplication(sys.argv)
        
        # Configurar propriedades da aplicação
        self.app.setApplicationName("MultiConvert Pro")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("MultiConvert Pro Team")
        self.app.setOrganizationDomain("multiconvertpro.com")
        
        # Configurar ícone da aplicação (se existir)
        icon_path = project_root / "assets" / "icons" / "app_icon.ico"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        
        # Configurar estilo
        self.app.setStyle("Fusion")  # Estilo moderno
        
    def create_main_window(self):
        """Cria e configura a janela principal."""
        try:
            self.main_window = MainWindow()
            self.main_window.show()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Erro de Inicialização",
                f"Erro ao criar a janela principal:\n{str(e)}"
            )
            return False
        return True
        
    def run(self):
        """Executa a aplicação."""
        try:
            # Configurar aplicação
            self.setup_application()
            
            # Criar janela principal
            if not self.create_main_window():
                return 1
            
            # Executar loop principal
            return self.app.exec()
            
        except Exception as e:
            print(f"Erro fatal na aplicação: {e}")
            return 1
        finally:
            # Limpeza
            if self.app:
                self.app.quit()


def main():
    """Função principal."""
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--version", "-v"]:
            print("MultiConvert Pro v1.0.0")
            return 0
        elif sys.argv[1] in ["--help", "-h"]:
            print("MultiConvert Pro - Conversor Universal de Arquivos")
            print("Uso: python main.py [opções]")
            print("Opções:")
            print("  --version, -v    Mostrar versão")
            print("  --help, -h       Mostrar esta ajuda")
            return 0
    
    # Criar e executar aplicação
    app = MultiConvertApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())