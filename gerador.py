import pathlib

def gerar_estrutura_agente():

    print("--- Gerador de Estrutura de Projeto para Agentes ---")

    nome_projeto = input("Qual é o nome do novo projeto de agente? ")

    if not nome_projeto:
        print("Erro: O nome do projeto não pode ser vazio.")
        return

    # Converte o nome para um formato de pasta (lowercase, sem espaços)
    nome_pasta = nome_projeto.lower().replace(" ", "_")
    root_dir = pathlib.Path(nome_pasta)

    # 2. DEFININDO A ESTRUTURA E O CONTEÚDO PADRÃO
    # Usamos um dicionário para mapear cada arquivo ao seu conteúdo inicial.
    # Isso torna o código mais limpo e fácil de modificar.
    conteudos_boilerplate = {
        "__init__.py": "from . import agent",
        
        "agent.py": f"""from .prompt import ROOT_AGENT_INSTRUCTION
from .tools import 
import os
from dotenv import load_dotenv
load_dotenv()

vertexai.init(
project=os.getenv("GOOGLE_CLOUD_PROJECT"),
location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

root_agent = Agent(
model="gemini-2.0-flash",
name='{nome_projeto}',
description="",
instruction=ROOT_AGENT_INSTRUCTION,
tools=[],
)
""",
        
        "prompt.py": """ROOT_AGENT_INSTRUCTION = """,
        
        "requirements.txt": """google-adk
google-generativeai
""",
        
        ".env": """GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
GOOGLE_GENAI_USE_VERTEXAI=True""",
        
        "tools/__init__.py": """from .funcs import 
__all__ = [""]
""",
        "tools/funcs.py": """"""
    }

    # 3. CRIANDO A ESTRUTURA
    try:
        print(f"\\nCriando estrutura para o projeto '{nome_pasta}'...")

        # Criando o diretório principal
        root_dir.mkdir(exist_ok=True)
        print(f"  [OK] Diretório principal: ./{nome_pasta}/")
        
        # Criando todos os arquivos
        for caminho_relativo, conteudo in conteudos_boilerplate.items():
            caminho_completo = root_dir / pathlib.Path(caminho_relativo)
            
            # Garante que a subpasta exista antes de criar o arquivo nela
            caminho_completo.parent.mkdir(parents=True, exist_ok=True)
            
            # Escreve o conteúdo no arquivo
            caminho_completo.write_text(conteudo, encoding="utf-8")
            print(f"  [OK] Arquivo criado: ./{caminho_completo}")

        print("\\nEstrutura do projeto criada com sucesso!")

    except Exception as e:
        print(f"\\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_estrutura_agente()