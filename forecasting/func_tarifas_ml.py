

def calcular_costes_ml(df):

    costes_dict = {'T01':tarifa_ml_01(df),
                   'T02':tarifa_ml_02(df),
                   'T03':tarifa_ml_03(df),
                   }

    return costes_dict


def tarifa_ml_01(df):
    # Tarifa con discriminación por los fines de semana. Iberdrola
    df['weekday'] = df.index.dayofweek
    PRECIO_LABORAL = 0.19
    PRECIO_FINDE = 0.090
    coste_laboral = 0
    coste_finde = 0
    for index, row in df.iterrows():
        if row['weekday'] == 0 or 1 or 2 or 3 or 4:
            coste_laboral += PRECIO_LABORAL * row['Consumo_kWh']
        else:
            coste_finde += PRECIO_FINDE * row['Consumo_kWh']

    costeT01 = coste_laboral + coste_finde
    tarifa_dict = {'Nombre':'Finde', 'Coste':costeT01, 'Empresa':'Iberdrola'}
    return tarifa_dict


def tarifa_ml_02(df):
    # Tarifa de un único precio. Iberdrola
    PRECIO_UNICO=0.143889

    coste_unico = 0
    for index, row in df.iterrows():
        coste_unico += PRECIO_UNICO * row['Consumo_kWh']

    costeT02 = coste_unico

    tarifa_dict = {'Nombre': 'Unico', 'Coste': costeT02, 'Empresa': 'Iberdrola'}
    return tarifa_dict


def tarifa_ml_03(df):
    # Tarifa de un único precio. Endesa
    PRECIO_UNICO = 0.119893

    coste_unico = 0
    for index, row in df.iterrows():
        coste_unico += PRECIO_UNICO * row['Consumo_kWh']

    costeT03 = coste_unico

    tarifa_dict = {'Nombre': 'OneLuz', 'Coste': costeT03, 'Empresa': 'Endesa'}
    return tarifa_dict