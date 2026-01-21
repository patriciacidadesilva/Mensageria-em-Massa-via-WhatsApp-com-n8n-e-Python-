# ============================================================
# 📲 Disparo SAUDAÇÃO 
# 1. IMPORTANDO BIBLIOTECAS
# ------------------------------------------------------------

import pandas as pd  # Importa o pandas para ler/manipular a planilha Excel (DataFrame)
import os  # Importa o módulo os para ler variáveis de ambiente e checar caminhos/arquivos
import logging  # Importa logging para gerar logs (INFO/WARNING/ERROR) no terminal
import requests  # Importa requests para fazer chamadas HTTP para os webhooks do n8n
import time  # Importa time para controlar delays (sleep) entre envios e retries
import re  # Importa re (regex) para normalizar o telefone removendo caracteres não numéricos
from dotenv import load_dotenv  # Importa load_dotenv para carregar variáveis do arquivo .env


# ============================================================
# 2. LOGS
# ============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # Configura nível INFO e formato dos logs
logger = logging.getLogger(__name__)  # Cria um logger associado a este arquivo (nome do módulo)


# ============================================================
# 3. CARREGA .env
# - O .env deve estar no diretório atual de execução
# ============================================================
load_dotenv()  # Carrega as variáveis do arquivo .env (por padrão no diretório atual)


# ============================================================
# 4. VARIÁVEIS DE AMBIENTE
# ============================================================
CAMINHO_DADOS = os.environ.get('CAMINHO_ARQUIVO')  # Lê do .env o caminho do Excel com os telefones
URL_N8N_IMG_POST = os.environ.get('URL_N8N_IMG_POST')  # Lê do .env o webhook do n8n responsável por upload da imagem
FOTO = os.environ.get('FOTO')  # Lê do .env o caminho da imagem de saudação
URL_N8N = os.environ.get('URL_N8N')  # Lê do .env o webhook do n8n responsável pelo disparo do template
USUARIO_N8N = os.environ.get('USUARIO_N8N')  # Lê do .env o usuário (se o webhook exigir Basic Auth)
SENHA_N8N = os.environ.get('SENHA_N8N')  # Lê do .env a senha (se o webhook exigir Basic Auth)
USE_AUTH = os.environ.get("USE_AUTH", "false").lower() == "true"  # Lê USE_AUTH e converte para boolean (true/false)


# ============================================================
# 5. AUTH
# - Se USE_AUTH=true, envia Basic Auth no requests.post
# - Se USE_AUTH=false, não envia autenticação
# ============================================================
def auth():  # Define uma função para retornar autenticação quando necessário
    return (USUARIO_N8N, SENHA_N8N) if USE_AUTH else None  # Se USE_AUTH=true retorna tupla (user,pass), senão None (sem auth)


# ============================================================
# 6. VALIDAÇÃO
# - Garante que as variáveis do .env existem e não estão vazias
# - Garante que Excel e imagem existem no caminho informado
# ============================================================
def validar_variaveis():  # Define uma função para validar se o .env e arquivos estão corretos
    variaveis = {  # Cria um dicionário com variáveis obrigatórias para o script rodar
        'CAMINHO_ARQUIVO': CAMINHO_DADOS,  # Mapeia o nome lógico para o valor lido do .env
        'URL_N8N_IMG_POST': URL_N8N_IMG_POST,  # Mapeia o webhook de upload de imagem
        'FOTO': FOTO,  # Mapeia o caminho da imagem
        'URL_N8N': URL_N8N,  # Mapeia o webhook de disparo
    }  # Fecha o dicionário

    for nome, valor in variaveis.items():  # Percorre cada variável (nome, valor)
        if not valor:  # Se o valor for None, vazio ou falso
            raise ValueError(f"A variável de ambiente {nome} não está definida ou está vazia")  # Interrompe com erro explicativo

    if not os.path.exists(CAMINHO_DADOS):  # Verifica se o arquivo Excel existe no caminho indicado
        raise FileNotFoundError(f"Excel não encontrado: {CAMINHO_DADOS}")  # Se não existir, levanta erro
    if not os.path.exists(FOTO):  # Verifica se a imagem existe no caminho indicado
        raise FileNotFoundError(f"Imagem não encontrada: {FOTO}")  # Se não existir, levanta erro

    if USE_AUTH and (not USUARIO_N8N or not SENHA_N8N):  # Se auth estiver ligado, usuário e senha precisam existir
        raise ValueError("USE_AUTH=true, mas USUARIO_N8N/SENHA_N8N não foram definidos.")  # Se faltar, levanta erro

    logger.info(f"USE_AUTH={USE_AUTH}")  # Loga se autenticação está habilitada (não loga senha)
    logger.info(f"URL_N8N_IMG_POST={URL_N8N_IMG_POST}")  # Loga o endpoint de upload (ajuda no debug)
    logger.info(f"URL_N8N={URL_N8N}")  # Loga o endpoint de disparo (ajuda no debug)


