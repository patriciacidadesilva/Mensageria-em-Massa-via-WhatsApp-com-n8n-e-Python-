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
