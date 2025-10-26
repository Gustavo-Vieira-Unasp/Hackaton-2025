from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ParticipacaoForm

def form(request):
    if request.method == 'POST':
        form = ParticipacaoForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            tipo = data['tipo_participacao']
            quantidade = data['quantidade_pessoas']
            
            print(f"Dados Recebidos: Tipo={tipo}, Quantidade={quantidade}")
            
            return redirect(reverse('form:sucesso'))
            
    else:
        form = ParticipacaoForm()
        
    return render(request, 'form.html', {'form': form})

def sucesso(request):
    return render(request, 'sucesso.html')