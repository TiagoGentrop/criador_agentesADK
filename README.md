# Projeto: Criador_agentesADK

## 📝 Descrição

Este script é uma ferramenta de linha de comando para criar uma estrutura
de projeto padronizada para agentes de IA, referida como "ADK" (Agent
Development Kit).

Ao ser executado, o script solicita o nome do novo agente e, em seguida,
gera automaticamente uma estrutura de pastas e arquivos com conteúdo
básico (boilerplate). O objetivo é acelerar o início de novos projetos
de agentes, garantindo consistência e boas práticas de organização de código.

## 📂 Estrutura do Projeto

Este projeto foi organizado para separar claramente a lógica, as ferramentas e as configurações. Abaixo está a descrição de cada componente principal.

### **Visão Geral da Estrutura**

```
.
├── tools/                
│   ├── __init__.py
│   └── funcs.py          
├── .env                  
├── __init__.py           
├── agent.py              
├── prompt.py             
├── requirements.txt      
└── README.md             
```

### **Propósito dos Arquivos**

* **`agent.py`**
    * Este é o coração do projeto. Ele contém a classe principal do agente e orquestra toda a lógica de funcionamento, decidindo quando usar as ferramentas e como responder aos estímulos.

* **`prompt.py`**
    * Para manter o código limpo, todos os textos (prompts) que são enviados para os modelos de linguagem (IA) ficam centralizados neste arquivo. Isso facilita a edição e o teste de diferentes prompts.

* **`tools/`**
    * Esta pasta organiza as "ferramentas" que o agente pode utilizar. Uma ferramenta é uma função que executa uma tarefa específica (ex: buscar um arquivo, enviar um e-mail).

* **`tools/funcs.py`**
    * É aqui que as funções das ferramentas são efetivamente escritas. Cada função neste arquivo deve ter um propósito claro e ser, de preferência, independente.

* **`requirements.txt`**
    * Lista todas as bibliotecas externas (pacotes Python) que o projeto precisa para funcionar. Serve como um registro das dependências do projeto.

* **`.env`**
    * Arquivo de configuração para armazenar informações sensíveis, como chaves de API, senhas ou tokens de acesso. **Este arquivo nunca deve ser compartilhado.**

* **`__init__.py`**
    * Este arquivo, mesmo que vazio, sinaliza para o Python que a pasta onde ele se encontra é um "pacote" Python, permitindo a importação de módulos entre as pastas de forma organizada.