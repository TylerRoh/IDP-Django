from django import forms

class TestForm(forms.Form):
    solo_tackles = forms.DecimalField(label='Solo Tackles')
    ast_tackles = forms.DecimalField(label='Assist Tackles')
    sacks = forms.DecimalField(label='Sacks')
    interceptions = forms.DecimalField(label='Ints')
    ffb = forms.DecimalField(label='Force Fb')


class Customized_Tables(forms.Form):
    games = forms.BooleanField(required=False)
    games_started = forms.BooleanField(required=False)
    solo_tackles = forms.BooleanField(required=False)
    asst_tackles = forms.BooleanField(required=False)
    tackle_for_loss = forms.BooleanField(required=False)
    sacks = forms.BooleanField(required=False)
    qb_hits = forms.BooleanField(required=False)
    interceptions = forms.BooleanField(required=False)
    pass_def = forms.BooleanField(required=False)
    forced_fumble = forms.BooleanField(required=False)
    fumble_recovery = forms.BooleanField(required=False)
