import asyncio
import platform
import random
import math

FPS = 60
turns = 1040
Edad_cron_inicial = 40
Edad_cron_final = 60

def setup():
    global Alex, Brillith
    Alex = {'AE': 0.81, 'RC': 0.7, 'FP': 0.9, 'Iq': 0.9, 'C_Epi': 0.0, 'Edad_bio': (Edad_cron_inicial / 0.81)}
    Brillith = {'AE': 0.49, 'RC': 0.4, 'FP': 0.7, 'Iq': 0.7, 'C_Epi': 0.0, 'Edad_bio': (Edad_cron_inicial / 0.49)}

def actualizar_C_Epi(agent, partner, turno):
    estres_externo = 0.02 * (turno / turns)
    influencia_pareja = 0.1 * (partner['RC'] - agent['RC'])
    
    delta_C_Epi = (estres_externo + influencia_pareja) * agent['RC'] * (1 - agent['FP'])
    
    if delta_C_Epi > 0:
        agent['C_Epi'] += delta_C_Epi
    
    if agent['C_Epi'] > 1.5: agent['C_Epi'] = 1.5

def alpha_NKF(turno, agent_RC, partner_alpha_effect):
    if turno < 520: return 0.0
    base = 0.4 / (1 + math.exp(-0.02 * (turno - 520)))
    # El efecto cooperativo se suma al efecto base
    return base + partner_alpha_effect

def actualizar_RC(agent, turno):
    if turno >= 520:
        reduccion_nkf = 0.005 * alpha_NKF(turno, agent['RC'], 0) # La mejora personal base
        agent['RC'] -= reduccion_nkf
    if agent['RC'] < 0.1: agent['RC'] = 0.1

def calcular_Edad_bio(agent, Edad_cron, turno, partner):
    # El efecto cooperativo del alpha del partner
    partner_alpha_effect = 0.1 * alpha_NKF(turno, partner['RC'], 0)
    alpha = alpha_NKF(turno, agent['RC'], partner_alpha_effect)
    return (Edad_cron / agent['AE']) * (1 + agent['C_Epi']) * (1 - alpha)

def update_loop():
    global turno, Edad_cron
    
    # Calcular estados para el turno actual antes de actualizarlos
    Alex_old_RC = Alex['RC']
    Brillith_old_RC = Brillith['RC']

    Edad_cron = Edad_cron_inicial + (Edad_cron_final - Edad_cron_inicial) * (turno / turns)

    # Actualizar estado de Alex
    actualizar_C_Epi(Alex, Brillith, turno)
    actualizar_RC(Alex, turno)
    Alex['Edad_bio'] = calcular_Edad_bio(Alex, Edad_cron, turno, Brillith)

    # Actualizar estado de Brillith usando los valores antiguos de Alex para la interacción del turno
    Brillith_temp = Brillith.copy()
    Brillith_temp['RC'] = Brillith_old_RC
    Alex_temp = Alex.copy()
    Alex_temp['RC'] = Alex_old_RC
    actualizar_C_Epi(Brillith, Alex_temp, turno)
    actualizar_RC(Brillith, turno)
    Brillith['Edad_bio'] = calcular_Edad_bio(Brillith, Edad_cron, turno, Alex_temp)

    print(f"Turno {turno}: Alex Edad_bio: {Alex['Edad_bio']:.2f}, RC: {Alex['RC']:.2f} | Brillith Edad_bio: {Brillith['Edad_bio']:.2f}, RC: {Brillith['RC']:.2f}")

async def main():
    global turno
    setup()
    turno = 0
    print("Iniciando Simulación: Matrimonio Entrópico (Cooperativo)")
    while turno < turns:
        update_loop()
        turno += 1
        await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__":
    turno = 0
    setup()
    while turno < turns:
        update_loop()
        turno += 1