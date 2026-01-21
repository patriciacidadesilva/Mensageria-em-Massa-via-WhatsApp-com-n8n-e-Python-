# 🍰📲 Mensageria em Massa via WhatsApp com n8n e Python

Automação para **envio de mensagens em massa via WhatsApp**, utilizando **Python** e **n8n**, com foco no disparo de **mensagens de boas-vindas da Confeitaria LadyDream**, contendo **imagem no cabeçalho** e **template aprovado pela Meta**.

Projeto pensado para ser **simples de operar**, **seguro** e **pronto para produção**.

---

## 🎯 Objetivo do Projeto

Automatizar o envio de uma **mensagem de boas-vindas** para clientes da LadyDream, contendo:

- 📸 Imagem personalizada no cabeçalho  
- 📝 Texto via template oficial do WhatsApp  
- 📊 Lista de contatos vinda de uma planilha Excel  

Eliminando envio manual, reduzindo erros operacionais e garantindo padronização da comunicação.

---

## 🧠 Como Funciona (Fluxo End-to-End)

1. O **Python** lê as configurações do arquivo `.env`  
2. O **Python envia a imagem** para o n8n  
3. O **n8n faz o upload da imagem no WhatsApp Cloud API** e retorna um `media_id`  
4. O **Python lê a planilha Excel** com os telefones  
5. Para cada telefone, o **Python envia `wa_id + media_id` para o n8n**  
6. O **n8n dispara o template aprovado** para cada contato via WhatsApp  

Resultado: envio automático, rastreável e em lote.

---

## 🧩 Arquitetura (alto nível)

Excel (Telefones)  
↓  
Python (upload + leitura + envio em lote)  
↓  
n8n (upload media + envio template)  
↓  
WhatsApp Cloud API

---

## 📁 Estrutura do repositório

- `src/disparo_saudacao.py` → script principal
- `n8n/PostImagem.json` → workflow de upload e retorno do media_id
- `n8n/MensageriaAtiva.json` → workflow que envia o template
- `assets/` → imagens de campanha/boas-vindas
- `data/` → base de telefones (não versionar em produção)
- `.env.example` → modelo de configuração
- `requirements.txt` → dependências

---

## 🧱 Princípios do Projeto

### ♻️ Reutilizável
- Configurações centralizadas no `.env`
- Troca de imagem, base de contatos ou campanha sem alterar código
- Estrutura padronizada e reaproveitável
- Detecção automática da coluna de telefone no Excel

### 👁️ Observável (Logs)
- Logs em tempo real no terminal
- Progresso visível durante o envio
- Identificação clara de sucessos e falhas
- Registro do `media_id` retornado pelo WhatsApp

### 🔐 Seguro
- Nenhuma credencial no código-fonte
- `.env` protegido via `.gitignore`
- Segredos gerenciados no n8n (credentials)
- Logs sem exposição de dados sensíveis

### 🚀 Escalável
- Controle de taxa de envio (rate limit)
- Retry automático com backoff exponencial
- Tratamento específico para erros 429
- Pronto para envio em grandes volumes

---

## ✅ Pré-requisitos

- Windows  
- Python 3.10+  
- VS Code ou Git Bash  
- Acesso ao n8n  
- Template do WhatsApp previamente aprovado  

---

##  🔐 Segurança

- .env nunca vai pro Git
- tokens/segredos ficam no n8n (credentials)
- logs não devem imprimir credenciais

---

##  🧪 Observabilidade (logs)

Durante a execução, o script exibe:
- Confirmação do upload da imagem (media_id)
- Progresso do envio
- Falhas por contato (quando ocorrer)

Essas informações facilitam:
- Auditoria
- Debug
- Reprocessamento

---

##  🛣️ Roadmap

- Validação automática de telefones (E.164)
- Relatório CSV de falhas
- Execução paralela com controle de throughput
- Evitar reenvio para contatos já processados
- Suporte a múltiplos templates e campanhas

---

## 🌳 Árvore do Repositório

```text
ladydream-whatsapp/
├── src/
│   └── disparo_saudacao.py          # Script principal (Python)
│
├── assets/
│   └── imagem_saudacao_ladydream.png
│
├── data/
│   └── Telefones.xlsx               # Base de contatos (exemplo)
│
├── n8n/
│   ├── PostImagem/
│   │   ├── PostImagem.json          # Workflow: upload da imagem
│   │   └── README.md                # Documentação do workflow PostImagem
│   │
│   ├── MensageriaAtiva/
│   │   ├── MensageriaAtiva.json     # Workflow: disparo do template
│   │   └── README.md                # Documentação do workflow MensageriaAtiva
│
├── .env.example                     # Modelo de configuração
├── .gitignore                       # Proteção de segredos
├── requirements.txt                 # Dependências
└── README.md                        # Documentação principal
```

---


## 🚀 Como Executar

### 1️⃣ Acessar a pasta do projeto
```bash
cd caminho/ladydream-whatsapp
```

### 2️⃣ Criar e ativar o ambiente virtual
```bash
py -m venv .venv
source .venv/Scripts/activate
```

### 3️⃣ Instalar as dependências
```bash
py -m pip install -U pip
py -m pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente
```bash
cp .env.example .env
```

Preencha o .env com:
- Caminho da planilha
- Caminho da imagem
- URLs do n8n
- Credenciais (se necessário)
- ⚠️ Nunca versionar o .env.

### 5️⃣ Executar o disparo
```bash
py src/disparo_saudacao.py
```
