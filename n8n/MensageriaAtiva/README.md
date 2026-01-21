# 📤 Workflow n8n — `MensageriaAtiva.json`

## 🎯 Objetivo

Este workflow é responsável por **enviar a mensagem de WhatsApp**  
usando **template aprovado pela Meta**, com **imagem no cabeçalho**.

Ele recebe do Python:
- `wa_id`
- `media_id`

---

## 🧠 Fluxo lógico

[Python]  
→ Webhook n8n  
→ HTTP Request para WhatsApp Cloud API  
→ Disparo do template  
→ Retorno do status

### Imagem do Fluxo dentro do N8N

<img width="1145" height="457" alt="image" src="https://github.com/user-attachments/assets/0a503360-c45d-40f1-bb01-de456b82d93e" />

---

## 🔐 Segurança aplicada

- ❌ Token **NÃO** fica no JSON
- ✅ Token configurado via **Credentials do n8n**
- ✅ Header Authorization gerenciado pelo n8n
- ✅ JSON versionável com segurança


---

## ✅ Resultado

- Mensagem enviada com imagem no cabeçalho
- Token protegido
- Workflow reutilizável
- Pronto para produção e portfólio

---

## 📤 MensageriaAtiva.json — o que é cada campo 

### `SEU_WEBHOOK_MENSAGERIA` (`path` do Webhook)
- **O que é:** o caminho do endpoint HTTP do n8n que recebe a requisição do Python.
- **De onde vem:** definido no nó **Webhook** (o n8n pode sugerir automaticamente).
- **Por que não versionar o valor real:** expõe o endpoint ativo do seu ambiente.
- **Como usar no projeto:**  
  - No Git: `SEU_WEBHOOK_MENSAGERIA`  
  - No `.env`: URL real em `URL_N8N`

---

### `SEU_PHONE_NUMBER_ID` (URL `/messages`)
- **O que é:** identificador técnico do número de WhatsApp que **envia** a mensagem.
- **De onde vem:** WhatsApp Cloud API / Meta Business (Phone Number ID).
- **Importante:** **não é o telefone** e **não é o wa_id do cliente**.
- **Por que não versionar o real:** amarra o workflow a uma conta/ambiente específico.
- **Como configurar:** substituir `SEU_PHONE_NUMBER_ID` no n8n com o valor do seu número registrado.

---

### `Bearer` (Authorization Token)
- **O que é:** token de autenticação da Meta usado no header `Authorization`.
- **De onde vem:** gerado no **Meta Developers / WhatsApp Cloud API**.
- **Por que nunca versionar:** é um **segredo crítico** — permite envio de mensagens.
- **Como fazer certo:**  
  - O token deve ficar em **Credentials do n8n**  
  - O JSON versionado **não deve conter o Bearer**

---

### `credentials.httpHeaderAuth`
- **O que é:** referência à Credential do n8n onde o token Bearer está armazenado.
- **Como deve ficar no Git:** apenas o campo `name`.
- **Por quê:** o campo `id` da credential é interno do n8n e específico do ambiente.

---

### `id` (dos nós)
- **O que é:** identificador interno de cada nó no workflow.
- **De onde vem:** gerado automaticamente pelo n8n ao criar/importar o workflow.
- **Por que não versionar:** não representa lógica e só adiciona ruído.
- **Importante:** o n8n recria automaticamente ao importar o JSON.

---

### `webhookId`
- **O que é:** identificador interno do Webhook no n8n.
- **De onde vem:** gerado automaticamente quando o nó Webhook é criado.
- **Por que não versionar:** identifica o endpoint real do ambiente.
- **Boa prática:** remover antes de versionar.

---

### `versionId`
- **O que é:** identificador da versão interna do workflow no n8n.
- **De onde vem:** controle interno do n8n para versionamento.
- **Por que não versionar:** muda a cada alteração e não faz parte da lógica.
- **Impacto:** nenhum — pode ser removido com segurança.

---

### `jsonBody` (payload do template)
- **O que é:** corpo da requisição enviada à WhatsApp Cloud API.
- **Campos importantes:**
  - `to`: `{{ $json.body.wa_id }}` → destinatário (vem do Excel/Python)
  - `template.name`: `mensageria_saudacao` → template aprovado na Meta
  - `language.code`: `pt_BR` → idioma
  - `header.image.id`: `{{ $json.body.media_id }}` → imagem enviada previamente
- **Por que é seguro versionar:** não contém segredos, apenas estrutura da mensagem.

---

## ✅ Resumo prático

- **Versionar no Git:** estrutura do workflow + placeholders (`SEU_*`)
- **Nunca versionar:** tokens, ids internos, webhook real
- **Configurar no n8n:** Phone Number ID + Bearer via Credentials
- **Configurar no `.env`:** URLs reais dos webhooks

---

## 📄 Versão sanitizada para GitHub (`MensageriaAtiva.json`)

```json
{
  "name": "MensageriaAtiva",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "SEU_WEBHOOK_MENSAGERIA",
        "responseMode": "responseNode"
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [-40, 0],
      "name": "Webhook"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://graph.facebook.com/v22.0/SEU_PHONE_NUMBER_ID/messages",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"messaging_product\": \"whatsapp\",\n  \"to\": \"{{ $json.body.wa_id }}\",\n  \"type\": \"template\",\n  \"template\": {\n    \"name\": \"mensageria_saudacao\",\n    \"language\": { \"code\": \"pt_BR\" },\n    \"components\": [\n      {\n        \"type\": \"header\",\n        \"parameters\": [\n          {\n            \"type\": \"image\",\n            \"image\": { \"id\": \"{{ $json.body.media_id }}\" }\n          }\n        ]\n      }\n    ]\n  }\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [220, 0],
      "name": "Enviar Template",
      "credentials": {
        "httpHeaderAuth": {
          "name": "WhatsApp Cloud API Token"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "allIncomingItems"
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [440, 0],
      "name": "Resposta Final"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "Enviar Template", "type": "main", "index": 0 }]]
    },
    "Enviar Template": {
      "main": [[{ "node": "Resposta Final", "type": "main", "index": 0 }]]
    }
  }
}
