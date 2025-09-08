# Servidor HTTP simples para servir arquivos estáticos
# Isso resolve problemas de CORS com file://

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Definir porta e diretório
PORT = 3000
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Adicionar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def start_server():
    # Mudar para o diretório do projeto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Servidor frontend rodando em http://localhost:{PORT}")
        print(f"📁 Servindo arquivos de: {os.path.abspath(DIRECTORY)}")
        print("🔗 Abrindo navegador...")
        
        # Abrir navegador automaticamente
        webbrowser.open(f"http://localhost:{PORT}")
        
        print("📋 Para parar o servidor, pressione Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor parado!")

if __name__ == "__main__":
    start_server()
