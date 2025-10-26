from django import forms

TIPO_PARTICIPACAO_CHOICES = [
    ('SOZINHO', 'Estou sozinho(a)'),
    ('GRUPO', 'Estamos em grupo'),
]

class ParticipacaoForm(forms.Form):
    """
    Formulário para registrar a participação (individual ou grupo).
    """
    tipo_participacao = forms.ChoiceField(
        choices=TIPO_PARTICIPACAO_CHOICES,
        widget=forms.RadioSelect,
        label="Como você está participando?"
    )
    
    quantidade_pessoas = forms.IntegerField(
        min_value=1,
        required=False,
        label="Quantas pessoas há no seu grupo?",
        widget=forms.NumberInput(attrs={'placeholder': 'Digite o número'})
    )

    def clean(self):
        """
        Garante que o campo 'quantidade_pessoas' seja preenchido se 'GRUPO' for escolhido.
        """
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_participacao')
        quantidade = cleaned_data.get('quantidade_pessoas')

        if tipo == 'GRUPO':
            if not quantidade:
                self.add_error('quantidade_pessoas', 'Este campo é obrigatório para participação em grupo.')
            
        elif tipo == 'SOZINHO':
             cleaned_data['quantidade_pessoas'] = 1
             
        return cleaned_data