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
    estres_externo = 0.02 * (turno / turns) # Aumentamos un poco el estrés base
    influencia_pareja = 0.1 * (partner['RC'] - agent['RC']) # Beta de influencia
    
    # El cambio en C_Epi ahora incluye la influencia de la pareja
    delta_C_Epi = (estres_externo + influencia_pareja) * agent['RC'] * (1 - agent['FP'])
    
    if delta_C_Epi > 0: # Solo se suma el desgaste, no se "cura" por la influencia
        agent['C_Epi'] += delta_C_Epi
    
    if agent['C_Epi'] > 1.5: agent['C_Epi'] = 1.5 # Permitimos un C_Epi mayor

def alpha_NKF(turno, agent_RC):
    if turno < 520: return 0.0
    # El efecto es más potente si la RC es alta (más margen de mejora)
    eficacia_base = 0.4 
    return eficacia_base * (1 + agent_RC) / (1 + math.exp(-0.02 * (turno - 520)))

def actualizar_RC(agent, turno):
    if turno >= 520:
        reduccion_nkf = 0.005 * alpha_NKF(turno, agent['RC'])
        agent['RC'] -= reduccion_nkf
    if agent['RC'] < 0.1: agent['RC'] = 0.1

def calcular_Edad_bio(agent, Edad_cron, turno):
    alpha = alpha_NKF(turno, agent['RC'])
    return (Edad_cron / agent['AE']) * (1 + agent['C_Epi']) * (1 - alpha)

def update_loop():
    global turno, Edad_cron
    
    # Actualizar estado de Alex
    actualizar_C_Epi(Alex, Brillith, turno)
    actualizar_RC(Alex, turno)
    Edad_cron = Edad_cron_inicial + (Edad_cron_final - Edad_cron_inicial) * (turno / turns)
    Alex['Edad_bio'] = calcular_Edad_bio(Alex, Edad_cron, turno)

    # Actualizar estado de Brillith
    actualizar_C_Epi(Brillith, Alex, turno)
    actualizar_RC(Brillith, turno)
    Brillith['Edad_bio'] = calcular_Edad_bio(Brillith, Edad_cron, turno)

    print(f"Turno {turno}: Alex Edad_bio: {Alex['Edad_bio']:.2f}, RC: {Alex['RC']:.2f} | Brillith Edad_bio: {Brillith['Edad_bio']:.2f}, RC: {Brillith['RC']:.2f}")

async def main():
    global turno
    setup()
    Alex['name'], Brillith['name'] = 'Alex', 'Brillith'
    turno = 0
    print("Iniciando Simulación: Matrimonio Entrópico")
    while turno < turns:
        update_loop()
        turno += 1
        # await asyncio.sleep(1.0 / FPS) # Descomentar para visualización en tiempo real

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        # asyncio.run(main()) # Descomentar para visualización en tiempo real
        # Ejecución síncrona para obtener resultados rápidos
        turno = 0
        setup()
        while turno < turns:
            update_loop()
            turno += 1