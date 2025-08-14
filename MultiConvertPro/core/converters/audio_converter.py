#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Conversor de Áudio

Este módulo contém a classe AudioConverter que gerencia
conversões de arquivos de áudio usando FFmpeg.

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

import os
from typing import Optional, Callable
from pathlib import Path

from ..engines.ffmpeg_engine import run_ffmpeg_conversion, get_file_info, is_ffmpeg_available


class AudioConverter:
    """Conversor especializado para arquivos de áudio."""
    
    def __init__(self):
        self.supported_formats = {
            'input': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'opus', 'aiff', 'au'],
            'output': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'opus']
        }
        
        # Presets de qualidade específicos para áudio
        self.quality_presets = {
            'baixa': {
                'bitrate': '64k',
                'sample_rate': '22050',
                'channels': '1'  # mono
            },
            'media': {
                'bitrate': '128k',
                'sample_rate': '44100',
                'channels': '2'  # stereo
            },
            'alta': {
                'bitrate': '192k',
                'sample_rate': '44100',
                'channels': '2'
            },
            'maxima': {
                'bitrate': '320k',
                'sample_rate': '48000',
                'channels': '2'
            }
        }
        
        # Configurações específicas por formato
        self.format_configs = {
            'mp3': {'codec': 'libmp3lame', 'extension': 'mp3'},
            'wav': {'codec': 'pcm_s16le', 'extension': 'wav'},
            'flac': {'codec': 'flac', 'extension': 'flac'},
            'aac': {'codec': 'aac', 'extension': 'aac'},
            'ogg': {'codec': 'libvorbis', 'extension': 'ogg'},
            'm4a': {'codec': 'aac', 'extension': 'm4a'},
            'opus': {'codec': 'libopus', 'extension': 'opus'}
        }
    
    def is_available(self) -> bool:
        """Verifica se o conversor de áudio está disponível (FFmpeg instalado)."""
        return is_ffmpeg_available()
    
    def is_supported_input(self, file_path: str) -> bool:
        """Verifica se o formato de entrada é suportado."""
        extension = Path(file_path).suffix.lower().lstrip('.')
        return extension in self.supported_formats['input']
    
    def is_supported_output(self, format_name: str) -> bool:
        """Verifica se o formato de saída é suportado."""
        return format_name.lower() in self.supported_formats['output']
    
    def get_supported_input_formats(self) -> list:
        """Retorna lista de formatos de entrada suportados."""
        return self.supported_formats['input']
    
    def get_supported_output_formats(self) -> list:
        """Retorna lista de formatos de saída suportados."""
        return self.supported_formats['output']
    
    def get_engine_status(self) -> dict:
        """Retorna o status do engine de conversão."""
        return {
            'available': self.is_available(),
            'engine': 'FFmpeg',
            'version': 'Unknown'
        }
    
    def get_file_info(self, file_path: str) -> dict:
        """Obtém informações detalhadas do arquivo de áudio."""
        try:
            return get_file_info(file_path)
        except Exception as e:
            return {
                'error': f'Erro ao obter informações: {str(e)}',
                'duration': 0,
                'bitrate': 'unknown',
                'sample_rate': 'unknown',
                'channels': 'unknown'
            }
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """Converte um arquivo de áudio.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            target_format: Formato de saída (mp3, wav, etc.)
            quality: Preset de qualidade (baixa, media, alta, maxima)
            progress_callback: Callback para progresso
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Validar entrada
            if not self.is_supported_input(input_path):
                return False, f"Formato de entrada não suportado: {Path(input_path).suffix}"
            
            if not self.is_supported_output(target_format):
                return False, f"Formato de saída não suportado: {target_format}"
            
            if not os.path.exists(input_path):
                return False, f"Arquivo não encontrado: {input_path}"
            
            # Obter preset de qualidade
            preset = self.quality_presets.get(quality, self.quality_presets['media'])
            
            # Obter configuração do formato
            format_config = self.format_configs.get(target_format, {})
            
            # Preparar parâmetros específicos para áudio
            extra_params = {
                'audio_bitrate': preset['bitrate'],
                'sample_rate': preset['sample_rate'],
                'channels': preset['channels']
            }
            
            # Adicionar codec específico se disponível
            if 'codec' in format_config:
                extra_params['audio_codec'] = format_config['codec']
            
            # Executar conversão
            success, message = run_ffmpeg_conversion(
                input_path=input_path,
                output_path=output_path,
                target_format=target_format,
                quality=quality,
                progress_callback=progress_callback,
                **extra_params
            )
            
            return success, message
            
        except Exception as e:
            error_msg = f"Erro na conversão de áudio: {str(e)}"
            return False, error_msg
    
    def extract_audio_from_video(self, video_path: str, output_path: str, target_format: str = 'mp3') -> tuple[bool, str]:
        """Extrai áudio de um arquivo de vídeo."""
        try:
            # Verificar se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                return False, f"Arquivo de vídeo não encontrado: {video_path}"
            
            # Preparar parâmetros para extração de áudio
            extra_params = {
                'extract_audio_only': True,
                'audio_codec': self.format_configs.get(target_format, {}).get('codec', 'libmp3lame')
            }
            
            # Executar extração
            success, message = run_ffmpeg_conversion(
                input_path=video_path,
                output_path=output_path,
                target_format=target_format,
                quality='media',
                **extra_params
            )
            
            return success, message
            
        except Exception as e:
            error_msg = f"Erro na extração de áudio: {str(e)}"
            return False, error_msg
    
    def normalize_audio(self, input_path: str, output_path: str) -> tuple[bool, str]:
        """Normaliza o volume do áudio."""
        try:
            extra_params = {
                'normalize_audio': True,
                'audio_filter': 'loudnorm'
            }
            
            # Manter o mesmo formato
            input_format = Path(input_path).suffix.lower().lstrip('.')
            
            success, message = run_ffmpeg_conversion(
                input_path=input_path,
                output_path=output_path,
                target_format=input_format,
                quality='alta',
                **extra_params
            )
            
            return success, message
            
        except Exception as e:
            error_msg = f"Erro na normalização de áudio: {str(e)}"
            return False, error_msg
    
    def get_recommended_settings(self, input_path: str, target_format: str) -> dict:
        """Retorna configurações recomendadas baseadas no arquivo de entrada."""
        try:
            info = self.get_file_info(input_path)
            
            # Configurações padrão
            settings = {
                'quality': 'media',
                'preserve_metadata': True
            }
            
            # Ajustar qualidade baseada no bitrate original
            if 'bit_rate' in info:
                try:
                    original_bitrate = int(info['bit_rate'])
                    if original_bitrate >= 256000:  # 256 kbps
                        settings['quality'] = 'maxima'
                    elif original_bitrate >= 192000:  # 192 kbps
                        settings['quality'] = 'alta'
                    elif original_bitrate <= 96000:  # 96 kbps
                        settings['quality'] = 'baixa'
                except (ValueError, TypeError):
                    pass
            
            # Recomendações específicas por formato
            format_recommendations = {
                'mp3': {'lossy': True, 'good_for': 'general'},
                'flac': {'lossy': False, 'good_for': 'archival'},
                'aac': {'lossy': True, 'good_for': 'mobile'},
                'opus': {'lossy': True, 'good_for': 'streaming'}
            }
            
            if target_format in format_recommendations:
                settings.update(format_recommendations[target_format])
            
            return settings
            
        except Exception:
            # Retornar configurações padrão em caso de erro
            return {
                'quality': 'media',
                'preserve_metadata': True
            }