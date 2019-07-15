



function mostrarConsumoHorario(){
    document.getElementById('graf-consumo-horario').style.display = 'block';
    document.getElementById('graf-consumo-diario').style.display = 'none';
    document.getElementById('graf-consumo-semanal').style.display = 'none';
    document.getElementById('graf-consumo-mensual').style.display = 'none';
}

function mostrarConsumoDiario(){
    document.getElementById('graf-consumo-horario').style.display = 'none';
    document.getElementById('graf-consumo-diario').style.display = 'block';
    document.getElementById('graf-consumo-semanal').style.display = 'none';
    document.getElementById('graf-consumo-mensual').style.display = 'none';
}

function mostrarConsumoSemanal(){
    document.getElementById('graf-consumo-horario').style.display = 'none';
    document.getElementById('graf-consumo-diario').style.display = 'none';
    document.getElementById('graf-consumo-semanal').style.display = 'block';
    document.getElementById('graf-consumo-mensual').style.display = 'none';
}

function mostrarConsumoMensual(){
    document.getElementById('graf-consumo-horario').style.display = 'none';
    document.getElementById('graf-consumo-diario').style.display = 'none';
    document.getElementById('graf-consumo-semanal').style.display = 'none';
    document.getElementById('graf-consumo-mensual').style.display = 'block';
}
