import pandas as pd


"""
Consideraciones:
- Si ha habido cambio de hora, me cargo esa hora de más.
- Si falta algún dato entre las fechas del consumo, me lo invento
"""
def limpiarCSV(df):
    df=df[df.Hora != 25]
    df.Fecha=pd.to_datetime(df['Fecha'],format="%d/%m/%Y") + pd.to_timedelta(df.Hora-1, unit='h')
    df.index=pd.to_datetime(df['Fecha'], format="%m/%d/%Y %I:%M:%S")
    df = df.drop(['CUPS', 'Fecha', 'Hora', 'Metodo_obtencion'], axis=1)
    df = df.resample('H').interpolate(method='linear')
    return df


"""
Consideraciones:
- Los valores que se pasen de los quantiles definidos, se capan.
"""
def arreglarDatosCSV(df):
    filt_df = df.loc[:, 'Consumo_kWh']
    low = .05
    high = .95
    quant_df_low = filt_df.quantile(low)
    quant_df_high = filt_df.quantile(high)

    for index, row in df.iterrows():
        if row['Consumo_kWh'] < quant_df_low:
            row['Consumo_kWh'] = quant_df_low
        elif row['Consumo_kWh'] > quant_df_high:
            row['Consumo_kWh'] = quant_df_high
    return df


"""
if:
- Los ficheros no tienen consumos solapados.
- No se garantiza que donde acabe uno justo empiece el otro (por lo que en ese caso puede que algo estalle más adelante).
elif:
- Los ficheros tienen consumos solapados, parcial o totalmente.
else:
- 
"""
def unirConsumos(df_1, df_2):
    ini1 = df_1.first_valid_index()
    fin1 = df_1.last_valid_index()
    ini2 = df_2.first_valid_index()
    fin2 = df_2.last_valid_index()

    if (((ini1 < ini2) and (fin1 < ini2)) or ((ini2 < ini1) and (fin2 < ini1))):
        print('Ambos consumos están separados, por delante o por detrás. Aplicando pandas.concat().')
        return 0
    elif ((fin1 > ini2) or (fin2 > ini1)):
        print('Los consumos se solapan, parcial o totalmente. Aplicando combine_first()')
        return 0
    else:
        print('Caso no considerado. Actuar por defecto. pandas.concat().')
        return 1

    return 0




"""
import rpy2.robjects as robjects
def limpiarCSV(ruta):
    r_source = robjects.r['source']
    r_source('pruebaScript.R')
    print('CSV limpio.')
    
    return
"""