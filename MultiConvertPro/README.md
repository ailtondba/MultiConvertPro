#  MultiConvert Pro - Conversor Universal de Arquivos

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-6.9.1-green.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
</div>

##  Sobre o Projeto

O **MultiConvert Pro** é um conversor universal de arquivos desenvolvido com tecnologias modernas em Python. O sistema oferece uma solução completa para conversão de múltiplos formatos de arquivo com interface gráfica intuitiva e engines de conversão profissionais.

##  Características Principais

-  **Interface Moderna**: Design intuitivo com PySide6 (Qt)
-  **Performance**: Conversões otimizadas e processamento em lote
-  **Engines Múltiplas**: FFmpeg, LibreOffice, OnlyOffice e Pillow
-  **Suporte Amplo**: Imagens, vídeos, áudios e documentos
-  **Arquitetura Modular**: Sistema extensível e personalizável
-  **Validação**: Verificação automática de formatos e integridade

##  Funcionalidades

###  Conversão de Imagens
- Formatos suportados: JPG, PNG, BMP, GIF, TIFF, WebP
- Redimensionamento e otimização
- Conversão em lote
- Preservação de metadados

###  Conversão de Vídeos
- Formatos suportados: MP4, AVI, MOV, MKV, WebM
- Compressão e otimização
- Extração de áudio
- Configurações avançadas de codec

###  Conversão de Áudios
- Formatos suportados: MP3, WAV, FLAC, AAC, OGG
- Ajuste de qualidade e bitrate
- Normalização de volume
- Edição de metadados

###  Conversão de Documentos
- Formatos suportados: PDF, DOCX, ODT, RTF, TXT
- Preservação de formatação
- Conversão de planilhas (XLSX, ODS)
- Apresentações (PPTX, ODP)

##  Tecnologias Utilizadas

### Frontend
- **PySide6**: Framework Qt para interface gráfica moderna
- **Qt Designer**: Design de interfaces visuais
- **Custom Widgets**: Componentes personalizados

### Backend
- **Python 3.8+**: Linguagem principal
- **FFmpeg**: Engine para conversão de mídia
- **Pillow**: Processamento de imagens
- **LibreOffice**: Conversão de documentos
- **OnlyOffice**: Engine alternativa para documentos

### Bibliotecas Principais
- **filetype**: Detecção automática de tipos de arquivo
- **PyPDF2**: Manipulação de arquivos PDF
- **python-docx**: Processamento de documentos Word
- **openpyxl**: Manipulação de planilhas Excel
- **psutil**: Monitoramento de sistema

##  Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- FFmpeg (para conversão de mídia)

### Instalação do Código Fonte

```bash
# Clone o repositório
git clone https://github.com/ailtondba/MultiConvertPro.git

# Entre no diretório
cd MultiConvertPro

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py
```

### Configuração do FFmpeg

Para conversão de mídia, é necessário instalar o FFmpeg:

**Windows:**
```bash
# Baixe o FFmpeg do site oficial
# Extraia e adicione ao PATH do sistema
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

##  Como Usar

### Primeira Execução
1. Execute `python main.py`
2. A interface gráfica será carregada
3. Selecione os arquivos para conversão
4. Escolha o formato de destino
5. Configure as opções avançadas (opcional)
6. Inicie a conversão

### Conversão em Lote
1. Selecione múltiplos arquivos
2. Defina o formato de saída
3. Configure a pasta de destino
4. Execute a conversão em lote

### Configurações Avançadas
- Qualidade de compressão
- Resolução de saída
- Codec específico
- Metadados personalizados

##  Estrutura do Projeto

```
MultiConvertPro/
 main.py                 # Ponto de entrada principal
 requirements.txt        # Dependências do projeto
 core/                   # Núcleo da aplicação
    converters/        # Conversores específicos
       audio_converter.py
       document_converter.py
       image_converter.py
       video_converter.py
       main_converter.py
    engines/           # Engines de conversão
       ffmpeg_engine.py
       libreoffice_engine.py
       onlyoffice_engine.py
       fallback_engine.py
    validators/        # Validadores de arquivo
 ui/                    # Interface do usuário
    windows/          # Janelas principais
    widgets/          # Widgets personalizados
    dialogs/          # Diálogos e modais
 assets/               # Recursos visuais
    icons/           # Ícones da aplicação
    images/          # Imagens e logos
    themes/          # Temas visuais
 utils/                # Utilitários gerais
 tests/                # Testes automatizados
 docs/                 # Documentação
 translations/         # Arquivos de tradução
 installer/            # Scripts de instalação
```

##  Scripts Disponíveis

```bash
# Executar aplicação
python main.py

# Executar testes
python -m pytest tests/

# Gerar executável
pyinstaller --onefile main.py

# Verificar dependências
pip check

# Atualizar dependências
pip install -r requirements.txt --upgrade
```

##  Contribuindo

Contribuições são sempre bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição
- Siga o padrão PEP 8 para código Python
- Adicione testes para novas funcionalidades
- Documente mudanças no README
- Use commits semânticos

##  Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

##  Autor

**Criado por ailtondba**

-  GitHub: [@ailtondba](https://github.com/ailtondba)
-  Email: ailtonazure@gmail.com
-  Website: [MultiConvert Pro](https://github.com/ailtondba/MultiConvertPro)

##  Suporte

Se você encontrar algum problema ou tiver dúvidas:

-  [Reporte um bug](https://github.com/ailtondba/MultiConvertPro/issues)
-  [Solicite uma feature](https://github.com/ailtondba/MultiConvertPro/issues)
-  Entre em contato: ailtonazure@gmail.com

##  Roadmap

- [ ]  Interface web responsiva
- [ ]  Integração com serviços de nuvem
- [ ]  Conversão em tempo real
- [ ]  Dashboard de estatísticas
- [ ]  Suporte a mais idiomas
- [ ]  Sistema de plugins
- [ ]  Aplicativo mobile
- [ ]  Conversão automática por IA

##  Agradecimentos

Agradecimentos especiais a:

- **FFmpeg Team** - Engine de conversão de mídia
- **Qt/PySide Team** - Framework de interface gráfica
- **Python Community** - Linguagem e ecossistema
- **LibreOffice** - Engine de documentos
- **Pillow Contributors** - Processamento de imagens

---

<div align="center">
  <p><strong>criado por ailtondba</strong></p>
  <p> Se este projeto te ajudou, considere dar uma estrela!</p>
</div>
