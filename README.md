# MultiConvert Pro

![MultiConvert Pro Logo](assets/images/logo.png)

**Um conversor universal de arquivos para Windows - Áudio, Vídeo, Imagem e Documentos**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)](https://pyside.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010/11-lightgrey.svg)]()

## 🚀 Características Principais

- ✅ **Conversão Universal** - Suporte a 20+ formatos de áudio, vídeo, imagem e documentos
- ✅ **Interface Intuitiva** - Design moderno e fácil de usar
- ✅ **Conversão em Lote** - Processe múltiplos arquivos simultaneamente
- ✅ **Totalmente Offline** - Funciona sem conexão com a internet
- ✅ **Alta Qualidade** - Powered by FFmpeg para conversões de mídia
- ✅ **Drag & Drop** - Arraste arquivos diretamente para o aplicativo
- ✅ **Presets de Qualidade** - Configurações otimizadas para diferentes usos

## 📥 Instalação

### Opção 1: Instalador (Recomendado)
1. Baixe o instalador mais recente da [página de releases](https://github.com/seu-usuario/multiconvert-pro/releases)
2. Execute `MultiConvertPro-Setup.exe`
3. Siga as instruções do assistente de instalação

### Opção 2: Versão Portable
1. Baixe `MultiConvertPro-Portable.zip`
2. Extraia para uma pasta de sua escolha
3. Execute `MultiConvertPro.exe`

### Opção 3: Executar do Código Fonte
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/multiconvert-pro.git
cd multiconvert-pro

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python main.py
```

## 🎯 Formatos Suportados

### 🎵 Áudio
**Entrada:** MP3, WAV, AAC, FLAC, OGG, OPUS, M4A, WMA  
**Saída:** MP3, WAV, AAC, FLAC, OGG, OPUS

### 🎬 Vídeo
**Entrada:** MP4, MKV, AVI, MOV, WEBM, FLV, WMV, 3GP  
**Saída:** MP4, MKV, AVI, MOV, WEBM

### 🖼️ Imagem
**Entrada:** JPEG, PNG, GIF, BMP, TIFF, WEBP, ICO, SVG  
**Saída:** JPEG, PNG, GIF, BMP, TIFF, WEBP

### 📄 Documentos
**Entrada:** PDF, DOC, DOCX, TXT, ODT, RTF  
**Saída:** PDF, DOC, DOCX, TXT, ODT, RTF

## 🖥️ Capturas de Tela

### Tela Principal
![Tela Principal](screenshots/main-window.png)

### Conversão em Progresso
![Progresso](screenshots/conversion-progress.png)

### Configurações
![Configurações](screenshots/settings.png)

## 🛠️ Requisitos do Sistema

### Mínimos
- **SO:** Windows 10 (64-bit)
- **RAM:** 4 GB
- **Espaço:** 500 MB livres
- **Processador:** Intel Core i3 ou AMD equivalente

### Recomendados
- **SO:** Windows 11 (64-bit)
- **RAM:** 8 GB
- **Espaço:** 1 GB livres
- **Processador:** Intel Core i5 ou AMD equivalente
- **Armazenamento:** SSD para melhor performance

## 📖 Como Usar

### Conversão Simples
1. **Abra o MultiConvert Pro**
2. **Arraste seus arquivos** para a área central ou clique em "Adicionar Arquivos"
3. **Selecione o formato de saída** no dropdown
4. **Escolha a qualidade** (Alta/Média/Baixa)
5. **Clique em "Converter"**

### Conversão em Lote
1. **Adicione múltiplos arquivos** de uma vez
2. **Configure o formato de saída** para todos
3. **Defina a pasta de destino** (opcional)
4. **Inicie a conversão** e acompanhe o progresso

### Configurações Avançadas
- **Presets personalizados** para diferentes cenários
- **Configurações de codec** para usuários avançados
- **Nomenclatura automática** de arquivos convertidos
- **Preservação de metadados** quando possível

## ⚙️ Configuração de Desenvolvimento

### Pré-requisitos
- Python 3.12 ou superior
- Git
- FFmpeg (incluído no projeto)

### Setup do Ambiente
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/multiconvert-pro.git
cd multiconvert-pro

# Crie um ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# Execute os testes
pytest tests/

# Execute o aplicativo em modo de desenvolvimento
python main.py --debug
```

### Estrutura do Código
```
MultiConvertPro/
├── core/           # Lógica de conversão
├── ui/             # Interface gráfica
├── utils/          # Utilitários
├── tests/          # Testes automatizados
├── assets/         # Recursos (ícones, imagens)
└── installer/      # Scripts de empacotamento
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=core --cov=ui

# Testes específicos
pytest tests/test_audio_converter.py
```

## 📦 Build e Distribuição

### Gerar Executável
```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar executável
pyinstaller --onefile --windowed main.py
```

### Criar Instalador
```bash
# Usar Inno Setup (Windows)
# Compilar installer/setup.iss
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nosso [Guia de Contribuição](CONTRIBUTING.md) antes de submeter pull requests.

### Como Contribuir
1. **Fork** o projeto
2. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra um Pull Request**

### Áreas que Precisam de Ajuda
- 🌐 Traduções para outros idiomas
- 🎨 Melhorias na interface
- 🔧 Novos formatos de arquivo
- 📚 Documentação
- 🐛 Correção de bugs

## 📋 Roadmap

### v1.0.0 (Atual)
- [x] Conversão básica de áudio/vídeo
- [x] Interface principal
- [x] Conversão em lote
- [ ] Instalador Windows

### v1.1.0
- [ ] Suporte a mais formatos de documento
- [ ] Presets avançados
- [ ] Tema escuro
- [ ] Configurações de proxy

### v1.2.0
- [ ] Plugins para formatos especializados
- [ ] API para automação
- [ ] Integração com serviços em nuvem

### v2.0.0
- [ ] Suporte para macOS
- [ ] Suporte para Linux
- [ ] Interface web

## 🐛 Problemas Conhecidos

- Conversão de vídeos 4K pode ser lenta em sistemas com pouca RAM
- Alguns formatos de documento podem perder formatação complexa
- FFmpeg pode não estar disponível em algumas configurações corporativas

## 📞 Suporte

### Obtendo Ajuda
- 📖 [Documentação Completa](docs/)
- ❓ [FAQ](docs/FAQ.md)
- 🐛 [Reportar Bug](https://github.com/seu-usuario/multiconvert-pro/issues)
- 💡 [Solicitar Feature](https://github.com/seu-usuario/multiconvert-pro/issues)

### Comunidade
- 💬 [Discord](https://discord.gg/multiconvert-pro)
- 📧 Email: suporte@multiconvertpro.com
- 🐦 Twitter: [@MultiConvertPro](https://twitter.com/multiconvertpro)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **FFmpeg Team** - Pelo excelente motor de conversão
- **Qt/PySide Team** - Pela framework de interface
- **Python Community** - Pelas bibliotecas incríveis
- **Contribuidores** - Por tornarem este projeto melhor

## 📊 Estatísticas

![GitHub stars](https://img.shields.io/github/stars/seu-usuario/multiconvert-pro?style=social)
![GitHub forks](https://img.shields.io/github/forks/seu-usuario/multiconvert-pro?style=social)
![GitHub issues](https://img.shields.io/github/issues/seu-usuario/multiconvert-pro)
![GitHub downloads](https://img.shields.io/github/downloads/seu-usuario/multiconvert-pro/total)

---

**MultiConvert Pro** - Convertendo arquivos com simplicidade e qualidade.

*Feito com ❤️ para a comunidade*