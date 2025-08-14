#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiConvert Pro - Conversor de Imagem

Este módulo contém a classe ImageConverter que gerencia
conversões de arquivos de imagem usando Pillow (PIL).

Autor: MultiConvert Pro Team
Versão: 1.0.0
"""

import os
from typing import Optional, Callable, Tuple
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageEnhance, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageOps = None
    ImageEnhance = None
    ExifTags = None


class ImageConverter:
    """Conversor especializado para arquivos de imagem."""
    
    def __init__(self):
        if not PIL_AVAILABLE:
            raise ImportError("Pillow (PIL) não está instalado. Execute: pip install Pillow")
        
        self.supported_formats = {
            'input': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'ppm', 'pgm', 'pbm'],
            'output': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico']
        }
        
        # Presets de qualidade específicos para imagem
        self.quality_presets = {
            'baixa': {
                'quality': 60,
                'optimize': True,
                'max_size': (800, 600)
            },
            'media': {
                'quality': 80,
                'optimize': True,
                'max_size': (1920, 1080)
            },
            'alta': {
                'quality': 90,
                'optimize': False,
                'max_size': (2560, 1440)
            },
            'maxima': {
                'quality': 95,
                'optimize': False,
                'max_size': None  # Sem redimensionamento
            }
        }
        
        # Configurações específicas por formato
        self.format_configs = {
            'jpg': {'mode': 'RGB', 'supports_transparency': False},
            'jpeg': {'mode': 'RGB', 'supports_transparency': False},
            'png': {'mode': 'RGBA', 'supports_transparency': True},
            'gif': {'mode': 'P', 'supports_transparency': True, 'supports_animation': True},
            'bmp': {'mode': 'RGB', 'supports_transparency': False},
            'tiff': {'mode': 'RGBA', 'supports_transparency': True},
            'webp': {'mode': 'RGBA', 'supports_transparency': True, 'supports_animation': True},
            'ico': {'mode': 'RGBA', 'supports_transparency': True}
        }
    
    def is_available(self) -> bool:
        """Verifica se o conversor de imagens está disponível (Pillow instalado)."""
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
    
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
    
    def get_file_info(self, file_path: str) -> dict:
        """Obtém informações detalhadas do arquivo de imagem."""
        try:
            with Image.open(file_path) as img:
                info = {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'size_bytes': os.path.getsize(file_path),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                # Tentar obter informações EXIF
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        info['exif'] = {}
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            info['exif'][tag] = value
                
                return info
                
        except Exception as e:
            return {
                'error': f'Erro ao obter informações: {str(e)}',
                'width': 0,
                'height': 0,
                'mode': 'unknown',
                'format': 'unknown'
            }
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        quality: str = 'media',
        progress_callback: Optional[Callable] = None,
        **kwargs
    ) -> tuple[bool, str]:
        """Converte um arquivo de imagem.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            target_format: Formato de saída (jpg, png, etc.)
            quality: Preset de qualidade (baixa, media, alta, maxima)
            progress_callback: Callback para progresso
            **kwargs: Parâmetros adicionais (resize, rotate, etc.)
            
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
            
            if progress_callback:
                progress_callback(10, "Abrindo imagem...")
            
            # Abrir imagem
            with Image.open(input_path) as img:
                # Corrigir orientação baseada no EXIF
                img = ImageOps.exif_transpose(img)
                
                if progress_callback:
                    progress_callback(30, "Processando imagem...")
                
                # Obter configurações
                preset = self.quality_presets.get(quality, self.quality_presets['media'])
                format_config = self.format_configs.get(target_format, {})
                
                # Converter modo de cor se necessário
                target_mode = format_config.get('mode', 'RGB')
                if img.mode != target_mode:
                    if target_mode == 'RGB' and img.mode in ('RGBA', 'LA'):
                        # Criar fundo branco para formatos sem transparência
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    else:
                        img = img.convert(target_mode)
                
                if progress_callback:
                    progress_callback(50, "Aplicando transformações...")
                
                # Aplicar transformações opcionais
                img = self._apply_transformations(img, kwargs)
                
                # Redimensionar se necessário
                max_size = preset.get('max_size')
                if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                if progress_callback:
                    progress_callback(80, "Salvando arquivo...")
                
                # Preparar parâmetros de salvamento
                save_params = {}
                
                if target_format.lower() in ['jpg', 'jpeg']:
                    save_params['quality'] = preset['quality']
                    save_params['optimize'] = preset['optimize']
                    save_params['progressive'] = True
                elif target_format.lower() == 'png':
                    save_params['optimize'] = preset['optimize']
                elif target_format.lower() == 'webp':
                    save_params['quality'] = preset['quality']
                    save_params['method'] = 6  # Melhor compressão
                
                # Criar diretório de saída se não existir
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Salvar imagem
                # Mapear formatos para PIL
                format_mapping = {
                    'jpg': 'JPEG',
                    'jpeg': 'JPEG',
                    'png': 'PNG',
                    'webp': 'WEBP',
                    'bmp': 'BMP',
                    'tiff': 'TIFF',
                    'gif': 'GIF'
                }
                pil_format = format_mapping.get(target_format.lower(), target_format.upper())
                img.save(output_path, format=pil_format, **save_params)
                
                if progress_callback:
                    progress_callback(100, "Conversão concluída!")
                
                return True, f"Imagem convertida com sucesso para {target_format.upper()}"
                
        except Exception as e:
            error_msg = f"Erro na conversão de imagem: {str(e)}"
            return False, error_msg
    
    def _apply_transformations(self, img: 'Image.Image', params: dict) -> 'Image.Image':
        """Aplica transformações opcionais à imagem."""
        # Rotação
        if 'rotate' in params:
            angle = params['rotate']
            if angle != 0:
                img = img.rotate(angle, expand=True)
        
        # Redimensionamento específico
        if 'resize' in params:
            size = params['resize']
            if isinstance(size, (list, tuple)) and len(size) == 2:
                img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Corte (crop)
        if 'crop' in params:
            box = params['crop']
            if isinstance(box, (list, tuple)) and len(box) == 4:
                img = img.crop(box)
        
        # Espelhamento
        if params.get('flip_horizontal'):
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        if params.get('flip_vertical'):
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        # Ajustes de cor
        if 'brightness' in params:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(params['brightness'])
        
        if 'contrast' in params:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(params['contrast'])
        
        if 'saturation' in params:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(params['saturation'])
        
        return img
    
    def resize_image(self, input_path: str, output_path: str, size: Tuple[int, int], maintain_aspect: bool = True) -> tuple[bool, str]:
        """Redimensiona uma imagem para o tamanho especificado."""
        try:
            with Image.open(input_path) as img:
                if maintain_aspect:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Manter o mesmo formato
                format_name = img.format or Path(input_path).suffix.lower().lstrip('.')
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, format=format_name)
                
                return True, f"Imagem redimensionada para {img.width}x{img.height}"
                
        except Exception as e:
            return False, f"Erro ao redimensionar imagem: {str(e)}"
    
    def create_thumbnail(self, input_path: str, output_path: str, size: Tuple[int, int] = (128, 128)) -> tuple[bool, str]:
        """Cria uma miniatura da imagem."""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Salvar como PNG para preservar qualidade
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, 'PNG', optimize=True)
                
                return True, f"Miniatura criada: {img.width}x{img.height}"
                
        except Exception as e:
            return False, f"Erro ao criar miniatura: {str(e)}"
    
    def get_recommended_settings(self, input_path: str, target_format: str) -> dict:
        """Retorna configurações recomendadas baseadas no arquivo de entrada."""
        try:
            info = self.get_file_info(input_path)
            
            # Configurações padrão
            settings = {
                'quality': 'media',
                'preserve_exif': True
            }
            
            # Ajustar qualidade baseada no tamanho da imagem
            width = info.get('width', 0)
            height = info.get('height', 0)
            
            if width >= 2560 or height >= 1440:
                settings['quality'] = 'alta'
            elif width <= 800 or height <= 600:
                settings['quality'] = 'baixa'
            
            # Recomendações específicas por formato
            format_recommendations = {
                'jpg': {'good_for': 'photos', 'compression': 'lossy'},
                'png': {'good_for': 'graphics', 'compression': 'lossless'},
                'webp': {'good_for': 'web', 'compression': 'both'},
                'gif': {'good_for': 'animation', 'colors': 'limited'}
            }
            
            if target_format in format_recommendations:
                settings.update(format_recommendations[target_format])
            
            # Verificar se há transparência
            if info.get('has_transparency') and target_format in ['jpg', 'jpeg', 'bmp']:
                settings['warning'] = 'Transparência será perdida neste formato'
            
            return settings
            
        except Exception:
            return {
                'quality': 'media',
                'preserve_exif': True
            }