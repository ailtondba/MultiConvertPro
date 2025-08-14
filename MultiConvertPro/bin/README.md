# FFmpeg Setup

Esta pasta deve conter os executáveis do FFmpeg para que o MultiConvert Pro funcione corretamente.

## Arquivos Necessários:
- `ffmpeg.exe` - Conversor principal
- `ffprobe.exe` - Analisador de arquivos de mídia

## Como Instalar:

### Opção 1: Download Direto
1. Acesse: https://www.gyan.dev/ffmpeg/builds/
2. Baixe a versão "release builds" (essentials)
3. Extraia o arquivo ZIP
4. Copie `ffmpeg.exe` e `ffprobe.exe` da pasta `bin/` para esta pasta

### Opção 2: Via Chocolatey (Windows)
```powershell
choco install ffmpeg
```
Depois copie os arquivos de `C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\`

### Opção 3: Via Winget
```powershell
winget install Gyan.FFmpeg
```

## Verificação:
Após a instalação, esta pasta deve conter:
```
bin/
├── ffmpeg.exe
├── ffprobe.exe
└── README.md (este arquivo)
```

## Nota:
Os executáveis do FFmpeg não estão incluídos no repositório devido ao tamanho dos arquivos.
O MultiConvert Pro verificará automaticamente se os arquivos estão presentes antes de iniciar conversões.