#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Engine OnlyOffice

Este módulo contém a classe OnlyOfficeEngine que executa
conversões de documentos usando OnlyOffice DocumentBuilder.

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

import os
import subprocess
import tempfile
import json
import shutil
import requests
import time
from typing import Optional, Callable
from pathlib import Path


class OnlyOfficeEngine:
    """Engine para conversões usando OnlyOffice DocumentBuilder."""
    
    def __init__(self, executable_path: Optional[str] = None, server_url: str = "http://localhost"):
        self.executable_path = executable_path or self._find_docbuilder()
        self.server_url = server_url.rstrip('/')
        self.use_server = True  # Priorizar servidor sobre executável local
        
        # Mapeamento de formatos suportados pelo OnlyOffice
        self.format_mapping = {
            # Documentos de texto
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'doc',
            'odt': 'odt',
            'rtf': 'rtf',
            'txt': 'txt',
            'html': 'html',
            
            # Planilhas
            'xlsx': 'xlsx',
            'xls': 'xls',
            'ods': 'ods',
            'csv': 'csv',
            
            # Apresentações
            'pptx': 'pptx',
            'ppt': 'ppt',
            'odp': 'odp'
        }
        
        # Formatos de entrada suportados
        self.supported_input_formats = ['txt', 'docx', 'doc', 'odt', 'rtf', 'xlsx', 'xls', 'ods', 'pptx', 'ppt', 'odp']
        
        # Formatos de saída suportados
        self.supported_output_formats = ['pdf', 'docx', 'odt', 'rtf', 'txt', 'html', 'xlsx', 'ods', 'pptx', 'odp']
    
    def _find_docbuilder(self) -> Optional[str]:
        """Encontra o executável do DocumentBuilder."""
        possible_paths = [
            # Caminhos comuns do OnlyOffice no Windows
            r"C:\Program Files\ONLYOFFICE\DocumentServer\core-fonts\docbuilder.exe",
            r"C:\Program Files (x86)\ONLYOFFICE\DocumentServer\core-fonts\docbuilder.exe",
            r"C:\ONLYOFFICE\DocumentServer\core-fonts\docbuilder.exe",
            # PATH environment
            "docbuilder",
            "docbuilder.exe"
        ]
        
        for path in possible_paths:
            if os.path.isfile(path) or shutil.which(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Verifica se o OnlyOffice está disponível (servidor ou executável local)."""
        if self.use_server:
            return self._check_server_availability()
        return self.executable_path is not None and os.path.exists(self.executable_path)
    
    def _check_server_availability(self) -> bool:
        """Verifica se o servidor OnlyOffice está rodando."""
        try:
            response = requests.get(f"{self.server_url}/healthcheck", timeout=5)
            return response.status_code == 200
        except:
            try:
                # Tenta endpoint alternativo
                response = requests.get(f"{self.server_url}/", timeout=5)
                return response.status_code == 200
            except:
                return False   
    def get_version(self) -> str:
        """Obtém a versão do OnlyOffice DocumentBuilder."""
        if not self.is_available():
            return "Não disponível"
        
        try:
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "Versão desconhecida"
        except Exception:
            return "Erro ao obter versão"
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """Converte um arquivo usando OnlyOffice DocumentBuilder.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            target_format: Formato de saída
            quality: Preset de qualidade (não usado pelo OnlyOffice)
            progress_callback: Callback para progresso
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        print(f"[OnlyOffice] Iniciando conversão: {input_path} -> {output_path} ({target_format})")
        
        if not self.is_available():
            error_msg = "OnlyOffice DocumentBuilder não está disponível"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
        
        if not os.path.exists(input_path):
            error_msg = f"Arquivo de entrada não encontrado: {input_path}"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
        
        input_ext = Path(input_path).suffix.lower().lstrip('.')
        
        if input_ext not in self.supported_input_formats:
            error_msg = f"Formato de entrada não suportado: {input_ext}"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
        
        if target_format not in self.supported_output_formats:
            error_msg = f"Formato de saída não suportado: {target_format}"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
        
        try:
            if progress_callback:
                progress_callback(10, "Preparando conversão OnlyOffice...")
            
            # Usar servidor se disponível, senão usar executável local
            if self.use_server and self._check_server_availability():
                return self._convert_via_server(input_path, output_path, target_format, progress_callback)
            else:
                return self._convert_via_executable(input_path, output_path, target_format, progress_callback)
                
        except Exception as e:
            error_msg = f"Erro durante conversão OnlyOffice: {str(e)}"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
    
    def _convert_via_executable(self, input_path: str, output_path: str, target_format: str, progress_callback: Optional[Callable] = None) -> tuple[bool, str]:
        """Converte usando o executável local do DocumentBuilder."""
        try:
            # Criar script de conversão temporário
            script_content = self._create_conversion_script(
                input_path, output_path, target_format
            )
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as script_file:
                script_file.write(script_content)
                script_path = script_file.name
            
            print(f"[OnlyOffice] Script criado: {script_path}")
            print(f"[OnlyOffice] Executável: {self.executable_path}")
            
            if progress_callback:
                progress_callback(30, "Executando conversão OnlyOffice...")
            
            # Executar o DocumentBuilder
            result = subprocess.run(
                [self.executable_path, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            print(f"[OnlyOffice] Código de retorno: {result.returncode}")
            print(f"[OnlyOffice] Stdout: {result.stdout}")
            print(f"[OnlyOffice] Stderr: {result.stderr}")
            
            # Limpar arquivo de script temporário
            try:
                os.unlink(script_path)
            except Exception:
                pass
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    if progress_callback:
                        progress_callback(100, "Conversão OnlyOffice concluída!")
                    success_msg = f"Conversão realizada com sucesso usando OnlyOffice"
                    print(f"[OnlyOffice] Sucesso: {success_msg}")
                    return True, success_msg
                else:
                    error_msg = f"Arquivo de saída não foi criado: {output_path}"
                    print(f"[OnlyOffice] Erro: {error_msg}")
                    return False, error_msg
            else:
                error_msg = f"Erro na conversão OnlyOffice: {result.stderr or result.stdout}"
                print(f"[OnlyOffice] Erro: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Timeout na conversão OnlyOffice (5 minutos)"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro durante conversão OnlyOffice: {str(e)}"
            print(f"[OnlyOffice] Erro: {error_msg}")
            return False, error_msg
    
    def _convert_via_server(self, input_path: str, output_path: str, target_format: str, progress_callback: Optional[Callable] = None) -> tuple[bool, str]:
        """Converte usando a API do servidor OnlyOffice Document Server."""
        try:
            if progress_callback:
                progress_callback(20, "Preparando arquivo para conversão...")
            
            # Usar diretório compartilhado
            shared_dir = "C:\\temp\\onlyoffice-shared"
            os.makedirs(shared_dir, exist_ok=True)
            
            # Copiar arquivo para diretório compartilhado
            file_name = os.path.basename(input_path)
            shared_file_path = os.path.join(shared_dir, file_name)
            shutil.copy2(input_path, shared_file_path)
            
            try:
                # URL do arquivo para o OnlyOffice (caminho interno do contêiner)
                file_url = f"file:///var/www/onlyoffice/documentserver/shared/{file_name}"
                
                # Determinar formato de saída
                output_format = target_format.lower()
                if output_format.startswith('.'):
                    output_format = output_format[1:]
                
                # Preparar dados JSON para a API do OnlyOffice
                json_data = {
                    'async': False,
                    'filetype': os.path.splitext(input_path)[1][1:].lower(),
                    'key': str(int(time.time())),
                    'outputtype': output_format,
                    'title': file_name,
                    'url': file_url
                }
                
                if progress_callback:
                    progress_callback(50, "Processando conversão no servidor...")
                
                # Fazer requisição de conversão
                conversion_url = f"{self.server_url}/ConvertService.ashx"
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(
                    conversion_url, 
                    data=json.dumps(json_data), 
                    headers=headers, 
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('error') == 0:  # Sucesso
                        download_url = result.get('fileUrl')
                        if download_url:
                            if progress_callback:
                                progress_callback(80, "Baixando arquivo convertido...")
                            
                            # Baixar arquivo convertido
                            download_response = requests.get(download_url, timeout=60)
                            if download_response.status_code == 200:
                                with open(output_path, 'wb') as output_file:
                                    output_file.write(download_response.content)
                                
                                if progress_callback:
                                    progress_callback(100, "Conversão OnlyOffice Server concluída!")
                                
                                success_msg = "Conversão realizada com sucesso usando OnlyOffice Server"
                                print(f"[OnlyOffice Server] Sucesso: {success_msg}")
                                return True, success_msg
                            else:
                                error_msg = f"Erro ao baixar arquivo convertido: {download_response.status_code}"
                                print(f"[OnlyOffice Server] Erro: {error_msg}")
                                return False, error_msg
                        else:
                            error_msg = "URL de download não fornecida pelo servidor"
                            print(f"[OnlyOffice Server] Erro: {error_msg}")
                            return False, error_msg
                    else:
                        error_msg = f"Erro na conversão: {result.get('error', 'Erro desconhecido')}"
                        print(f"[OnlyOffice Server] Erro: {error_msg}")
                        return False, error_msg
                else:
                    error_msg = f"Erro na requisição: {response.status_code} - {response.text}"
                    print(f"[OnlyOffice Server] Erro: {error_msg}")
                    return False, error_msg
                    
            finally:
                # Limpar arquivo temporário
                try:
                    if os.path.exists(shared_file_path):
                        os.remove(shared_file_path)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Erro durante conversão via servidor: {str(e)}"
            print(f"[OnlyOffice Server] Erro: {error_msg}")
            return False, error_msg
    
    def _create_conversion_script(self, input_path: str, output_path: str, target_format: str) -> str:
        """Cria o script JavaScript para o DocumentBuilder."""
        # Normalizar caminhos para JavaScript (usar barras normais)
        input_path_js = input_path.replace('\\', '/')
        output_path_js = output_path.replace('\\', '/')
        
        # Determinar o tipo de documento baseado na extensão de entrada
        input_ext = Path(input_path).suffix.lower().lstrip('.')
        
        if input_ext in ['txt', 'docx', 'doc', 'odt', 'rtf']:
            doc_type = 'docx'  # Documento de texto
        elif input_ext in ['xlsx', 'xls', 'ods', 'csv']:
            doc_type = 'xlsx'  # Planilha
        elif input_ext in ['pptx', 'ppt', 'odp']:
            doc_type = 'pptx'  # Apresentação
        else:
            doc_type = 'docx'  # Padrão
        
        # Mapear formato de saída para código do OnlyOffice
        format_codes = {
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'doc',
            'odt': 'odt',
            'rtf': 'rtf',
            'txt': 'txt',
            'html': 'html',
            'xlsx': 'xlsx',
            'xls': 'xls',
            'ods': 'ods',
            'pptx': 'pptx',
            'ppt': 'ppt',
            'odp': 'odp'
        }
        
        output_format = format_codes.get(target_format, target_format)
        
        script = f"""
builder.OpenFile("{input_path_js}");
builder.SaveFile("{output_format}", "{output_path_js}");
builder.CloseFile();
"""
        
        return script
    
    def can_convert(self, input_format: str, output_format: str) -> bool:
        """Verifica se uma conversão específica é suportada."""
        return (input_format.lower() in self.supported_input_formats and 
                output_format.lower() in self.supported_output_formats)
    
    def get_supported_conversions(self) -> dict:
        """Retorna as conversões suportadas pelo OnlyOffice."""
        return {
            'input_formats': self.supported_input_formats,
            'output_formats': self.supported_output_formats,
            'engine': 'OnlyOffice DocumentBuilder'
        }