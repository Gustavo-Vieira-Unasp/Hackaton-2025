from django.shortcuts import render, redirect
from .forms import ParticipacaoForm

def form(request):
    if request.method == 'POST':
        form = ParticipacaoForm(request.POST)
        if form.is_valid():
            escolha = form.cleaned_data['tipo_participacao']
            
            print(f"O usuário escolheu: {escolha}")

            return redirect('pagina_de_sucesso')
    else:
        form = ParticipacaoForm()
        
    return render(request, 'form.html', {'form': form})