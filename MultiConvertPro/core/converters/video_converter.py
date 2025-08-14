#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Conversor de Vídeo

Este módulo contém a classe VideoConverter que gerencia
conversões de arquivos de vídeo usando FFmpeg.

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

import os
from typing import Optional, Callable
from pathlib import Path

from ..engines.ffmpeg_engine import run_ffmpeg_conversion, get_file_info, is_ffmpeg_available


class VideoConverter:
    """Conversor especializado para arquivos de vídeo."""
    
    def __init__(self):
        self.supported_formats = {
            'input': ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp', 'ogv'],
            'output': ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']
        }
        
        # Presets de qualidade específicos para vídeo
        self.quality_presets = {
            'baixa': {
                'video_bitrate': '500k',
                'audio_bitrate': '64k',
                'resolution': '480p',
                'fps': '24'
            },
            'media': {
                'video_bitrate': '1500k',
                'audio_bitrate': '128k',
                'resolution': '720p',
                'fps': '30'
            },
            'alta': {
                'video_bitrate': '3000k',
                'audio_bitrate': '192k',
                'resolution': '1080p',
                'fps': '30'
            },
            'maxima': {
                'video_bitrate': '8000k',
                'audio_bitrate': '320k',
                'resolution': 'original',
                'fps': 'original'
            }
        }
    
    def is_available(self) -> bool:
        """Verifica se o conversor de vídeo está disponível (FFmpeg instalado)."""
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
        """Obtém informações detalhadas do arquivo de vídeo."""
        try:
            return get_file_info(file_path)
        except Exception as e:
            return {
                'error': f'Erro ao obter informações: {str(e)}',
                'duration': 0,
                'video_codec': 'unknown',
                'audio_codec': 'unknown',
                'resolution': 'unknown'
            }
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """Converte um arquivo de vídeo.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            target_format: Formato de saída (mp4, avi, etc.)
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
            
            # Preparar parâmetros específicos para vídeo
            extra_params = {
                'video_bitrate': preset['video_bitrate'],
                'audio_bitrate': preset['audio_bitrate']
            }
            
            # Adicionar resolução se especificada
            if preset['resolution'] != 'original':
                extra_params['resolution'] = preset['resolution']
            
            # Adicionar FPS se especificado
            if preset['fps'] != 'original':
                extra_params['fps'] = preset['fps']
            
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
            error_msg = f"Erro na conversão de vídeo: {str(e)}"
            return False, error_msg
    
    def get_recommended_settings(self, input_path: str, target_format: str) -> dict:
        """Retorna configurações recomendadas baseadas no arquivo de entrada."""
        try:
            info = self.get_file_info(input_path)
            
            # Configurações padrão
            settings = {
                'quality': 'media',
                'preserve_audio': True,
                'preserve_subtitles': True
            }
            
            # Ajustar qualidade baseada na resolução original
            if 'width' in info and 'height' in info:
                width = info.get('width', 0)
                height = info.get('height', 0)
                
                if width >= 1920 or height >= 1080:
                    settings['quality'] = 'alta'
                elif width <= 640 or height <= 480:
                    settings['quality'] = 'baixa'
            
            # Recomendações específicas por formato
            format_recommendations = {
                'mp4': {'codec': 'h264', 'container': 'mp4'},
                'webm': {'codec': 'vp9', 'container': 'webm'},
                'avi': {'codec': 'xvid', 'container': 'avi'}
            }
            
            if target_format in format_recommendations:
                settings.update(format_recommendations[target_format])
            
            return settings
            
        except Exception:
            # Retornar configurações padrão em caso de erro
            return {
                'quality': 'media',
                'preserve_audio': True,
                'preserve_subtitles': False
            }