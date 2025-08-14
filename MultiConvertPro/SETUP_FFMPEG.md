# 🚀 Configuração do FFmpeg para MultiConvert Pro

## ⚠️ IMPORTANTE
Para que o MultiConvert Pro funcione corretamente, você precisa instalar o FFmpeg. Sem ele, as conversões não funcionarão.

## 📥 Download e Instalação

### Opção 1: Download Direto (Recomendado)

1. **Acesse o site oficial:**
   - Vá para: https://www.gyan.dev/ffmpeg/builds/
   - Ou: https://ffmpeg.org/download.html#build-windows

2. **Baixe a versão correta:**
   - Clique em "release builds"
   - Baixe o arquivo "ffmpeg-release-essentials.zip"

3. **Extraia os arquivos:**
   - Extraia o arquivo ZIP baixado
   - Navegue até a pasta `bin/` dentro do arquivo extraído
   - Você verá os arquivos: `ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe`

4. **Copie para o MultiConvert Pro:**
   - Copie `ffmpeg.exe` e `ffprobe.exe` para a pasta `bin/` do MultiConvert Pro
   - Caminho: `MultiConvertPro/bin/`

### Opção 2: Via Chocolatey

```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar FFmpeg
choco install ffmpeg

# Copiar arquivos
copy "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe" "caminho\para\MultiConvertPro\bin\"
copy "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffprobe.exe" "caminho\para\MultiConvertPro\bin\"
```

### Opção 3: Via Winget

```powershell
# Instalar FFmpeg
winget install Gyan.FFmpeg

# Localizar e copiar os arquivos para a pasta bin/ do MultiConvert Pro
```

## ✅ Verificação da Instalação

Após copiar os arquivos, sua pasta `bin/` deve conter:

```
MultiConvertPro/
├── bin/
│   ├── ffmpeg.exe     ✅
│   ├── ffprobe.exe    ✅
│   └── README.md
├── core/
├── ui/
└── ...
```

## 🧪 Teste

1. **Abra o MultiConvert Pro**
2. **Adicione um arquivo de teste** (qualquer vídeo, áudio ou imagem)
3. **Selecione um formato de saída**
4. **Clique em "🚀 Iniciar Conversão"**

Se tudo estiver correto, você verá:
- ✅ "Conversão iniciada" na barra de status
- ✅ Progresso sendo exibido
- ✅ "Conversão concluída!" ao final

Se houver erro:
- ❌ "FFmpeg não encontrado" - Verifique se os arquivos estão na pasta `bin/`
- ❌ "Erro na conversão" - Verifique se o arquivo de entrada é válido

## 🔧 Solução de Problemas

### Erro: "FFmpeg não encontrado"
- Verifique se `ffmpeg.exe` está em `MultiConvertPro/bin/`
- Verifique se o arquivo não está corrompido
- Tente baixar novamente do site oficial

### Erro: "Conversão falhou"
- Verifique se o arquivo de entrada não está corrompido
- Tente com um arquivo diferente
- Verifique se há espaço suficiente no disco

### Erro: "Pasta de destino não encontrada"
- Selecione uma pasta de destino válida
- Verifique se você tem permissão de escrita na pasta

## 📞 Suporte

Se ainda tiver problemas:
1. Verifique se todos os arquivos estão nas pastas corretas
2. Teste com um arquivo pequeno primeiro
3. Verifique as mensagens de erro na barra de status

---

**🎉 Após a instalação, o MultiConvert Pro estará pronto para converter seus arquivos!**