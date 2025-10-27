import os
import json
import threading
import time
import datetime
import pandas as pd
import schedule
from django.conf import settings 

try:
    import pywhatkit
except ModuleNotFoundError:
    print("\n\n[ERRO CRÍTICO DE AMBIENTE] Módulo 'pywhatkit' não encontrado!")
    print("O agendador de WhatsApp NÃO VAI FUNCIONAR até que você resolva o problema de PATH.")
    pywhatkit = None


LOG_BUFFER = [] 

def log(msg: str):
    """Adiciona uma linha de log com timestamp e guarda em memória para a view."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line) 
    LOG_BUFFER.append(line)
    if len(LOG_BUFFER) > 200:
        del LOG_BUFFER[0:len(LOG_BUFFER)-200]

CAMINHO_ARQUIVO = settings.CHATBOT_CONTATOS_FILE

MENSAGEM_DIA_UTIL = "Olá {nome}! 😊 Agradecemos pela sua visita ao SavePoint ontem! Esperamos te ver novamente em breve!"
MENSAGEM_FIM_DE_SEMANA = "Olá {nome}! 👾 Valeu por passar no SavePoint! Esperamos te ver de novo!"

INTERVALO_ENTRE_MSGS = 10 
HORARIO_INICIO = 9 
HORARIO_FIM = 18 


def carregar_contatos_json(caminho_json):
    """
    Lê o arquivo JSON de contatos e retorna um DataFrame pandas
    com pelo menos: Nome, Telefone, Data_Visita.
    Retorna None se der erro.
    """
    caminho_json = str(caminho_json) 
    if not os.path.isfile(caminho_json):
        log(f"[ERRO] Não encontrei o arquivo {caminho_json}")
        return None

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        log(f"[ERRO] Falha lendo/parsing o JSON: {e}")
        return None

    try:
        contatos = pd.DataFrame(dados)
    except Exception as e:
        log(f"[ERRO] Não consegui transformar o JSON em DataFrame: {e}")
        return None

    obrigatorias = ["Nome", "Telefone", "Data_Visita"]
    faltando = [c for c in obrigatorias if c not in contatos.columns]
    if faltando:
        log(f"[ERRO] contatos.json faltando colunas: {faltando}")
        log('       Formato esperado: {"Nome": "...", "Telefone": "+55...", "Data_Visita": "2025-10-25"}')
        return None

    try:
        contatos["Data_Visita"] = pd.to_datetime(contatos["Data_Visita"]).dt.date
    except Exception as e:
        log(f"[ERRO] Não consegui converter Data_Visita pra data: {e}")
        return None

    return contatos


def enviar_whatsapp_para_contatos(contatos_filtrados, mensagem_base):
    """
    Recebe um DataFrame já filtrado e manda mensagem pra cada contato.
    Usa pywhatkit (WhatsApp Web precisa estar logado).
    """
    if pywhatkit is None:
        log("[ERRO] O módulo pywhatkit falhou ao carregar. Não é possível enviar mensagens.")
        return

    if contatos_filtrados.empty:
        log("[INFO] Ninguém visitou ontem. Nada para enviar.")
        return

    log(f"[*] Visitantes encontrados ontem ({len(contatos_filtrados)}):")
    for _, row in contatos_filtrados.iterrows():
        log(f"      - {row['Nome']} {row['Telefone']}")

    for _, row in contatos_filtrados.iterrows():
        nome = str(row["Nome"]).strip()
        telefone = str(row["Telefone"]).strip()
        mensagem = mensagem_base.format(nome=nome)

        log(f"[*] Enviando para {nome} ({telefone}) ...")

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                tab_close=True
            )
            log(f"[OK] Mensagem enviada para {nome}!")
            time.sleep(INTERVALO_ENTRE_MSGS)
        except Exception as e:
            log(f"[ERRO] Falha ao enviar para {nome} ({telefone}): {e}")

    log("[*] Envio concluído.")


def job_dias_uteis():
    """
    Roda em dias úteis, mas só dentro do horário comercial.
    Filtra quem visitou 'ontem' e dispara mensagem de agradecimento.
    """
    agora = datetime.datetime.now()
    ontem = (agora - datetime.timedelta(days=1)).date()
    dia_semana = agora.weekday()
    hora_atual = agora.hour

    log("=== [JOB DIAS ÚTEIS] ===")
    log(f"Data/hora agora: {agora}")
    log("Verificando regras de dia útil e horário comercial...")

    if dia_semana >= 5:
        log("[BLOQUEADO] Hoje não é dia útil (é sábado/domingo).")
        return

    if not (HORARIO_INICIO <= hora_atual < HORARIO_FIM):
        log(f"[BLOQUEADO] Agora são {hora_atual}h, fora do horário comercial {HORARIO_INICIO}-{HORARIO_FIM}.")
        return

    contatos = carregar_contatos_json(CAMINHO_ARQUIVO)
    if contatos is None:
        log("[ERRO] Não foi possível carregar contatos.json")
        return

    contatos_ontem = contatos[contatos["Data_Visita"] == ontem]
    log(f"Total de contatos de ontem ({ontem}): {len(contatos_ontem)}")

    enviar_whatsapp_para_contatos(
        contatos_filtrados=contatos_ontem,
        mensagem_base=MENSAGEM_DIA_UTIL
    )


def job_fim_de_semana():
    """
    Roda sábado e domingo, em qualquer horário.
    Filtra quem visitou 'ontem' e dispara mensagem de agradecimento.
    """
    agora = datetime.datetime.now()
    ontem = (agora - datetime.timedelta(days=1)).date()
    dia_semana = agora.weekday()

    log("=== [JOB FIM DE SEMANA] ===")
    log(f"Data/hora agora: {agora}")
    log("Verificando se hoje é fim de semana...")

    if dia_semana < 5:
        log("[BLOQUEADO] Hoje é dia útil (seg-sex). Esse job é só fim de semana.")
        return

    contatos = carregar_contatos_json(CAMINHO_ARQUIVO)
    if contatos is None:
        log("[ERRO] Não foi possível carregar contatos.json")
        return

    contatos_ontem = contatos[contatos["Data_Visita"] == ontem]
    log(f"Total de contatos de ontem ({ontem}): {len(contatos_ontem)}")

    enviar_whatsapp_para_contatos(
        contatos_filtrados=contatos_ontem,
        mensagem_base=MENSAGEM_FIM_DE_SEMANA
    )


def configurar_agendamento():
    """
    Registra os horários em que cada job roda.
    """
    schedule.every().monday.at("16:30").do(job_dias_uteis)
    schedule.every().tuesday.at("16:30").do(job_dias_uteis)
    schedule.every().wednesday.at("16:30").do(job_dias_uteis)
    schedule.every().thursday.at("16:30").do(job_dias_uteis)
    schedule.every().friday.at("16:30").do(job_dias_uteis)

    schedule.every().saturday.at("16:00").do(job_fim_de_semana)
    schedule.every().sunday.at("06:27").do(job_fim_de_semana)

    log("BOT AGENDADO ✅")
    log(" - Seg-Sex às 16h30 -> envia modo dia útil.")
    log(" - Sáb e Dom às 16h00 -> envia modo fim de semana.")
    log("Deixe o servidor Django rodando e o WhatsApp Web logado.")


def _loop_schedule():
    configurar_agendamento()
    while True:
        schedule.run_pending()
        time.sleep(30)


_scheduler_started = False

def start_scheduler():
    """
    Chamada pelo apps.py quando o Django sobe.
    Garanti que só criamos UMA thread do agendador.
    """
    global _scheduler_started
    if _scheduler_started:
        return

    log("[INIT] Iniciando thread do bot WhatsApp agendado...")
    t = threading.Thread(target=_loop_schedule, daemon=True)
    t.start()
    _scheduler_started = True