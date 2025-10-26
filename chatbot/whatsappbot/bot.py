import os
import json
import threading
import time
import datetime
import pandas as pd
import pywhatkit
import schedule


CAMINHO_ARQUIVO = r"C:\Users\cauec\Desktop\Hackaton-2025\chatbot\contatos.json"

MENSAGEM_DIA_UTIL = "Olá {nome}! 😊 Agradecemos pela sua visita ao SavePoint ontem! Esperamos te ver novamente em breve!"
MENSAGEM_FIM_DE_SEMANA = "Olá {nome}! 👾 Valeu por passar no SavePoint! Esperamos te ver de novo!"

INTERVALO_ENTRE_MSGS = 10  
HORARIO_INICIO = 9         
HORARIO_FIM = 18           
def carregar_contatos_json(caminho_json):
   
    if not os.path.isfile(caminho_json):
        print("[ERRO] Não encontrei o arquivo:", caminho_json)
        return None

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print("[ERRO] Falha lendo/parsing o JSON.")
        print("       Detalhes técnicos:", e)
        return None

    try:
        contatos = pd.DataFrame(dados)
    except Exception as e:
        print("[ERRO] Não consegui transformar o JSON em tabela (DataFrame).")
        print("       Detalhes técnicos:", e)
        return None

    obrigatorias = ["Nome", "Telefone", "Data_Visita"]
    faltando = [c for c in obrigatorias if c not in contatos.columns]
    if faltando:
        print("[ERRO] Seu contatos.json não tem todas as colunas necessárias.")
        print("       Faltando:", faltando)
        print('       Cada item precisa ter: {"Nome": "...", "Telefone": "+55...", "Data_Visita": "2025-10-25"}')
        return None

    try:
        contatos["Data_Visita"] = pd.to_datetime(contatos["Data_Visita"]).dt.date
    except Exception as e:
        print("[ERRO] Não consegui converter Data_Visita pra data.")
        print("       Garanta formato tipo '2025-10-25' ou '25/10/2025'.")
        print("       Detalhes técnicos:", e)
        return None

    return contatos


def enviar_whatsapp_para_contatos(contatos_filtrados, mensagem_base):
    if contatos_filtrados.empty:
        print("[INFO] Ninguém visitou ontem. Nada para enviar.\n")
        return

    print(f"[*] Visitantes encontrados ontem ({len(contatos_filtrados)}):")
    for _, row in contatos_filtrados.iterrows():
        print("    -", row["Nome"], row["Telefone"])
    print()

    for _, row in contatos_filtrados.iterrows():
        nome = str(row["Nome"]).strip()
        telefone = str(row["Telefone"]).strip()
        mensagem = mensagem_base.format(nome=nome)

        print(f"[*] Enviando para {nome} ({telefone}) ...")

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                tab_close=True
            )
            print(f"[OK] Mensagem enviada para {nome}!\n")
            time.sleep(INTERVALO_ENTRE_MSGS)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar para {nome} ({telefone}): {e}\n")

    print("[*] Envio concluído.\n")


def job_dias_uteis():
    agora = datetime.datetime.now()
    ontem = (agora - datetime.timedelta(days=1)).date()
    dia_semana = agora.weekday()  
    hora_atual = agora.hour

    print("\n=== [JOB DIAS ÚTEIS] ===")
    print(f"Data/hora agora: {agora}")
    print("Verificando regras de dia útil e horário comercial...")

    if dia_semana >= 5:
        print("[BLOQUEADO] Hoje não é dia útil (é sábado/domingo).")
        return

    if not (HORARIO_INICIO <= hora_atual < HORARIO_FIM):
        print(f"[BLOQUEADO] Agora são {hora_atual}h, fora do horário comercial {HORARIO_INICIO}-{HORARIO_FIM}.")
        return

    contatos = carregar_contatos_json(CAMINHO_ARQUIVO)
    if contatos is None:
        return

    contatos_ontem = contatos[contatos["Data_Visita"] == ontem]

    enviar_whatsapp_para_contatos(
        contatos_filtrados=contatos_ontem,
        mensagem_base=MENSAGEM_DIA_UTIL
    )


def job_fim_de_semana():

    agora = datetime.datetime.now()
    ontem = (agora - datetime.timedelta(days=1)).date()
    dia_semana = agora.weekday()  # 5=sáb, 6=dom

    print("\n=== [JOB FIM DE SEMANA] ===")
    print(f"Data/hora agora: {agora}")
    print("Verificando se hoje é fim de semana...")

    if dia_semana < 5:
        print("[BLOQUEADO] Hoje é dia útil (seg-sex). Esse job é só fim de semana.")
        return

    contatos = carregar_contatos_json(CAMINHO_ARQUIVO)
    if contatos is None:
        return

    contatos_ontem = contatos[contatos["Data_Visita"] == ontem]

    enviar_whatsapp_para_contatos(
        contatos_filtrados=contatos_ontem,
        mensagem_base=MENSAGEM_FIM_DE_SEMANA
    )


def configurar_agendamento():

    schedule.every().monday.at("16:30").do(job_dias_uteis)
    schedule.every().tuesday.at("16:30").do(job_dias_uteis)
    schedule.every().wednesday.at("16:30").do(job_dias_uteis)
    schedule.every().thursday.at("16:30").do(job_dias_uteis)
    schedule.every().friday.at("16:30").do(job_dias_uteis)

    schedule.every().saturday.at("16:00").do(job_fim_de_semana)
    schedule.every().sunday.at("04:33").do(job_fim_de_semana)

    print("BOT AGENDADO ✅")
    print(" - Seg-Sex às 16h30 -> envia mensagem modo dia útil.")
    print(" - Sáb e Dom às 16h00 -> envia mensagem modo fim de semana.")
    print("Deixe o servidor Django rodando e o WhatsApp Web logado.\n")


def _loop_schedule():
    configurar_agendamento()

    while True:
        schedule.run_pending()
        time.sleep(30)


_scheduler_started = False

def start_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return

    print("[INIT] Iniciando thread do bot WhatsApp agendado...")
    t = threading.Thread(target=_loop_schedule, daemon=True)
    t.start()
    _scheduler_started = True
