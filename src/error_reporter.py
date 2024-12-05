import sys
import traceback
import logging
import json
import os
import requests
from datetime import datetime
from pathlib import Path

class GitHubIssueReporter:
    def __init__(self, token=None, repo_owner=None, repo_name=None):
        """
        Inicializa o reporter de issues.
        
        :param token: GitHub token (pode ser definido via GITHUB_TOKEN env var)
        :param repo_owner: Dono do repositório (pode ser definido via GITHUB_REPO_OWNER env var)
        :param repo_name: Nome do repositório (pode ser definido via GITHUB_REPO_NAME env var)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.repo_owner = repo_owner or os.environ.get('GITHUB_REPO_OWNER')
        self.repo_name = repo_name or os.environ.get('GITHUB_REPO_NAME')
        
        # Configurar logging
        self.setup_logging()
        
        # Verificar configuração
        if not all([self.token, self.repo_owner, self.repo_name]):
            logging.warning("GitHub reporter não configurado completamente. Issues não serão criadas automaticamente.")
    
    def setup_logging(self):
        """Configura o sistema de logging."""
        # Criar diretório de logs se não existir
        log_dir = Path.home() / '.my-yt-down' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo de log com data
        log_file = log_dir / f'error_{datetime.now().strftime("%Y%m%d")}.log'
        
        # Configurar logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def get_system_info(self):
        """Coleta informações do sistema."""
        import platform
        import psutil
        
        try:
            return {
                'os': platform.system(),
                'os_release': platform.release(),
                'python_version': platform.python_version(),
                'memory': f"{psutil.virtual_memory().percent}% used",
                'disk': f"{psutil.disk_usage('/').percent}% used",
                'cpu': f"{psutil.cpu_percent()}% used"
            }
        except Exception as e:
            logging.error(f"Erro ao coletar informações do sistema: {e}")
            return {}

    def create_issue(self, error, context=None):
        """
        Cria uma issue no GitHub com o erro.
        
        :param error: Exceção ou mensagem de erro
        :param context: Contexto adicional do erro (dict)
        :return: URL da issue criada ou None se falhar
        """
        if not all([self.token, self.repo_owner, self.repo_name]):
            logging.warning("GitHub reporter não configurado. Issue não será criada.")
            return None
            
        try:
            # Coletar informações do erro
            if isinstance(error, Exception):
                error_type = type(error).__name__
                error_message = str(error)
                error_traceback = ''.join(traceback.format_tb(error.__traceback__))
            else:
                error_type = "Error"
                error_message = str(error)
                error_traceback = traceback.format_stack()
            
            # Coletar informações do sistema
            system_info = self.get_system_info()
            
            # Criar corpo da issue
            body = f"""## Relatório de Erro Automático

### Erro
- **Tipo**: {error_type}
- **Mensagem**: {error_message}

### Stack Trace
```python
{error_traceback}
```

### Informações do Sistema
```json
{json.dumps(system_info, indent=2)}
```

### Contexto Adicional
```json
{json.dumps(context or {}, indent=2)}
```
"""
            
            # Criar título da issue
            title = f"[Auto] {error_type}: {error_message[:100]}"
            
            # Enviar para o GitHub
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': title,
                'body': body,
                'labels': ['bug', 'automated']
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            issue_url = response.json()['html_url']
            logging.info(f"Issue criada com sucesso: {issue_url}")
            return issue_url
            
        except Exception as e:
            logging.error(f"Erro ao criar issue no GitHub: {e}")
            return None
    
    def __call__(self, error, context=None):
        """
        Permite usar a classe como decorator ou context manager.
        
        Como decorator:
        @error_reporter
        def minha_funcao():
            ...
            
        Como context manager:
        with error_reporter:
            ...
        """
        return self.create_issue(error, context)

# Criar instância global
error_reporter = GitHubIssueReporter()

def setup_error_handling(token=None, repo_owner=None, repo_name=None):
    """
    Configura o handler de erros global.
    
    :param token: GitHub token
    :param repo_owner: Dono do repositório
    :param repo_name: Nome do repositório
    """
    global error_reporter
    error_reporter = GitHubIssueReporter(token, repo_owner, repo_name)
    
    def global_exception_handler(exctype, value, traceback):
        """Handler global para exceções não tratadas."""
        error_reporter(value)
        sys.__excepthook__(exctype, value, traceback)  # Chamar o handler padrão também
    
    sys.excepthook = global_exception_handler
