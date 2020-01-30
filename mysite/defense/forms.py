from django import forms

class TestForm(forms.Form):
    solo_tackles = forms.DecimalField(label='Solo Tackles')
    ast_tackles = forms.DecimalField(label='Assist Tackles')
    sacks = forms.DecimalField(label='Sacks')
    interceptions = forms.DecimalField(label='Ints')
    ffb = forms.DecimalField(label='Force Fb')
