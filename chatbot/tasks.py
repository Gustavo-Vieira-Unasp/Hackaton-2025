import os
import json
import threading
import time
import datetime
import pandas as pd
import pywhatkit
import schedule
from django.conf import settings  # pega caminhos do settings

# -----------------------
# LOG EM MEMÓRIA
# -----------------------
LOG_BUFFER = []  # últimas mensagens de log (mostradas na página /chatbot/status/)

def log(msg: str):
    """Adiciona uma linha de log com timestamp e guarda em memória para a view."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)  # ainda printa no console
    LOG_BUFFER.append(line)
    # limita tamanho do buffer pra não ficar infinito
    if len(LOG_BUFFER) > 200:
        del LOG_BUFFER[0:len(LOG_BUFFER)-200]


# Caminho do arquivo de contatos definido no settings.py
CAMINHO_ARQUIVO = settings.CHATBOT_CONTATOS_FILE

MENSAGEM_DIA_UTIL = "Olá {nome}! 😊 Agradecemos pela sua visita ao SavePoint ontem! Esperamos te ver novamente em breve!"
MENSAGEM_FIM_DE_SEMANA = "Olá {nome}! 👾 Valeu por passar no SavePoint! Esperamos te ver de novo!"

INTERVALO_ENTRE_MSGS = 10  # segundos entre cada envio
HORARIO_INICIO = 9         # horário comercial - início
HORARIO_FIM = 18           # horário comercial - fim


def carregar_contatos_json(caminho_json):
    """
    Lê o arquivo JSON de contatos e retorna um DataFrame pandas
    com pelo menos: Nome, Telefone, Data_Visita.
    Retorna None se der erro.
    """
    caminho_json = str(caminho_json)  # garante string
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
    if contatos_filtrados.empty:
        log("[INFO] Ninguém visitou ontem. Nada para enviar.")
        return

    log(f"[*] Visitantes encontrados ontem ({len(contatos_filtrados)}):")
    for _, row in contatos_filtrados.iterrows():
        log(f"    - {row['Nome']} {row['Telefone']}")

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
    dia_semana = agora.weekday()   # 0=seg ... 6=dom
    hora_atual = agora.hour

    log("=== [JOB DIAS ÚTEIS] ===")
    log(f"Data/hora agora: {agora}")
    log("Verificando regras de dia útil e horário comercial...")

    # Bloqueia sábado/domingo
    if dia_semana >= 5:
        log("[BLOQUEADO] Hoje não é dia útil (é sábado/domingo).")
        return

    # Bloqueia fora do horário comercial
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
    dia_semana = agora.weekday()  # 5=sáb, 6=dom

    log("=== [JOB FIM DE SEMANA] ===")
    log(f"Data/hora agora: {agora}")
    log("Verificando se hoje é fim de semana...")

    # Bloqueia segunda-sexta
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
    # dias úteis às 16:30
    schedule.every().monday.at("16:30").do(job_dias_uteis)
    schedule.every().tuesday.at("16:30").do(job_dias_uteis)
    schedule.every().wednesday.at("16:30").do(job_dias_uteis)
    schedule.every().thursday.at("16:30").do(job_dias_uteis)
    schedule.every().friday.at("16:30").do(job_dias_uteis)

    # fim de semana às 16:00
    schedule.every().saturday.at("16:00").do(job_fim_de_semana)
    schedule.every().sunday.at("05:23" \
    "").do(job_fim_de_semana)

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
    Garante que só criamos UMA thread do agendador.
    """
    global _scheduler_started
    if _scheduler_started:
        return

    log("[INIT] Iniciando thread do bot WhatsApp agendado...")
    t = threading.Thread(target=_loop_schedule, daemon=True)
    t.start()
    _scheduler_started = True
