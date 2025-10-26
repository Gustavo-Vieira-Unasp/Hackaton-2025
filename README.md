# Hackaton
## Membros
- Gustavo Vieira
- Caue Carvalho

# Requirements
. Baixar o SDK do Flutter

Vai no site do Flutter → botão de download para Windows (arquivo .zip).

Arquivo vem tipo flutter_windows_x.x.x-stable.zip.

⚠ Se você não quiser abrir navegador agora: não tem problema, mas você vai precisar desse zip oficial do Flutter. É ele que contém o SDK.

Extrair o Flutter para uma pasta fixa

Cria uma pasta direta no C:, por exemplo:

C:\src\flutter
(Evita colocar dentro de C:\Users\seuUsuario\Downloads ou dentro de pasta com espaço no nome.)

Extrai o conteúdo do .zip lá dentro.
No final você deve ter:

C:\src\flutter\bin

C:\src\flutter\examples
etc.
Isso é pra você conseguir usar o comando flutter no terminal de qualquer pasta.

Aperta Win e digita: Variáveis de Ambiente

abre “Editar as variáveis de ambiente do sistema”.

Clica em Variáveis de Ambiente...

Na parte de baixo (Variáveis do sistema), seleciona Path → Editar.

Clica em Novo e cola:

C:\src\flutter\bin


Dá OK em tudo até fechar.

Fecha qualquer terminal/PowerShell que já estava aberto e abre um novo.

Testa:

flutter --version


Se aparecer a versão do Flutter em vez de “comando não reconhecido”, o PATH está certo.

7. Criar e rodar o primeiro projeto

Ainda no terminal/powershell:

flutter create meu_app
cd meu_app
flutter run -d chrome
https://www.youtube.com/watch?v=Vkm0O4B-vts&t=1992s (video de exemplo flutter + python)
https://docs.flutter.dev/get-started/quick
https://developer.android.com/studio?hl=pt-br (nao é necessario para todos)
flask ou fastapi

Flutter (atual)
import 'package:flutter/material.dart';

Flutter (quando chamar API)
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

FastAPI backend (atual) (pode ser flask)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

1-FastAPI backend (quando tiver entrada de dados / modelos) (pode ser flask)
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
