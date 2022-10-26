from django import forms


class CarpForm(forms.Form):
    name            = forms.CharField(max_length=50, label="Nome do Piloto")
    trigram         = forms.CharField(max_length=3, label="Trigrama")

    drop_height     = forms.IntegerField(label="ALTURA do lançamento (ft)")
    terrain_alt     = forms.IntegerField(label="ALTITUDE da ZL (ft)")
    point_of_impact = forms.IntegerField(label="ALTITUDE do Ponto de Impacto (ft)")

    pressure        = forms.IntegerField(label="Pressão (hPa)")
    temperature     = forms.FloatField(label="Temperatura (ºC)")

    speed           = forms.IntegerField(label="Velocidade (kt)")
    mag_course      = forms.IntegerField(label="Eixo de Lançamento (º)")

    # DADOS BALÍSTICOS
    chute_selection = forms.ChoiceField(choices=(
        (1, "T-10 AC/RAC"),
        (2, "T-10 C/D, MC1-1C, RALC"),
        (3, "ASA"),
        (4, "G11 A, G12 D"),
        (5, "G13, G14"),
        (6, "STAB")
    ), initial=1, label="Tipo de Paraquedas")
    chute_amount      = forms.IntegerField(label="Quantidade de Paraquedas", initial=1)
    rate_of_fall      = forms.FloatField(label="Rate of Fall (RF)", initial=14.5)
    vertical_distance = forms.IntegerField(label="Vertical Distance (VD)", initial=180)
    dec_quocient      = forms.FloatField(label="Deceleration Quocient (DC)", initial=1.6)
    tfc               = forms.FloatField(label="Time of Fall Constant (TFC)", initial=5.4)
    exit_time         = forms.FloatField(label="Exit Time (ET)", initial=0.2)

    measure_unit      = forms.ChoiceField(choices=(
        ("M", "Metros (m)"),
        ("YD", "Jardas (yd)")
    ), label="Unidade de Medida", initial="M")

