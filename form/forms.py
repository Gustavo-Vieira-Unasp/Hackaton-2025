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