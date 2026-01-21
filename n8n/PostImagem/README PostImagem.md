# 🔄 Workflow n8n — `PostImagem.json`

## 🎯 Objetivo

Este workflow é responsável por **receber uma imagem via webhook**,  
**fazer o upload dessa imagem no WhatsApp Cloud API**  
e **retornar o `media_id`**, que será usado no envio da mensagem.

Ele é chamado **primeiro** pelo script Python.

---

## 🧠 Fluxo lógico

[Python]  
→ Webhook n8n  
→ Upload da imagem no WhatsApp  
→ Retorno do `media_id`

[Imagem do Fluxo dentro do N8N]  
<img width="1167" height="452" alt="image" src="https://github.com/user-attachments/assets/f3411e2c-8c73-4480-b7f8-9f1981e81a9a" />

---

## 📌 Pontos importantes de segurança

- ❌ Nenhuma credencial hardcoded no JSON
- ✅ Credenciais do WhatsApp ficam no **Credentials do n8n**
- ✅ Webhook exposto apenas como endpoint técnico

---

## ✅ Resultado

-O Python recebe apenas { "media_id": "xxxx" }
-Nenhum segredo exposto
-Workflow reutilizável para qualquer campanha

---

## 🧩 PostImagem.json — o que é cada campo 

### `path` (Webhook)
- **O que é:** o caminho do endpoint no n8n.
- **De onde vem:** você define no nó Webhook (ou o n8n sugere um valor).
- **Por que não versionar o real:** expõe o endpoint do seu ambiente.
- **Como usar no projeto:** no Git usamos `SEU_WEBHOOK_POST_IMAGEM` e no `.env` você coloca a URL real (`URL_N8N_IMG_POST`).

### `phoneNumberId`
- **O que é:** ID do número de WhatsApp que envia mensagens (não é o telefone).
- **De onde vem:** WhatsApp Cloud API / Meta Business (Phone Number ID).
- **Por que não versionar o real:** amarra o workflow a um ambiente/conta e expõe infraestrutura.
- **Como configurar:** substituir `SEU_PHONE_NUMBER_ID` no n8n conforme seu número.

### `credentials.whatsAppApi`
- **O que é:** referência à Credential do n8n (onde ficam os tokens/segredos).
- **Como deve ficar no Git:** **apenas o `name`**, sem `id`.
- **Por quê:** o `id` é interno do n8n e pode indicar uma credencial real do ambiente.

### `id` e `webhookId`
- **O que são:** metadados internos gerados pelo n8n (não são lógica do fluxo).
- **Por que removemos:** reduzem ruído e evitam expor detalhes do ambiente.
- **Importante:** o n8n recria esses IDs automaticamente ao importar.

---

## 📄 Versão sanitizada para GitHub (`PostImagem.json`)

```json
{
  "name": "PostImagem",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "SEU_WEBHOOK_POST_IMAGEM",
        "responseMode": "responseNode"
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [-50, 0],
      "name": "Webhook"
    },
    {
      "parameters": {
        "resource": "media",
        "phoneNumberId": "SEU_PHONE_NUMBER_ID",
        "mediaPropertyName": "file"
      },
      "type": "n8n-nodes-base.whatsApp",
      "typeVersion": 1,
      "position": [200, 0],
      "name": "Upload Media",
      "credentials": {
        "whatsAppApi": {
          "name": "WhatsApp Cloud API (Credential n8n)"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"media_id\": $json.id } }}",
        "options": { "responseCode": 200 }
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [450, 0],
      "name": "Return media_id"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "Upload Media", "type": "main", "index": 0 }]]
    },
    "Upload Media": {
      "main": [[{ "node": "Return media_id", "type": "main", "index": 0 }]]
    }
  }