# ============================================================
# 7. NORMALIZAÇÃO DO wa_id (telefone)
# - Remove .0 (Excel)
# - Remove caracteres não numéricos
# - Retorna somente dígitos (ex.: 5511999999999)
# ============================================================
def normalizar_wa_id(x: str) -> str:  # Função para normalizar o telefone/wa_id para somente dígitos
    s = str(x).strip().replace(".0", "")  # Converte para string, remove espaços e remove ".0" comum vindo do Excel
    s = re.sub(r"\D", "", s)  # Remove tudo que não é dígito (mantém apenas números)
    return s  # Retorna o telefone normalizado (ex.: 5511999999999)


# ============================================================
# 8. DETECTA A COLUNA DE TELEFONE NO EXCEL
# - Aceita 'Telefone' ou 'Telefones'
# ============================================================
def coluna_telefone(df: pd.DataFrame) -> str:  # Função para descobrir qual coluna do Excel contém os telefones
    cols = {c.lower(): c for c in df.columns}  # Cria mapa: nome_em_minúsculo -> nome_original da coluna
    if "telefones" in cols:  # Se existir a coluna "telefones" (case-insensitive)
        return cols["telefones"]  # Retorna o nome original dessa coluna
    if "telefone" in cols:  # Se existir a coluna "telefone" (case-insensitive)
        return cols["telefone"]  # Retorna o nome original dessa coluna
    raise ValueError("A planilha precisa ter coluna Telefone ou Telefones")  # Se não achar, interrompe com erro


# ============================================================
# 9. UPLOAD DA IMAGEM
# - Envia imagem ao n8n (workflow PostImagem)
# - O n8n faz upload no WhatsApp e retorna media_id (ou id)
# ============================================================
def send_foto(foto):  # Função que faz o upload da imagem para o n8n e retorna o media_id
    with open(foto, 'rb') as f:  # Abre o arquivo de imagem em modo binário (leitura)
        nome_arquivo = os.path.basename(foto)  # Pega somente o nome do arquivo (sem o caminho) para enviar no upload
        files = {'file': (nome_arquivo, f, 'image/png')}  # Monta multipart/form-data com o arquivo e MIME type (PNG)

        response = requests.post(  # Faz POST para o webhook de upload de imagem
            URL_N8N_IMG_POST,  # URL do webhook PostImagem no n8n
            files=files,  # Envia arquivo no corpo (multipart)
            auth=auth(),  # Envia auth se USE_AUTH=true; caso contrário None
            timeout=60  # Timeout de 60s para o upload não travar indefinidamente
        )  # Fecha a chamada requests.post

        if response.status_code == 200:  # Se a resposta HTTP for 200 (sucesso)
            try:  # Tenta interpretar o corpo como JSON
                media_id = response.json().get('media_id') or response.json().get('id') or response.json().get('mediaId')  # Busca media_id em possíveis chaves
            except Exception:  # Se falhar parsear JSON
                raise ValueError(f"Upload retornou 200 mas não é JSON: {response.text}")  # Interrompe com mensagem e corpo retornado

            if not media_id:  # Se não encontrou media_id no JSON
                raise ValueError(f"Upload OK mas sem media_id na resposta: {response.text}")  # Interrompe com mensagem

            logger.info(f"Upload concluído. media_id: {media_id}")  # Loga o media_id retornado
            return media_id  # Retorna o media_id para ser usado no disparo do template
        else:  # Se status diferente de 200
            logger.error(f"Erro no upload: {response.status_code} - {response.text}")  # Loga status e body do erro
            response.raise_for_status()  # Lança exceção HTTPError com base no status code


