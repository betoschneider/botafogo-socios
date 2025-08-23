import time
from extrair_socios import extrair_e_salvar

INTERVALO_MINUTOS = 360

while True:
    extrair_e_salvar()
    time.sleep(INTERVALO_MINUTOS * 60)