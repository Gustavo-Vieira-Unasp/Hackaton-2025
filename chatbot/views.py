from django.http import HttpResponse
from .tasks import LOG_BUFFER

def status(request):
    """
    Mostra o log recente do bot (últimas ~200 linhas).
    """

    if not LOG_BUFFER:
        conteudo = "Nenhum evento ainda. O bot pode estar aguardando o horário agendado."
    else:
        conteudo = "\n".join(LOG_BUFFER)

    html = f"""
    <html>
    <head>
        <title>Status do Bot</title>
        <style>
            body {{
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
                padding: 2rem;
            }}
            .card {{
                background-color: #1e293b;
                border-radius: 0.5rem;
                padding: 1rem 1.5rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.6);
                max-width: 900px;
                margin: 0 auto;
            }}
            h1 {{
                font-size: 1.25rem;
                font-weight: 600;
                color: #38bdf8;
                margin: 0 0 1rem 0;
            }}
            .hint {{
                font-size: 0.8rem;
                color: #94a3b8;
                margin-bottom: 1rem;
            }}
            pre {{
                background-color: #0f172a;
                border-radius: 0.5rem;
                padding: 1rem;
                max-height: 70vh;
                overflow-y: auto;
                white-space: pre-wrap;
                word-break: break-word;
                font-size: 0.9rem;
                line-height: 1.4rem;
                border: 1px solid #334155;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Status do Bot de WhatsApp</h1>
            <div class="hint">
                Esse painel mostra o que o bot fez recentemente: tentativas de envio,
                bloqueios de horário comercial, erros, etc.
            </div>
            <pre>{conteudo}</pre>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html)
