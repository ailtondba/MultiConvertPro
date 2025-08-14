import os
from pathlib import Path
from typing import List, Dict, Callable, Optional
import filetype

# Importar conversores especializados
from .video_converter import VideoConverter
from .audio_converter import AudioConverter
from .image_converter import ImageConverter
from .document_converter import DocumentConverter

class ConversionJob:
    """Representa um trabalho de conversão individual."""
    
    def __init__(self, input_path: str, output_path: str, target_format: str, quality: str = 'Média'):
        self.input_path = input_path
        self.output_path = output_path
        self.target_format = target_format
        self.quality = quality
        self.status = 'pending'  # pending, processing, completed, failed
        self.progress = 0
        self.error_message = ''
        
    def __str__(self):
        return f"ConversionJob({Path(self.input_path).name} -> {self.target_format})"

class MainConverter:
    """Conversor principal que gerencia todas as conversões e roteia para conversores especializados."""
    
    def __init__(self):
        self.jobs: List[ConversionJob] = []
        self.current_job_index = 0
        self.is_converting = False
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # Inicializar conversores especializados
        self.video_converter = VideoConverter()
        self.audio_converter = AudioConverter()
        self.image_converter = ImageConverter()
        self.document_converter = DocumentConverter()
        
        # Mapeamento de extensões para tipos de arquivo
        self.extension_mapping = {
            # Vídeo
            'mp4': 'video', 'avi': 'video', 'mkv': 'video', 'mov': 'video',
            'wmv': 'video', 'flv': 'video', 'webm': 'video', 'm4v': 'video',
            'mpg': 'video', 'mpeg': 'video', '3gp': 'video', 'ogv': 'video',
            
            # Áudio
            'mp3': 'audio', 'wav': 'audio', 'flac': 'audio', 'aac': 'audio',
            'ogg': 'audio', 'm4a': 'audio', 'wma': 'audio', 'opus': 'audio',
            'aiff': 'audio', 'au': 'audio', 'ra': 'audio',
            
            # Imagem
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
            'bmp': 'image', 'tiff': 'image', 'tif': 'image', 'webp': 'image',
            'ico': 'image', 'svg': 'image', 'psd': 'image', 'raw': 'image',
            
            # Documento
            'pdf': 'document', 'doc': 'document', 'docx': 'document',
            'odt': 'document', 'rtf': 'document', 'txt': 'document',
            'html': 'document', 'htm': 'document', 'xls': 'document',
            'xlsx': 'document', 'ods': 'document', 'csv': 'document',
            'ppt': 'document', 'pptx': 'document', 'odp': 'document'
        }
        
        # Cache de formatos suportados
        self._supported_formats_cache = None
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Define callback para atualização de progresso."""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Define callback para atualização de status."""
        self.status_callback = callback
    
    def detect_file_type(self, file_path: str) -> str:
        """Detecta o tipo de arquivo baseado na extensão e conteúdo.
        
        Returns:
            Tipo do arquivo: 'video', 'audio', 'image', 'document' ou 'unknown'
        """
        try:
            # Primeiro, tentar pela extensão
            extension = Path(file_path).suffix.lower().lstrip('.')
            if extension in self.extension_mapping:
                return self.extension_mapping[extension]
            
            # Se não encontrou pela extensão, tentar detectar pelo conteúdo
            kind = filetype.guess(file_path)
            if kind is not None:
                mime_type = kind.mime
                if mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('application/') and any(doc_type in mime_type for doc_type in ['pdf', 'word', 'document', 'text']):
                    return 'document'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def get_converter_for_type(self, file_type: str):
        """Retorna o conversor apropriado para o tipo de arquivo."""
        converters = {
            'video': self.video_converter,
            'audio': self.audio_converter,
            'image': self.image_converter,
            'document': self.document_converter
        }
        return converters.get(file_type)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Retorna todos os formatos suportados por categoria."""
        if self._supported_formats_cache is None:
            self._supported_formats_cache = {
                'video': {
                    'input': self.video_converter.get_supported_input_formats(),
                    'output': self.video_converter.get_supported_output_formats()
                },
                'audio': {
                    'input': self.audio_converter.get_supported_input_formats(),
                    'output': self.audio_converter.get_supported_output_formats()
                },
                'image': {
                    'input': self.image_converter.get_supported_input_formats(),
                    'output': self.image_converter.get_supported_output_formats()
                },
                'document': {
                    'input': self.document_converter.get_supported_input_formats(),
                    'output': self.document_converter.get_supported_output_formats()
                }
            }
        return self._supported_formats_cache
    
    def is_format_supported(self, input_format: str, output_format: str) -> bool:
        """Verifica se uma conversão específica é suportada."""
        # Verifica se não é uma conversão para o mesmo formato
        if input_format.lower() == output_format.lower():
            return False
        
        supported = self.get_supported_formats()
        
        for category in supported.values():
            if (input_format.lower() in [fmt.lower() for fmt in category['input']] and 
                output_format.lower() in [fmt.lower() for fmt in category['output']]):
                return True
        
        return False
    
    def add_conversion_job(self, input_path: str, output_dir: str, target_format: str, quality: str = 'Média') -> bool:
        """Adiciona um trabalho de conversão à fila se a conversão for suportada."""
        try:
            # Verifica se o arquivo de entrada existe
            if not os.path.exists(input_path):
                return False
            
            # Verifica se o tipo de arquivo é suportado
            file_type = self.detect_file_type(input_path)
            if file_type == 'unknown':
                return False
            
            # Verifica se a conversão específica é suportada
            input_extension = Path(input_path).suffix.lower().lstrip('.')
            if not self.is_format_supported(input_extension, target_format):
                return False
            
            # Gera o nome do arquivo de saída
            input_file = Path(input_path)
            output_filename = f"{input_file.stem}.{target_format.lower()}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Cria o job
            job = ConversionJob(input_path, output_path, target_format, quality)
            self.jobs.append(job)
            
            return True
            
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Erro ao adicionar conversão: {str(e)}")
            return False
    
    def clear_jobs(self):
        """Limpa todos os trabalhos da fila."""
        if not self.is_converting:
            self.jobs.clear()
            self.current_job_index = 0
    
    def get_job_count(self) -> int:
        """Retorna o número total de trabalhos."""
        return len(self.jobs)
    
    def get_pending_jobs(self) -> List[ConversionJob]:
        """Retorna lista de trabalhos pendentes."""
        return [job for job in self.jobs if job.status == 'pending']
    
    def validate_conversion_setup(self, file_paths: List[str], output_dir: str, target_format: str) -> tuple[bool, str]:
        """Valida se a configuração de conversão está correta."""
        # Verifica se há arquivos selecionados
        if not file_paths:
            return False, "Nenhum arquivo selecionado para conversão"
        
        # Verifica se o diretório de saída foi definido
        if not output_dir or output_dir == "Selecione uma pasta de destino":
            return False, "Selecione uma pasta de destino"
        
        # Verifica se o diretório de saída existe ou pode ser criado
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return False, f"Não foi possível criar/acessar a pasta de destino: {str(e)}"
        
        # Verifica se os arquivos existem
        missing_files = [f for f in file_paths if not os.path.exists(f)]
        if missing_files:
            return False, f"Arquivos não encontrados: {', '.join(missing_files)}"
        
        # Verifica se pelo menos um arquivo pode ser convertido para o formato de saída
        convertible_files = []
        unsupported_files = []
        same_format_files = []
        
        for file_path in file_paths:
            file_type = self.detect_file_type(file_path)
            input_extension = Path(file_path).suffix.lower().lstrip('.')
            
            if file_type == 'unknown':
                unsupported_files.append(Path(file_path).name)
                continue
            
            # Verificar se é conversão para o mesmo formato
            if input_extension.lower() == target_format.lower():
                same_format_files.append(Path(file_path).name)
                continue
            
            # Verificar se a conversão é suportada
            if self.is_format_supported(input_extension, target_format):
                convertible_files.append(file_path)
            else:
                unsupported_files.append(f"{Path(file_path).name} ({input_extension} → {target_format})")
        
        if not convertible_files:
            if same_format_files:
                return False, f"Não é possível converter arquivos para o mesmo formato. Arquivos já em {target_format.upper()}: {', '.join(same_format_files)}"
            elif unsupported_files:
                return False, f"Nenhum arquivo pode ser convertido para {target_format.upper()}. Arquivos não suportados: {', '.join(unsupported_files)}"
            else:
                return False, f"Formato de saída '{target_format}' não é suportado"
        
        # Avisar sobre arquivos não suportados ou do mesmo formato, mas permitir conversão dos suportados
        warnings = []
        if same_format_files:
            warnings.append(f"{len(same_format_files)} arquivo(s) já estão em {target_format.upper()} e serão ignorados: {', '.join(same_format_files[:2])}")
            if len(same_format_files) > 2:
                warnings[-1] += f" e mais {len(same_format_files) - 2} arquivo(s)"
        
        if unsupported_files:
            warnings.append(f"{len(unsupported_files)} arquivo(s) não podem ser convertidos e serão ignorados: {', '.join(unsupported_files[:2])}")
            if len(unsupported_files) > 2:
                warnings[-1] += f" e mais {len(unsupported_files) - 2} arquivo(s)"
        
        if warnings:
            return True, "Aviso: " + "; ".join(warnings)
        
        return True, "Configuração válida"
    
    def start_conversion(self, file_paths: List[str], output_dir: str, target_format: str, quality: str = 'Média') -> bool:
        """Inicia o processo de conversão."""
        print(f"DEBUG: start_conversion chamado com {len(file_paths)} arquivos, formato: {target_format}")
        
        if self.is_converting:
            print("DEBUG: Conversão já em andamento")
            return False
        
        # Valida a configuração
        print("DEBUG: Validando configuração...")
        is_valid, message = self.validate_conversion_setup(file_paths, output_dir, target_format)
        if not is_valid:
            print(f"DEBUG: Validação falhou: {message}")
            if self.status_callback:
                self.status_callback(f"Erro: {message}")
            return False
        
        # Limpa trabalhos anteriores e adiciona novos
        print("DEBUG: Limpando jobs anteriores e adicionando novos...")
        self.clear_jobs()
        
        for file_path in file_paths:
            result = self.add_conversion_job(file_path, output_dir, target_format, quality)
            print(f"DEBUG: Adicionando job para {file_path}: {result}")
        
        if not self.jobs:
            print("DEBUG: Nenhum job foi criado")
            if self.status_callback:
                self.status_callback("Nenhum trabalho de conversão foi criado")
            return False
        
        # Inicia a conversão
        print(f"DEBUG: Iniciando conversão com {len(self.jobs)} jobs")
        self.is_converting = True
        self.current_job_index = 0
        
        if self.status_callback:
            self.status_callback(f"Iniciando conversão de {len(self.jobs)} arquivo(s)...")
        
        return True
    
    def process_next_job(self) -> tuple[bool, bool]:  # (success, has_more_jobs)
        """Processa o próximo trabalho na fila usando conversores especializados.
        
        Returns:
            tuple: (sucesso do job atual, há mais jobs para processar)
        """
        print(f"DEBUG: process_next_job chamado. is_converting: {self.is_converting}, current_job_index: {self.current_job_index}, total_jobs: {len(self.jobs)}")
        
        if not self.is_converting or self.current_job_index >= len(self.jobs):
            print("DEBUG: Saindo de process_next_job - não está convertendo ou não há mais jobs")
            return False, False
        
        current_job = self.jobs[self.current_job_index]
        current_job.status = 'processing'
        print(f"DEBUG: Processando job {self.current_job_index + 1}/{len(self.jobs)}: {current_job.input_path}")
        
        # Atualiza status
        if self.status_callback:
            filename = Path(current_job.input_path).name
            self.status_callback(f"Convertendo: {filename} ({self.current_job_index + 1}/{len(self.jobs)})")
        
        try:
            # Detecta o tipo de arquivo
            file_type = self.detect_file_type(current_job.input_path)
            print(f"DEBUG: Tipo de arquivo detectado: {file_type}")
            
            if file_type == 'unknown':
                success = False
                message = f"Tipo de arquivo não suportado: {Path(current_job.input_path).name}"
                print(f"DEBUG: {message}")
            else:
                # Obter o conversor apropriado
                converter = self.get_converter_for_type(file_type)
                print(f"DEBUG: Conversor obtido: {converter}")
                
                if converter is None:
                    success = False
                    message = f"Conversor não encontrado para tipo: {file_type}"
                    print(f"DEBUG: {message}")
                else:
                    # Verificar se o conversor suporta a conversão
                    input_extension = Path(current_job.input_path).suffix.lower().lstrip('.')
                    can_convert = converter.can_convert(input_extension, current_job.target_format)
                    print(f"DEBUG: Verificando se pode converter {input_extension} → {current_job.target_format}: {can_convert}")
                    
                    if not can_convert:
                        success = False
                        message = f"Conversão {input_extension} → {current_job.target_format} não suportada pelo conversor {file_type}"
                        print(f"DEBUG: {message}")
                    else:
                        # Executar a conversão usando o conversor especializado
                        print(f"DEBUG: Iniciando conversão real com conversor {file_type}")
                        
                        def progress_update(progress, status):
                            if self.progress_callback:
                                # Calcular progresso geral considerando o job atual
                                job_weight = 100 / len(self.jobs)
                                overall_progress = int((self.current_job_index * job_weight) + (progress * job_weight / 100))
                                self.progress_callback(overall_progress, status)
                        
                        success, message = converter.convert(
                            input_path=current_job.input_path,
                            output_path=current_job.output_path,
                            target_format=current_job.target_format,
                            quality=current_job.quality,
                            progress_callback=progress_update
                        )
                        print(f"DEBUG: Resultado da conversão: success={success}, message={message}")
        
        except Exception as e:
            success = False
            message = f"Erro durante a conversão: {str(e)}"
            print(f"DEBUG: Exceção capturada: {e}")
        
        # Atualiza o status do job
        if success:
            current_job.status = 'completed'
            current_job.progress = 100
        else:
            current_job.status = 'failed'
            current_job.error_message = message
        
        # Atualiza progresso geral final para este job
        overall_progress = int(((self.current_job_index + 1) / len(self.jobs)) * 100)
        if self.progress_callback:
            self.progress_callback(overall_progress, message)
        
        # Move para o próximo job
        self.current_job_index += 1
        has_more_jobs = self.current_job_index < len(self.jobs)
        
        if not has_more_jobs:
            self.finish_conversion()
        
        return success, has_more_jobs
    
    def finish_conversion(self):
        """Finaliza o processo de conversão."""
        self.is_converting = False
        
        # Conta sucessos e falhas
        completed = len([j for j in self.jobs if j.status == 'completed'])
        failed = len([j for j in self.jobs if j.status == 'failed'])
        
        if self.status_callback:
            if failed == 0:
                self.status_callback(f"Conversão concluída! {completed} arquivo(s) convertido(s) com sucesso.")
            else:
                self.status_callback(f"Conversão finalizada: {completed} sucesso(s), {failed} falha(s).")
        
        if self.progress_callback:
            self.progress_callback(100, "Conversão finalizada")
    
    def stop_conversion(self):
        """Para a conversão atual."""
        if self.is_converting:
            self.is_converting = False
            if self.status_callback:
                self.status_callback("Conversão interrompida pelo usuário")
            if self.progress_callback:
                self.progress_callback(0, "Conversão parada")
    
    def get_conversion_summary(self) -> Dict:
        """Retorna um resumo da conversão."""
        total = len(self.jobs)
        completed = len([j for j in self.jobs if j.status == 'completed'])
        failed = len([j for j in self.jobs if j.status == 'failed'])
        pending = len([j for j in self.jobs if j.status == 'pending'])
        processing = len([j for j in self.jobs if j.status == 'processing'])
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'processing': processing,
            'is_converting': self.is_converting
        }
    
    def get_system_status(self) -> Dict:
        """Retorna o status dos conversores e engines do sistema."""
        return {
            'converters': {
                'video': {
                    'available': self.video_converter.is_available(),
                    'engine_status': self.video_converter.get_engine_status(),
                    'supported_formats': {
                        'input': len(self.video_converter.get_supported_input_formats()),
                        'output': len(self.video_converter.get_supported_output_formats())
                    }
                },
                'audio': {
                    'available': self.audio_converter.is_available(),
                    'engine_status': self.audio_converter.get_engine_status(),
                    'supported_formats': {
                        'input': len(self.audio_converter.get_supported_input_formats()),
                        'output': len(self.audio_converter.get_supported_output_formats())
                    }
                },
                'image': {
                    'available': self.image_converter.is_available(),
                    'supported_formats': {
                        'input': len(self.image_converter.get_supported_input_formats()),
                        'output': len(self.image_converter.get_supported_output_formats())
                    }
                },
                'document': {
                    'available': self.document_converter.is_available(),
                    'engines_status': self.document_converter.get_engines_status(),
                    'supported_formats': {
                        'input': len(self.document_converter.get_supported_input_formats()),
                        'output': len(self.document_converter.get_supported_output_formats())
                    }
                }
            },
            'total_supported_conversions': sum([
                len(category['input']) * len(category['output']) 
                for category in self.get_supported_formats().values()
            ])
        }
    
    def test_all_converters(self) -> Dict:
        """Testa todos os conversores e retorna um relatório."""
        results = {
            'video': self.video_converter.test_conversion_capability(),
            'audio': self.audio_converter.test_conversion_capability(),
            'image': self.image_converter.test_conversion_capability(),
            'document': self.document_converter.test_conversion_capability()
        }
        
        # Resumo geral
        working_converters = sum(1 for result in results.values() if result.get('available', False))
        total_converters = len(results)
        
        results['summary'] = {
            'working_converters': working_converters,
            'total_converters': total_converters,
            'system_ready': working_converters > 0,
            'all_converters_working': working_converters == total_converters
        }
        
        return results