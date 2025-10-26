from django.shortcuts import render
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from openpyxl import load_workbook, Workbook
import json


def _excel_para_lista_dict(arquivo_excel):
    """
    Lê um arquivo Excel enviado (InMemoryUploadedFile) e converte
    para uma lista de dicionários [{coluna: valor, ...}, ...]
    sem salvar no disco.
    """
    wb = load_workbook(arquivo_excel, data_only=True)
    ws = wb.active  # usa a primeira aba

    # primeira linha = cabeçalhos
    cabecalhos = [cell.value for cell in ws[1]]

    dados = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        linha_dict = {}
        for i, nome_coluna in enumerate(cabecalhos):
            linha_dict[nome_coluna] = row[i]
        dados.append(linha_dict)

    return dados


def _lista_dict_para_excel_bytes(lista_dict):
    """
    Recebe uma lista de dicionários (ex.: [{"nome": "Ana", "tel": "123"}, ...])
    Gera um .xlsx em memória (BytesIO) e retorna esse buffer.
    Nada é salvo em caminho fixo.
    """
    wb = Workbook()
    ws = wb.active

    if not lista_dict:
        # se lista vazia, gera planilha só com uma célula informativa
        ws.append(["(vazio)"])
    else:
        # Cabeçalho = chaves do primeiro dicionário
        cabecalhos = list(lista_dict[0].keys())
        ws.append(cabecalhos)

        # Linhas = valores
        for item in lista_dict:
            ws.append([item.get(coluna) for coluna in cabecalhos])

    # salvar em memória
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


@csrf_exempt
def excel_para_json_view(request):
    """
    [ENDPOINT 1] POST /upload-excel/
    Campo esperado: arquivo_excel (multipart/form-data)

    Retorna JSON com os dados lidos da planilha.
    """
    if request.method != "POST":
        return JsonResponse(
            {"erro": "Use método POST e envie arquivo_excel (.xlsx)."},
            status=405
        )

    if "arquivo_excel" not in request.FILES:
        return JsonResponse(
            {"erro": "Campo 'arquivo_excel' não foi enviado."},
            status=400
        )

    arquivo = request.FILES["arquivo_excel"]

    # Converte Excel -> lista de dicionários
    dados_convertidos = _excel_para_lista_dict(arquivo)

    # devolve JSON já pronto p/ o chatbot usar
    return JsonResponse(
        {
            "status": "ok",
            "timestamp": now().isoformat(),
            "linhas_lidas": len(dados_convertidos),
            "dados": dados_convertidos,
        },
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
        safe=False
    )


@csrf_exempt
def json_para_excel_view(request):
    """
    [ENDPOINT 2] POST /gerar-excel/
    Body esperado: JSON no corpo da requisição.
    Exemplo:
    [
        {"nome": "Ana", "telefone": "5511999999999", "data_visita": "2025-10-25"},
        {"nome": "Bruno", "telefone": "5511888888888", "data_visita": "2025-10-25"}
    ]

    Retorna: um arquivo .xlsx para download (Content-Disposition)
    sem escrever nada no disco.
    """
    if request.method != "POST":
        return JsonResponse(
            {"erro": "Use método POST e envie um JSON no corpo da requisição."},
            status=405
        )

    # tentar ler o corpo como JSON
    try:
        corpo_bytes = request.body  # raw body
        lista_dict = json.loads(corpo_bytes.decode("utf-8"))
        # lista_dict deve ser uma lista de dicionários
        if not isinstance(lista_dict, list):
            raise ValueError("O corpo precisa ser uma lista JSON de objetos.")
    except Exception as e:
        return JsonResponse(
            {"erro": f"JSON inválido: {str(e)}"},
            status=400
        )

    # Converte lista de dicts -> Excel em memória (BytesIO)
    buffer_excel = _lista_dict_para_excel_bytes(lista_dict)

    # Montar resposta HTTP com arquivo .xlsx
    resposta = HttpResponse(
        buffer_excel.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )

    # Sugerir um nome de arquivo pro download
    resposta["Content-Disposition"] = 'attachment; filename="dados_convertidos.xlsx"'

    return resposta


def conversor_status(request):
    """
    Endpoint simples só pra checar se o app está ativo.
    GET /  → retorna uma mensagem.
    (Opcional, mas útil pra teste rápido no navegador.)
    """
    return HttpResponse(
        "Conversor ativo. Use POST /upload-excel/ (Excel → JSON) "
        "ou POST /gerar-excel/ (JSON → Excel)."
    )
