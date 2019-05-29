
import rpy2.robjects as robjects

def limpiarCSV(ruta):
    r_source = robjects.r['source']
    r_source('pruebaScript.R')
    print('CSV limpio.')
    
    return