# ============================================================
# 10. ENVIO PARA N8N COM RETRY + BACKOFF
# - Tenta max_retries
# - Trata 429 (rate limit) esperando 5s
# - Backoff exponencial: 1s, 2s, 4s...
# ============================================================
def send_n8n(doc, max_retries=3):  # Função que envia um payload (wa_id + media_id) para o n8n com retry
    for tentativa in range(max_retries):  # Repete até max_retries tentativas (0..max_retries-1)
        try:  # Tenta realizar o POST
            response = requests.post(  # Faz POST para o webhook de disparo
                URL_N8N,  # URL do webhook MensageriaAtiva no n8n
                auth=auth(),  # Auth opcional
                json=doc,  # Envia o payload como JSON (body)
                timeout=30  # Timeout de 30s para cada envio
            )  # Fecha requests.post

            if response.status_code == 200:  # Se sucesso
                return {"sucesso": True, "wa_id": doc.get("wa_id"), "status": response.status_code}  # Retorna sucesso e o wa_id

            if response.status_code == 429:  # Se rate limit
                logger.warning("Rate limit atingido (429). Aguardando 5s...")  # Loga aviso
                time.sleep(5)  # Espera 5s antes de tentar de novo
                continue  # Volta para próxima tentativa

            logger.warning(f"Erro {response.status_code} para {doc.get('wa_id')}: {response.text}")  # Loga erro de status e body

        except requests.exceptions.RequestException as e:  # Se houver erro de rede/timeout/etc
            logger.warning(f"Tentativa {tentativa + 1}/{max_retries} falhou para {doc.get('wa_id')}: {e}")  # Loga tentativa e erro

        time.sleep(2 ** tentativa)  # Backoff exponencial: 1s (2^0), 2s (2^1), 4s (2^2)...

    return {"sucesso": False, "wa_id": doc.get("wa_id"), "erro": "Máximo de tentativas excedidas"}  # Se acabou tentativas, retorna falha


# ============================================================
# 11. ENVIO EM LOTE
# - Normaliza telefones
# - Remove vazios e duplicados
# - Envia sequencialmente com delay para respeitar rate limit
# ============================================================
def enviar_lote_n8n(dados, media_id, delay_entre_requests=0.5):  # Função que envia todos os contatos em lote
    col = coluna_telefone(dados)  # Descobre qual coluna contém os telefones

    dados[col] = dados[col].astype(str).map(normalizar_wa_id)  # Converte valores para string e normaliza para somente dígitos
    dados = dados[dados[col].str.len() > 0].drop_duplicates(subset=[col])  # Remove telefones vazios e duplicados

    documentos = [{"wa_id": linha[col], "media_id": media_id} for _, linha in dados.iterrows()]  # Monta lista de payloads (um por telefone)

    resultados = {"sucesso": 0, "falha": 0, "erros": []}  # Cria objeto de resultados para contagem e registro de falhas
    logger.info(f"Iniciando envio de {len(documentos)} documentos para n8n...")  # Loga quantos contatos serão processados

    for i, doc in enumerate(documentos):  # Percorre cada payload, com índice i
        resultado = send_n8n(doc)  # Envia o payload com retry

        if resultado["sucesso"]:  # Se retornou sucesso
            resultados["sucesso"] += 1  # Incrementa contador de sucesso
        else:  # Se falhou
            resultados["falha"] += 1  # Incrementa contador de falha
            resultados["erros"].append(resultado)  # Armazena detalhes do erro (wa_id e mensagem)

        if (i + 1) % 50 == 0:  # A cada 50 envios
            logger.info(f"Progresso: {i + 1}/{len(documentos)} enviados")  # Loga progresso parcial

        time.sleep(delay_entre_requests)  # Espera um pouco entre requests para evitar rate limit

    logger.info(f"Envio concluído. Sucesso: {resultados['sucesso']}, Falhas: {resultados['falha']}")  # Loga resumo final
    return resultados  # Retorna o resumo e lista de erros (se houver)


# ============================================================
# 12. EXECUÇÃO PRINCIPAL
# ============================================================
if __name__ == "__main__":  # Garante que o código abaixo roda apenas quando o arquivo é executado diretamente
    try:  # Inicia bloco de execução com tratamento de erro
        validar_variaveis()  # Valida se .env e arquivos estão corretos
        media_id = send_foto(FOTO)  # Faz upload da imagem e obtém o media_id do WhatsApp via n8n
        dados = pd.read_excel(CAMINHO_DADOS, engine='openpyxl', dtype=str)  # Lê Excel como string para não “quebrar” telefones
        enviar_lote_n8n(dados, media_id, delay_entre_requests=0.5)  # Envia em lote com delay de 0.5s
        logger.info("Processamento concluído.")  # Loga que terminou com sucesso
    except Exception as e:  # Captura qualquer erro não tratado dentro do fluxo
        logger.error(f"Erro: {e}")  # Loga a mensagem de erro
        raise  # Re-lança o erro para aparecer no terminal com stack trace (melhor para debug)
