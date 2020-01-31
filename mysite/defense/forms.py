from django import forms

class TestForm(forms.Form):
    solo_tackles = forms.DecimalField(label='Solo Tackles')
    ast_tackles = forms.DecimalField(label='Assist Tackles')
    sacks = forms.DecimalField(label='Sacks')
    interceptions = forms.DecimalField(label='Ints')
    ffb = forms.DecimalField(label='Force Fb')


class Customized_Tables(forms.Form):
    games = forms.BooleanField()
    games_started = forms.BooleanField()
    solo_tackles = forms.BooleanField()
    asst_tackles = forms.BooleanField()
    tackle_for_loss = forms.BooleanField()
    sacks = forms.BooleanField()
    qb_hits = forms.BooleanField()
    interceptions = forms.BooleanField()
    pass_def = forms.BooleanField()
    forced_fumble = forms.BooleanField()
    fumble_recovery = forms.BooleanField()
    td = forms.BooleanField()
