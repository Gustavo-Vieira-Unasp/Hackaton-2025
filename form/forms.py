from django import forms

TIPO_PARTICIPACAO_CHOICES = [
    ('SOZINHO', 'Estou sozinho(a)'),
    ('GRUPO', 'Estamos em grupo'),
]

class ParticipacaoForm(forms.Form):
    tipo_participacao = forms.ChoiceField(
        choices=TIPO_PARTICIPACAO_CHOICES,
        widget=forms.RadioSelect,
        label="Como você está participando?"
    )
    
    quantidade_pessoas = forms.IntegerField(
        min_value=2, 
        required=False,
        label="Quantas pessoas há no seu grupo? (Mínimo 2)",
        widget=forms.NumberInput(attrs={'placeholder': 'Digite o número', 'min': 2})
    )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_participacao')
        quantidade = cleaned_data.get('quantidade_pessoas')

        if tipo == 'GRUPO':
            if not quantidade:
                self.add_error('quantidade_pessoas', 'Por favor, informe o número de pessoas no grupo (mínimo 2).')
            elif quantidade < 2: 
                 self.add_error('quantidade_pessoas', 'A participação em grupo deve ter no mínimo 2 pessoas.')
        
        elif tipo == 'SOZINHO':
             cleaned_data['quantidade_pessoas'] = 1
             
        return cleaned_data