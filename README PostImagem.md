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
