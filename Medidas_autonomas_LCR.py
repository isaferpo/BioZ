import time
import os
import datetime
import csv
import pyvisa
import winsound
import speech_recognition as sr

def audio_message(text: str):
    """Ejecuta el sintetizador de voz a través de PowerShell (Text-to-Speech)"""
    cmd = f'PowerShell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\');"'
    os.system(cmd)

def escuchar_voz(mensaje_consola: str = "[👂 Escuchando...]", timeout: int = 5) -> str:
    """Activa el micrófono y reconoce la voz del usuario (Speech-to-Text)"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[🎙️ Ajustando ruido de fondo...]")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        winsound.Beep(600, 200) # Pitido corto para avisar que ya está escuchando
        print(mensaje_consola) # <- Mensaje personalizable
        
        try:
            # Subimos phrase_time_limit a 5 para frases más largas
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5) 
            texto = recognizer.recognize_google(audio, language="es-ES").lower()
            print(f"> Has dicho: '{texto}'")
            return texto
        except sr.WaitTimeoutError:
            print("[❌] Tiempo de espera agotado. No se detectó voz.")
            return ""
        except sr.UnknownValueError:
            print("[❌] No se ha entendido el audio.")
            return ""
        except sr.RequestError as e:
            print(f"[❌] Error en el servicio de reconocimiento: {e}")
            return ""
def solicitar_nombre() -> str:
    """Solicita el ID por teclado y genera el nombre del archivo"""
    nomin = input("Introduce el ID del componente (teclado): ").strip()
    if not nomin:
        nomin = "Id"
    now = datetime.datetime.now()
    return f"{nomin}_{now.hour:02d}_{now.minute:02d}.csv"

def comando(instr, cmd: str, *args) -> str:
    """Envía un comando o realiza una consulta al instrumento VISA"""
    if not instr:
        raise Exception("No hay interfaz especificada.")
    
    cmdc = cmd % args if args else cmd
    # instr.clear()
    
    if cmdc.endswith('?'):
        return instr.query(cmdc).strip()
    else:
        instr.write(cmdc)
        return ""

def trigger_lcr_temp(instr) -> tuple:
    """Realiza el barrido de frecuencias y la extracción de datos"""
    freqs = [20, 50, 100, 200, 500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3, 100e3, 200e3, 500e3, 1e6, 2e6]
    zimp, phs, vac, iac = [], [], [], []
    
    comando(instr, 'TRIG:SOUR BUS')
    comando(instr, 'DISP:PAGE MEAS')
    
    print("\n[ Realizando barrido...]")
    for f in freqs:
        comando(instr, f':FREQ {f:g}')
        comando(instr, ':TRIG:IMM')
        
        res = comando(instr, ':FETC?')
        res_split = res.split(',')
        zimp.append(float(res_split[0]))
        phs.append(float(res_split[1]))
        
        vac.append(float(comando(instr, ':FETC:SMON:VAC?')))
        iac.append(float(comando(instr, ':FETC:SMON:IAC?')))
        
    winsound.Beep(500, 500)
    time.sleep(0.5)
    winsound.Beep(1000, 250)
    
    return zimp, phs, freqs, vac, iac

def guardar_datos(nomdoc: str, freqs, zimp, phs, vac, iac):
    """Guarda las 5 columnas en un CSV"""
    with open(nomdoc, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Freq(Hz)', 'Z(Ohm)', 'Phase(deg)', 'Vac(V)', 'Iac(A)']) # Encabezados
        for f, z, p, v, i in zip(freqs, zimp, phs, vac, iac):
            writer.writerow([f, z, p, v, i])

if __name__ == '__main__':
    print('==== Sistema de Medida Autónomo LCR ====')
    
    # 1. Inicialización del equipo
    try:
        rm = pyvisa.ResourceManager()
        visadev_obj = "USB0::0x2A8D::0x2F01::MY46620824::0::INSTR"
        instr = rm.open_resource(visadev_obj)
        instr.timeout = 120000 
        print("Equipo detectado:", comando(instr, '*IDN?'))
    except Exception as e:
        print(f"Error de conexión con el LCR: {e}")
        exit()

    # 2. Bucle principal interactivo
    while True:
        # Pide ID por teclado (hacerlo por voz es propenso a errores al deletrear)
        audio_message('Por favor, escribe el identificador del componente en la consola.')
        nomdoc = solicitar_nombre()
        
       # Bucle de confirmación de voz para arrancar
        while True:
            audio_message("Cuando estés listo, di 'comenzar medidas' para arrancar, o di 'cancelar'.")
            respuesta = escuchar_voz("[👂 Escuchando... Di 'comenzar medidas' o 'cancelar']")
            
            if "comenzar" in respuesta and "medidas" in respuesta:
                audio_message('Iniciando medida. Por favor, no toques los contactos.')
                start_time = time.perf_counter() 
                
                # Ejecutar medida
                zimp, phs, freqs, vac, iac = trigger_lcr_temp(instr)
                
                # Guardar y reportar
                guardar_datos(nomdoc, freqs, zimp, phs, vac, iac)
                tiempo = time.perf_counter() - start_time
                print(f"[✅ Guardado] Archivo: {nomdoc} ({tiempo:.2f} s)")
                audio_message('Medida concluida y guardada correctamente.')
                break
                
            elif "cancelar" in respuesta:
                audio_message('Medida cancelada. Esperando confirmación.')
                time.sleep(2) # Espera un poco antes de volver a preguntar
            else:
                audio_message('No te he entendido bien. Por favor, repite.')
        
        # Preguntar si se desea continuar con otro componente
        audio_message('¿Deseas medir un componente nuevo? Di continuar o finalizar.')
        continuar = escuchar_voz("[👂 Escuchando... Di 'continuar' o 'finalizar']")
        
        if "finalizar" in continuar:
            audio_message('Apagando el sistema. Hasta la vista.')
            break
        elif "continuar" not in continuar:
             audio_message('Ante la duda, asumiré que quieres parar. Apagando el sistema.')
             break
        
        # Preguntar si se desea continuar con otro componente
        audio_message('¿Deseas medir un componente nuevo? Responde sí o no.')
        continuar = escuchar_voz()
        if "no" in continuar:
            audio_message('Apagando el sistema. Hasta la vista.')
            break
        elif "sí" not in continuar and "si" not in continuar:
             audio_message('Ante la duda, asumiré que no. Apagando el sistema.')
             break

    instr.close()
    print("Sesión Finalizada")
