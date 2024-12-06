# YouTube Downloader

A modern, user-friendly YouTube media downloader with support for multiple formats and qualities.

## Features

- **Simple Interface**: Clean, intuitive GUI for easy downloads
- **Multiple Format Support**:
  - **Video Formats**:
    - MP4 (High/Medium/Low quality)
    - WebM (High/Medium/Low quality)
    - MKV (High/Medium/Low quality)
  - **Audio Formats**:
    - MP3 (High/Medium/Low quality)
    - AAC (High/Medium/Low quality)
    - Opus (High/Medium/Low quality)
- **Quality Options**:
  - Video:
    - High: Best available quality
    - Medium: 720p
    - Low: 480p
  - Audio:
    - High: Best bitrate (320kbps for MP3)
    - Medium: Medium bitrate (192kbps for MP3)
    - Low: Lower bitrate (128kbps for MP3)
- **Progress Tracking**: Real-time download progress monitoring
- **Custom Save Location**: Choose where to save your downloads
- **Error Handling**: Clear error messages and status updates

## Compatibilidade

### Linux
- **Debian/Ubuntu e derivados**: Suporte completo via pacote .deb
- **Fedora/RHEL e derivados**: Suporte via instalação manual ou script
- **Arch Linux e derivados**: Suporte via instalação manual ou script
- **OpenSUSE**: Suporte via instalação manual ou script
- **Outras distribuições**: Compatível desde que atenda aos requisitos

### macOS
- **macOS 11 (Big Sur) ou superior**: Suporte via instalação manual
- **macOS 10.15 (Catalina) ou anterior**: Não testado, pode funcionar com dependências corretas

### Sistemas Não Suportados
- **iOS/iPadOS**: Não suportado devido às restrições da App Store
- **Android**: Não suportado (sistema móvel)
- **Windows Phone**: Não suportado (descontinuado)

## Requisitos por Sistema

### Linux
- Python 3.12 ou superior
- FFmpeg
- Tkinter (python3-tk)
- Pip (python3-pip)

**Debian/Ubuntu**:
```bash
sudo apt-get update
sudo apt-get install python3 python3-tk python3-pip ffmpeg
```

**Fedora**:
```bash
sudo dnf install python3 python3-tkinter ffmpeg
```

**Arch Linux**:
```bash
sudo pacman -S python python-tkinter ffmpeg
```

**OpenSUSE**:
```bash
sudo zypper install python3 python3-tk python3-pip ffmpeg
```

### macOS
1. Instale o Homebrew (se ainda não tiver):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Instale as dependências:
```bash
brew install python@3.12 ffmpeg
brew install --cask tcl-tk
```

## Installation

### Método 1: Instalação via .deb (Recomendado para Ubuntu/Debian)

1. Clone o repositório e construa o pacote:
```bash
git clone https://github.com/seu-usuario/my-yt-down.git
cd DownTube
sudo ./build_deb.sh
```

2. Instale o pacote gerado:
```bash
sudo dpkg -i my-yt-down.deb
sudo apt-get install -f  # Para resolver dependências se necessário
```

3. Adicione as permissões necessárias:
```bash
sudo chmod +x /usr/local/bin/my-yt-down
sudo chmod +x /usr/lib/my-yt-down/my-yt-down
```

4. Execute o programa:
```bash
my-yt-down
```

### Método 2: Instalação Manual (Outros sistemas Linux)

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/my-yt-down.git
cd my-yt-down
```

2. Crie e ative um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o programa:
```bash
python3 src/gui.py
```

## Resolução de Problemas Comuns

### 1. Erro de Permissão Negada
Se você encontrar o erro "Permissão negada" ao executar `my-yt-down`, tente:

```bash
# Verificar permissões
sudo chmod +x /usr/local/bin/my-yt-down
sudo chmod +x /usr/lib/my-yt-down/my-yt-down

# Se o erro persistir, edite o script de inicialização
sudo nano /usr/local/bin/my-yt-down
```

Conteúdo do script deve ser:
```bash
#!/bin/bash
cd /usr/lib/my-yt-down
/usr/lib/my-yt-down/my-yt-down "$@"
```

### 2. Erro de Módulo Não Encontrado
Se encontrar erros de módulo não encontrado, como "No module named 'customtkinter'":

```bash
# Instale as dependências Python
pip install -r requirements.txt

# Ou instale manualmente
pip install customtkinter
pip install yt-dlp
```

### 3. Erro de URL Inválida
A aplicação suporta os seguintes formatos de URL:
- YouTube: `https://(www.)youtube.com/...`
- YouTube Short: `https://youtu.be/...`
- YouTube Music: `https://(www.)music.youtube.com/...`

### 4. Problemas com FFmpeg
Se encontrar erros relacionados ao FFmpeg:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### 5. Atualizando a Aplicação

Para atualizar a aplicação para a versão mais recente:

1. Atualize o repositório:
```bash
cd my-yt-down
git pull origin main
```

2. Reconstrua e reinstale o pacote:
```bash
sudo ./build_deb.sh
sudo dpkg -i my-yt-down.deb
```

