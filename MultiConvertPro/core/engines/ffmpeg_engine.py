import subprocess
import os
from pathlib import Path

def run_ffmpeg_conversion(input_path, output_path, quality_preset='medium', format_type='video'):
    """
    Executa a conversão usando FFmpeg.
    
    Args:
        input_path (str): Caminho do arquivo de entrada
        output_path (str): Caminho do arquivo de saída
        quality_preset (str): Preset de qualidade ('Alta', 'Média', 'Baixa')
        format_type (str): Tipo de formato ('video', 'audio', 'image')
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Caminho para o executável do FFmpeg
    ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bin', 'ffmpeg.exe')
    
    # Verifica se o FFmpeg existe
    if not os.path.exists(ffmpeg_path):
        return False, f"FFmpeg não encontrado em: {ffmpeg_path}"
    
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(input_path):
        return False, f"Arquivo de entrada não encontrado: {input_path}"
    
    # Cria o diretório de saída se não existir
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Mapeia presets de qualidade para parâmetros do FFmpeg
    quality_map = {
        'Alta': '18',
        'Média': '23',  # Valor padrão
        'Baixa': '28'
    }
    crf_value = quality_map.get(quality_preset, '23')
    
    # Monta o comando baseado no tipo de formato
    command = [ffmpeg_path, '-i', input_path]
    
    if format_type == 'video':
        # Configurações para vídeo
        command.extend([
            '-c:v', 'libx264',  # Codec de vídeo
            '-crf', crf_value,  # Fator de qualidade
            '-c:a', 'aac',      # Codec de áudio
            '-b:a', '128k'      # Bitrate do áudio
        ])
    elif format_type == 'audio':
        # Configurações para áudio
        command.extend([
            '-c:a', 'libmp3lame',  # Codec de áudio MP3
            '-b:a', '192k'         # Bitrate do áudio
        ])
    elif format_type == 'image':
        # Configurações para imagem
        command.extend([
            '-q:v', '2'  # Qualidade para imagens
        ])
    
    # Adiciona opções finais
    command.extend([
        '-y',        # Sobrescreve o arquivo de saída se existir
        output_path  # Arquivo de saída
    ])
    
    try:
        # Executa o comando e aguarda a conclusão
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=300  # Timeout de 5 minutos
        )
        
        # Verifica se o arquivo de saída foi criado
        if os.path.exists(output_path):
            return True, "Conversão concluída com sucesso!"
        else:
            return False, "Arquivo de saída não foi criado"
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Erro ao converter com FFmpeg: {e.stderr if e.stderr else str(e)}"
        return False, error_msg
        
    except subprocess.TimeoutExpired:
        return False, "Conversão cancelada por timeout (5 minutos)"
        
    except FileNotFoundError:
        return False, f"Executável do FFmpeg não encontrado: {ffmpeg_path}"
        
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"

def get_file_info(file_path):
    """
    Obtém informações sobre um arquivo de mídia usando FFprobe.
    
    Args:
        file_path (str): Caminho do arquivo
    
    Returns:
        dict: Informações do arquivo ou None se houver erro
    """
    ffprobe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bin', 'ffprobe.exe')
    
    if not os.path.exists(ffprobe_path):
        return None
    
    command = [
        ffprobe_path,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        import json
        return json.loads(result.stdout)
    except:
        return None

def detect_format_type(file_path):
    """
    Detecta o tipo de formato do arquivo (video, audio, image).
    
    Args:
        file_path (str): Caminho do arquivo
    
    Returns:
        str: Tipo do formato ('video', 'audio', 'image', 'unknown')
    """
    file_info = get_file_info(file_path)
    
    if not file_info or 'streams' not in file_info:
        # Fallback baseado na extensão
        ext = Path(file_path).suffix.lower()
        video_exts = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        if ext in video_exts:
            return 'video'
        elif ext in audio_exts:
            return 'audio'
        elif ext in image_exts:
            return 'image'
        else:
            return 'unknown'
    
    # Analisa os streams
    has_video = False
    has_audio = False
    
    for stream in file_info['streams']:
        codec_type = stream.get('codec_type', '')
        if codec_type == 'video':
            has_video = True
        elif codec_type == 'audio':
            has_audio = True
    
    if has_video:
        return 'video'
    elif has_audio:
        return 'audio'
    else:
        return 'image'

def is_ffmpeg_available() -> bool:
    """Verifica se o FFmpeg está disponível no sistema."""
    # Caminho para o executável do FFmpeg
    ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bin', 'ffmpeg.exe')
    
    # Verifica se o FFmpeg existe no diretório bin
    if os.path.exists(ffmpeg_path):
        return True
    
    # Verifica se o FFmpeg está no PATH do sistema
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False