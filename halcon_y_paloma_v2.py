import asyncio
import platform
import random
import math

FPS = 60
turns = 1040
Edad_cron_inicial = 40
Edad_cron_final = 60 # 20 años de simulación

def setup():
    global Alex, Brillith
    Alex = {'AE': 0.81, 'RC': 0.8, 'C_Epi': 0.0, 'FP': 0.9, 'Iq': 0.9, 'Edad_bio': (Edad_cron_inicial / 0.81)}
    Brillith = {'AE': 0.49, 'RC': 0.4, 'C_Epi': 0.0, 'FP': 0.7, 'Iq': 0.7, 'Edad_bio': (Edad_cron_inicial / 0.49)}

def actualizar_C_Epi_competitivo(agent, opponent, turno):
    # En un juego competitivo, el estrés es mayor y la RC del oponente es una fuente de estrés.
    estres_base = 0.05 * (turno / turns)
    estres_conflicto = 0.2 * opponent['RC'] 
    
    delta_C_Epi = (estres_base + estres_conflicto) * agent['RC'] * (1 - agent['FP'])
    
    agent['C_Epi'] += delta_C_Epi
    if agent['C_Epi'] > 2.0: agent['C_Epi'] = 2.0

def alpha_NKF_tactico(turno, agent_RC, opponent_RC):
    if turno < 520: return 0.0
    # El efecto es mucho más potente para revertir el daño agudo del conflicto
    eficacia_base = 0.8 
    # La táctica es más efectiva si el oponente es más rígido
    ventaja_tactica = 0.2 * (opponent_RC - agent_RC)
    
    alpha_total = eficacia_base + ventaja_tactica
    if alpha_total > 0.95: alpha_total = 0.95 # Cap al 95%
    if alpha_total < 0: alpha_total = 0
    return alpha_total

def actualizar_RC_competitivo(agent, turno):
    if turno >= 520:
        reduccion_nkf = 0.01 * alpha_NKF_tactico(turno, agent['RC'], 0.5) # Asumimos un oponente promedio para la mejora personal
        agent['RC'] -= reduccion_nkf
    if agent['RC'] < 0.1: agent['RC'] = 0.1


def calcular_Edad_bio(agent, Edad_cron, turno, opponent):
    alpha = alpha_NKF_tactico(turno, agent['RC'], opponent['RC'])
    return (Edad_cron / agent['AE']) * (1 + agent['C_Epi']) * (1 - alpha)

def update_loop():
    global turno, Edad_cron

    # Actualizar estado de Alex
    actualizar_C_Epi_competitivo(Alex, Brillith, turno)
    actualizar_RC_competitivo(Alex, turno)
    Edad_cron = Edad_cron_inicial + (Edad_cron_final - Edad_cron_inicial) * (turno / turns)
    Alex['Edad_bio'] = calcular_Edad_bio(Alex, Edad_cron, turno, Brillith)

    # Actualizar estado de Brillith
    actualizar_C_Epi_competitivo(Brillith, Alex, turno)
    actualizar_RC_competitivo(Brillith, turno)
    Brillith['Edad_bio'] = calcular_Edad_bio(Brillith, Edad_cron, turno, Alex)

    print(f"Turno {turno}: Alex Edad_bio: {Alex['Edad_bio']:.2f}, RC: {Alex['RC']:.2f} | Brillith Edad_bio: {Brillith['Edad_bio']:.2f}, RC: {Brillith['RC']:.2f}")

async def main():
    global turno
    setup()
    turno = 0
    print("Iniciando Simulación: Halcón y Paloma")
    while turno < turns:
        update_loop()
        turno += 1
        # await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        # asyncio.run(main())
        # Ejecución síncrona para obtener resultados rápidos
        turno = 0
        setup()
        while turno < turns:
            update_loop()
            turno += 1