3. Verifique as permissões:
```bash
sudo chmod +x /usr/local/bin/my-yt-down
sudo chmod +x /usr/lib/my-yt-down/my-yt-down
```

## Logs e Depuração

Os logs da aplicação podem ser encontrados em:
- Logs principais: `/home/seu-usuario/my-yt-down/logs/downloader.log`
- Logs de download: `/home/seu-usuario/my-yt-down/logs/download.log`

Para visualizar os logs em tempo real:
```bash
tail -f /home/seu-usuario/my-yt-down/logs/downloader.log
```

## Uso

1. Se instalado via .deb:
   - Abra o programa pelo menu de aplicativos ou
   - Execute `my-yt-down` no terminal

2. Se instalado manualmente:
   ```bash
   python3 src/gui.py
   ```

3. Na interface do programa:
   - Cole a URL do YouTube
   - Escolha o local para salvar
   - Selecione o formato (Vídeo/Áudio)
   - Escolha o formato específico (MP4/WebM/MKV ou MP3/AAC/Opus)
   - Selecione a qualidade (Alta/Média/Baixa)
   - Clique em Download

## Problemas Comuns

### FFmpeg não encontrado
Se você receber um erro sobre FFmpeg não encontrado:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Erro de permissão ao executar
Se encontrar erro de permissão ao executar o programa:
```bash
chmod +x /usr/local/bin/my-yt-down
```

## Relatório Automático de Erros

O aplicativo inclui um sistema automático de relatório de erros que pode criar issues no GitHub automaticamente quando ocorrem problemas. Para habilitar esta funcionalidade:

1. Crie um token de acesso pessoal do GitHub:
   - Vá para GitHub > Settings > Developer settings > Personal access tokens
   - Clique em "Generate new token"
   - Selecione o escopo "repo"
   - Copie o token gerado

2. Configure as variáveis de ambiente:
```bash
export GITHUB_TOKEN="seu_token_aqui"
export GITHUB_REPO_OWNER="seu_usuario_github"
export GITHUB_REPO_NAME="nome_do_repositorio"
```

Para configuração permanente, adicione ao seu arquivo de perfil (~/.bashrc, ~/.zshrc, etc.):
```bash
echo 'export GITHUB_TOKEN="seu_token_aqui"' >> ~/.bashrc
echo 'export GITHUB_REPO_OWNER="seu_usuario_github"' >> ~/.bashrc
echo 'export GITHUB_REPO_NAME="nome_do_repositorio"' >> ~/.bashrc
source ~/.bashrc
```

### Logs de Erro

Os logs de erro são salvos em:
- Linux/macOS: `~/.my-yt-down/logs/`

Cada arquivo de log é nomeado com a data: `error_YYYYMMDD.log`

### Acessando os Logs

Existem duas maneiras de acessar os logs de erro:

1. **Pela Interface Gráfica**:
   - Clique no botão "📋 Logs" no canto superior direito da janela
   - O gerenciador de arquivos abrirá a pasta contendo os logs

2. **Manualmente**:
   - Navegue até a pasta de logs:
     * Linux/macOS: `~/.my-yt-down/logs/`
   - Os arquivos de log são nomeados como `error_YYYYMMDD.log`

### Interpretando os Logs

Cada arquivo de log contém:
- Data e hora de cada evento
- Nível do log (INFO, WARNING, ERROR, etc.)
- Mensagem detalhada do erro
- Stack trace quando aplicável
- Informações do sistema quando relevante

Exemplo de entrada de log:
```
2024-01-20 14:30:45 [ERROR] Erro ao baixar vídeo: HTTP Error 404: Not Found
Stack trace:
  File "main.py", line 45, in download_video
    ...
Sistema: Linux 5.15.0-1
Python: 3.12.0
Memória: 65% usada
```

### Limpeza de Logs

Os logs são mantidos por 30 dias por padrão. Para limpar manualmente:
1. Abra a pasta de logs (botão "📋 Logs")
2. Exclua os arquivos antigos que não são mais necessários

### Informações Coletadas

O relatório de erros inclui:
- Stack trace do erro
- Tipo e mensagem do erro
- Informações do sistema:
  * Sistema operacional e versão
  * Versão do Python
  * Uso de memória
  * Uso de CPU
  * Uso de disco
- Contexto adicional do erro

### Privacidade

- Nenhuma informação pessoal é coletada
- Apenas informações técnicas necessárias para debug são incluídas
- Os logs são armazenados apenas localmente, exceto quando uma issue é criada
- Você pode desabilitar o relatório automático não configurando as variáveis de ambiente

## Atualizações

Para atualizar o programa:
- Se instalado via .deb: Baixe e instale a nova versão .deb
- Se instalado via git: `git pull` e execute `./install.sh` novamente

## Limitações Conhecidas

1. **Linux**:
   - Em algumas distribuições, pode ser necessário instalar codecs adicionais
   - Algumas distribuições podem requerer configuração adicional do FFmpeg

2. **macOS**:
   - Pode haver problemas de compatibilidade com versões antigas do macOS
   - Algumas funcionalidades podem requerer permissões adicionais
   - Interface pode variar ligeiramente devido às diferenças do Tkinter no macOS

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.
