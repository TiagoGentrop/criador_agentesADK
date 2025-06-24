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
        f"agents/{nome_pasta}/__init__.py": "from . import agent",
        
        f"agents/{nome_pasta}/agent.py": f"""from .prompt import ROOT_AGENT_INSTRUCTION
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
name='{nome_pasta}',
description="",
instruction=ROOT_AGENT_INSTRUCTION,
tools=[],
)
""",
        "agents/__init__.py":"",

        "agents/bot_registry.py":f"""import importlib
BOTS = {{
    "{nome_pasta}": {{
        "agent_import": "agents.{nome_pasta}.agent",
        "agent_name": "root_agent",
        "requirements": [
            "google-cloud-aiplatform[adk,agent_engines]",
        ],
        "extra_packages": ["agents/{nome_pasta}"],
    }},
}}

def get_agent_and_config({nome_pasta}):
    config = BOTS.get({nome_pasta})
    if not config:
        raise ValueError(f"Bot {nome_pasta} não está configurado!")
    mod = importlib.import_module(config["agent_import"])
    agent = getattr(mod, config["agent_name"])
    return agent, config
""",
        "deployment/remote.py":"""import os
import sys
import vertexai

from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from agents.bot_registry import get_agent_and_config

FLAGS = flags.FLAGS
flags.DEFINE_string("bot", None, "Nome do bot a ser usado.")
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("user_id", "test_user", "User ID for session operations.")
flags.DEFINE_string("session_id", None, "Session ID for operations.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("update", False, "Updates an existing deployment.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.DEFINE_bool("list", False, "Lists all deployments.")
flags.DEFINE_bool("create_session", False, "Creates a new session.")
flags.DEFINE_bool("list_sessions", False, "Lists all sessions for a user.")
flags.DEFINE_bool("get_session", False, "Gets a specific session.")
flags.DEFINE_bool("send", False, "Sends a message to the deployed agent.")
flags.DEFINE_string(
    "message",
    "Shorten this message: Hello, how are you doing today?",
    "Message to send to the agent.",
)
flags.mark_bool_flags_as_mutual_exclusive(
    [
        "create",
        "update",
        "delete",
        "list",
        "create_session",
        "list_sessions",
        "get_session",
        "send",
    ]
)

# <<< MUDANÇA AQUI: Adicionamos esta função para ler o arquivo de dependências
def get_requirements_from_file(file_path="requirements.txt"):
    #"Lê um arquivo requirements.txt e retorna uma lista de dependências."
    try:
        with open(file_path, "r") as f:
            # Filtra linhas vazias ou que sejam comentários
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"ERRO: Arquivo de dependências '{file_path}' não encontrado.")
        return []


def create(bot_name) -> None:
    #"Creates a new deployment."
    agent, config = get_agent_and_config(bot_name)
    # AdkApp só precisa se você for usar em outro lugar
    app = reasoning_engines.AdkApp(
        agent=agent,
        enable_tracing=True,
    )

    remote_app = agent_engines.create(
        agent_engine=agent,
        requirements=config["requirements"],
        extra_packages=config["extra_packages"],
    )
    print(f"Created remote app: {remote_app.resource_name}")

#UPDATE ainda precisa de todas as subdependências do projeto!
def update(bot_name, resource_id: str) -> None:
    #"Updates an existing deployment with new agent code/config."
    agent, config = get_agent_and_config(bot_name)

    # <<< MUDANÇA AQUI: Carregamos as dependências do arquivo
    all_requirements = get_requirements_from_file()
    if not all_requirements:
        print("Não foi possível carregar as dependências. Abortando a atualização.")
        return

    remote_app = agent_engines.get(resource_id)
    updated_app = remote_app.update(
        agent_engine=agent,
        requirements=all_requirements,  # Usamos a lista completa
        extra_packages=config["extra_packages"],
    )
    print(f"Updated remote app: {updated_app.resource_name}")


def delete(resource_id: str) -> None:
    #"Deletes an existing deployment."
    remote_app = agent_engines.get(resource_id)
    remote_app.delete(force=True)
    print(f"Deleted remote app: {resource_id}")


def list_deployments() -> None:
    #"Lists all deployments."
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    print("Deployments:")
    for deployment in deployments:
        print(f"- {deployment.resource_name}")


def create_session(resource_id: str, user_id: str) -> None:
    #"Creates a new session for the specified user."
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    print("Created session:")
    print(f"  Session ID: {remote_session['id']}")
    print(f"  User ID: {remote_session['user_id']}")
    print(f"  App name: {remote_session['app_name']}")
    print(f"  Last update time: {remote_session['last_update_time']}")
    print("\nUse this session ID with --session_id when sending messages.")


def list_sessions(resource_id: str, user_id: str) -> None:
    #"Lists all sessions for the specified user."
    remote_app = agent_engines.get(resource_id)
    sessions = remote_app.list_sessions(user_id=user_id)
    print(f"Sessions for user '{user_id}':")
    for session in sessions:
        print(f"- Session ID: {session['id']}")


def get_session(resource_id: str, user_id: str, session_id: str) -> None:
    #Gets a specific session.
    remote_app = agent_engines.get(resource_id)
    session = remote_app.get_session(user_id=user_id, session_id=session_id)
    print("Session details:")
    print(f"  ID: {session['id']}")
    print(f"  User ID: {session['user_id']}")
    print(f"  App name: {session['app_name']}")
    print(f"  Last update time: {session['last_update_time']}")


def send_message(resource_id: str, user_id: str, message: str) -> None:
    #"Sempre cria uma nova sessão ao enviar mensagem."
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    session_id = remote_session['id']
    print(f"Criada nova sessão: {session_id}")

    print(f"Sending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    for event in remote_app.stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        print(event)


def main(argv=None):
    #"Main function that can be called directly or through app.run()."
    # Parse flags first
    if argv is None:
        argv = flags.FLAGS(sys.argv)
    else:
        argv = flags.FLAGS(argv)

    load_dotenv()

    # Now we can safely access the flags
    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    user_id = FLAGS.user_id

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STAGING_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    if FLAGS.create:
        if not FLAGS.bot:
            print("Você deve informar o nome do bot com --bot")
            return
        create(FLAGS.bot)
    elif FLAGS.update:
        if not FLAGS.bot:
            print("Você deve informar o nome do bot com --bot")
            return
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        update(FLAGS.bot, FLAGS.resource_id)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.list:
        list_deployments()
    elif FLAGS.create_session:
        if not FLAGS.resource_id:
            print("resource_id is required for create_session")
            return
        create_session(FLAGS.resource_id, user_id)
    elif FLAGS.list_sessions:
        if not FLAGS.resource_id:
            print("resource_id is required for list_sessions")
            return
        list_sessions(FLAGS.resource_id, user_id)
    elif FLAGS.get_session:
        if not FLAGS.resource_id:
            print("resource_id is required for get_session")
            return
        if not FLAGS.session_id:
            print("session_id is required for get_session")
            return
        get_session(FLAGS.resource_id, user_id, FLAGS.session_id)
    elif FLAGS.send:
        if not FLAGS.resource_id:
            print("resource_id is required for send")
            return
        send_message(FLAGS.resource_id, user_id, FLAGS.message)
    else:
        print(
            "Please specify one of: --create, --delete, --list, --create_session, --list_sessions, --get_session, or --send"
        )


if __name__ == "__main__":
    app.run(main)
""",

        ".gitignore":""".env
__pycache__/
""",
        f"agents/{nome_pasta}/prompt.py": """ROOT_AGENT_INSTRUCTION = """,
        
        "requirements.txt": """google-adk
google-generativeai
""",
        
        ".env": """GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
GOOGLE_GENAI_USE_VERTEXAI=True""",
        
        f"agents/{nome_pasta}/tools/__init__.py": """from .funcs import 
__all__ = [""]
""",
        f"agents/{nome_pasta}/tools/funcs.py": """""",

        "pyproject.toml":"""[project]
name = "agents"
version = "0.1.0"
description = "A bot that shortens your messages"
authors = [
    {name = "", email = ""}
]
readme = "README.md"
requires-python = ">=3.12"
license = "Apache License 2.0"

[tool.poetry.dependencies]
python = ">=3.12"
requests = "^2.31.0"
google-cloud-aiplatform = {extras = ["adk", "agent_engines", "reasoningengine"], version = "^1.89.0"}
google-generativeai = "^0.7.2"
google-adk = "^0.1.0"

[tool.poetry]
packages = [
  { include = "agents" }
]

[tool.poetry.scripts]
adk-simple-bot = "agents/adk_simple_bot:app"
deploy-local = "deployment.local:main"
deploy-remote = "deployment.remote:main"
cleanup = "deployment.cleanup:cleanup_deployment"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.requires-plugins]
poetry-plugin-export = ">=1.8"""
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