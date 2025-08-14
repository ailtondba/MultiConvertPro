#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Engine LibreOffice

Este módulo contém a classe LibreOfficeEngine que executa
conversões de documentos usando LibreOffice em modo headless.

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

import os
import subprocess
import shutil
import tempfile
from typing import Optional, Callable
from pathlib import Path


class LibreOfficeEngine:
    """Engine para conversões usando LibreOffice CLI."""
    
    def __init__(self):
        self.libreoffice_paths = [
            # Caminhos comuns do LibreOffice no Windows
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            # Portable versions
            r"LibreOfficePortable\App\libreoffice\program\soffice.exe",
            # PATH environment
            "soffice",
            "libreoffice"
        ]
        
        self.executable_path = self._find_libreoffice()
        
        # Mapeamento de formatos suportados
        self.format_mapping = {
            # Documentos de texto
            'pdf': 'pdf:writer_pdf_Export',
            'docx': 'docx:MS Word 2007 XML',
            'doc': 'doc:MS Word 97',
            'odt': 'odt:writer8',
            'rtf': 'rtf:Rich Text Format',
            'txt': 'txt:Text (encoded)',
            'html': 'html:HTML (StarWriter)',
            
            # Planilhas
            'xlsx': 'xlsx:Calc MS Excel 2007 XML',
            'xls': 'xls:MS Excel 97',
            'ods': 'ods:calc8',
            'csv': 'csv:Text - txt - csv (StarCalc)',
            
            # Apresentações
            'pptx': 'pptx:Impress MS PowerPoint 2007 XML',
            'ppt': 'ppt:MS PowerPoint 97',
            'odp': 'odp:impress8'
        }
        
        # Configurações de qualidade para PDF
        self.pdf_quality_settings = {
            'baixa': {
                'SelectPdfVersion': '1',  # PDF 1.4
                'CompressMode': '1',      # Compressão máxima
                'Quality': '30',          # Qualidade de imagem baixa
                'ReduceImageResolution': 'true',
                'MaxImageResolution': '150'
            },
            'media': {
                'SelectPdfVersion': '1',
                'CompressMode': '1',
                'Quality': '75',
                'ReduceImageResolution': 'true',
                'MaxImageResolution': '300'
            },
            'alta': {
                'SelectPdfVersion': '1',
                'CompressMode': '2',      # Compressão sem perdas
                'Quality': '90',
                'ReduceImageResolution': 'false',
                'MaxImageResolution': '600'
            },
            'maxima': {
                'SelectPdfVersion': '1',
                'CompressMode': '0',      # Sem compressão
                'Quality': '100',
                'ReduceImageResolution': 'false',
                'EmbedStandardFonts': 'true'
            }
        }
    
    def _find_libreoffice(self) -> Optional[str]:
        """Encontra o executável do LibreOffice no sistema."""
        for path in self.libreoffice_paths:
            try:
                if os.path.isfile(path):
                    return path
                elif shutil.which(path):
                    return shutil.which(path)
            except Exception:
                continue
        return None
    
    def is_available(self) -> bool:
        """Verifica se o LibreOffice está disponível."""
        return self.executable_path is not None
    
    def get_version(self) -> str:
        """Obtém a versão do LibreOffice instalado."""
        if not self.is_available():
            return "LibreOffice não encontrado"
        
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "Versão desconhecida"
        except Exception as e:
            return f"Erro ao obter versão: {str(e)}"
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """Converte um documento usando LibreOffice.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            target_format: Formato de saída
            quality: Preset de qualidade
            progress_callback: Callback para progresso
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        print(f"DEBUG LibreOffice: Verificando disponibilidade. executable_path: {self.executable_path}")
        if not self.is_available():
            print("DEBUG LibreOffice: LibreOffice não está disponível")
            return False, "LibreOffice não está instalado ou não foi encontrado"
        
        try:
            print(f"DEBUG LibreOffice: Iniciando conversão {input_path} -> {target_format}")
            if progress_callback:
                progress_callback(10, "Preparando conversão com LibreOffice...")
            
            # Validar formato de saída
            if target_format not in self.format_mapping:
                print(f"DEBUG LibreOffice: Formato {target_format} não suportado")
                return False, f"Formato {target_format} não suportado pelo LibreOffice"
            
            print(f"DEBUG LibreOffice: Formato mapeado: {self.format_mapping[target_format]}")
            
            # Criar diretório temporário para a conversão
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"DEBUG LibreOffice: Diretório temporário: {temp_dir}")
                if progress_callback:
                    progress_callback(20, "Configurando parâmetros de conversão...")
                
                # Preparar comando base
                cmd = [
                    self.executable_path,
                    '--headless',
                    '--convert-to',
                    self.format_mapping[target_format],
                    '--outdir',
                    temp_dir,
                    input_path
                ]
                
                # Adicionar configurações específicas para PDF
                if target_format == 'pdf':
                    cmd = self._add_pdf_options(cmd, quality, temp_dir)
                
                print(f"DEBUG LibreOffice: Comando: {' '.join(cmd)}")
                
                if progress_callback:
                    progress_callback(30, "Executando LibreOffice...")
                
                # Executar conversão
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutos timeout
                    cwd=temp_dir
                )
                
                print(f"DEBUG LibreOffice: Return code: {result.returncode}")
                print(f"DEBUG LibreOffice: STDOUT: {result.stdout}")
                print(f"DEBUG LibreOffice: STDERR: {result.stderr}")
                
                if progress_callback:
                    progress_callback(80, "Processando resultado...")
                
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Erro desconhecido do LibreOffice"
                    print(f"DEBUG LibreOffice: Falha na conversão: {error_msg}")
                    return False, f"LibreOffice falhou: {error_msg}"
                
                # Encontrar arquivo de saída no diretório temporário
                input_name = Path(input_path).stem
                temp_output = None
                
                for file in os.listdir(temp_dir):
                    if file.startswith(input_name) and file.endswith(f'.{target_format}'):
                        temp_output = os.path.join(temp_dir, file)
                        break
                
                if not temp_output or not os.path.exists(temp_output):
                    return False, "Arquivo de saída não foi criado pelo LibreOffice"
                
                # Criar diretório de saída se necessário
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Mover arquivo para destino final
                shutil.move(temp_output, output_path)
                
                if progress_callback:
                    progress_callback(100, "Conversão concluída!")
                
                return True, f"Documento convertido com sucesso para {target_format.upper()}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: LibreOffice demorou muito para responder"
        except Exception as e:
            return False, f"Erro na conversão com LibreOffice: {str(e)}"
    
    def _add_pdf_options(self, cmd: list, quality: str, temp_dir: str) -> list:
        """Adiciona opções específicas para conversão PDF."""
        try:
            # Criar arquivo de configuração PDF
            pdf_settings = self.pdf_quality_settings.get(quality, self.pdf_quality_settings['media'])
            
            config_content = []
            for key, value in pdf_settings.items():
                config_content.append(f"{key}={value}")
            
            config_file = os.path.join(temp_dir, 'pdf_export.txt')
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(config_content))
            
            # Adicionar parâmetros PDF ao comando
            pdf_cmd = cmd.copy()
            pdf_cmd.extend([
                '--infilter=writer_pdf_Export',
                f'--outfilter={config_file}'
            ])
            
            return pdf_cmd
            
        except Exception:
            # Se falhar, retornar comando original
            return cmd
    
    def batch_convert(
        self,
        input_files: list,
        output_dir: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None
    ) -> tuple[bool, str, list]:
        """Converte múltiplos arquivos em lote.
        
        Returns:
            Tupla (sucesso_geral, mensagem, lista_de_resultados)
        """
        if not self.is_available():
            return False, "LibreOffice não disponível", []
        
        results = []
        successful = 0
        total = len(input_files)
        
        try:
            for i, input_file in enumerate(input_files):
                if progress_callback:
                    overall_progress = int((i / total) * 100)
                    progress_callback(overall_progress, f"Convertendo arquivo {i+1} de {total}...")
                
                # Gerar nome do arquivo de saída
                input_name = Path(input_file).stem
                output_file = os.path.join(output_dir, f"{input_name}.{target_format}")
                
                # Converter arquivo individual
                success, message = self.convert(
                    input_path=input_file,
                    output_path=output_file,
                    target_format=target_format,
                    quality=quality
                )
                
                results.append({
                    'input': input_file,
                    'output': output_file,
                    'success': success,
                    'message': message
                })
                
                if success:
                    successful += 1
            
            if progress_callback:
                progress_callback(100, f"Conversão em lote concluída: {successful}/{total} sucessos")
            
            overall_success = successful > 0
            summary = f"Conversão em lote: {successful}/{total} arquivos convertidos com sucesso"
            
            return overall_success, summary, results
            
        except Exception as e:
            return False, f"Erro na conversão em lote: {str(e)}", results
    
    def get_supported_formats(self) -> dict:
        """Retorna os formatos suportados pelo LibreOffice."""
        return {
            'input': [
                'doc', 'docx', 'odt', 'rtf', 'txt',  # Documentos
                'xls', 'xlsx', 'ods', 'csv',         # Planilhas
                'ppt', 'pptx', 'odp'                 # Apresentações
            ],
            'output': list(self.format_mapping.keys())
        }
    
    def test_installation(self) -> dict:
        """Testa a instalação do LibreOffice."""
        result = {
            'available': self.is_available(),
            'path': self.executable_path,
            'version': None,
            'test_conversion': False,
            'supported_formats': len(self.format_mapping)
        }
        
        if result['available']:
            result['version'] = self.get_version()
            
            # Teste básico de conversão
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
                    temp_input.write("Teste de conversão LibreOffice")
                    temp_input_path = temp_input.name
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_output:
                    temp_output_path = temp_output.name
                
                success, _ = self.convert(
                    input_path=temp_input_path,
                    output_path=temp_output_path,
                    target_format='pdf'
                )
                
                result['test_conversion'] = success
                
                # Limpar arquivos temporários
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except Exception:
                    pass
                    
            except Exception:
                result['test_conversion'] = False
        
        return result