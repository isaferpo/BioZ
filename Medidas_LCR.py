import time
import os
import datetime
import csv
import pyvisa
import winsound

def audio_message(text: str):
    """Ejecuta el sintetizador de voz a través de PowerShell"""
    # Usamos f-strings para inyectar la variable directamente en el texto
    cmd = f'PowerShell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\');"'
    os.system(cmd)

def solicitar_nombre(msj: str) -> str:
    """Solicita el ID y genera el nombre del archivo"""
    nomin = input(msj).strip()
    if not nomin:
        nomin = "Id"
    
    now = datetime.datetime.now()
    # f-strings con formato de dos dígitos (ej: 09 en lugar de 9 para los minutos)
    nomout = f"{nomin}{now.hour:02d}_{now.minute:02d}.csv"
    return nomout

def comando(instr, cmd: str, *args) -> str:
    """Envía un comando o realiza una consulta al instrumento VISA"""
    if not instr:
        raise Exception("SpectralM:InterfaceNotsent No interface specified.")
    
    cmdc = cmd % args if args else cmd  
    
    if cmdc.endswith('?'):
        return instr.query(cmdc).strip()
    else:
        instr.write(cmdc)
        return ""


def trigger_lcr_temp(instr):
    """Realiza el barrido de frecuencias y la extracción de datos"""
    freqs = [20, 50, 100, 200, 500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3, 100e3, 200e3, 500e3, 1e6, 2e6]
    
    zimp, phs, vac, iac = [], [], [], []
    
    comando(instr, 'TRIG:SOUR BUS')
    comando(instr, 'DISP:PAGE MEAS')
    
    audio_message('Realizando medidas punto a punto. Por favor, espera.')
    
    for f in freqs:
        # 1. Configurar la frecuencia usando f-strings
        comando(instr, f':FREQ {f:g}')
        
        # 2. Disparar medición
        comando(instr, ':TRIG:IMM')
        
        # 3. Leer Impedancia (Z) y Fase (Theta)
        res = comando(instr, ':FETC?')
        res_split = res.split(',')
        zimp.append(float(res_split[0]))
        phs.append(float(res_split[1]))
        
        # 4. Leer Monitores de Voltaje y Corriente
        vac.append(float(comando(instr, ':FETC:SMON:VAC?')))
        iac.append(float(comando(instr, ':FETC:SMON:IAC?')))
        
    # Aviso sonoro
    winsound.Beep(500, 500)
    time.sleep(0.5)
    winsound.Beep(1000, 250)
    
    audio_message('Medida concluida')
    
    return zimp, phs, freqs, vac, iac

if __name__ == '__main__':
    start_time = time.perf_counter() 
    
    rm = pyvisa.ResourceManager()
    visadev_obj = "USB0::0x2A8D::0x2F01::MY46620824::0::INSTR"
    
    # CORREGIDO: Añadidos los terminadores de lectura y escritura
    instr = rm.open_resource(visadev_obj, read_termination='\n', write_termination='\n')
    
    print(comando(instr, '*IDN?'))
    instr.timeout = 120000 
    
    print('----- Generador de documento de salida -----')
    audio_message('Comenzando medida. Por favor, ve a la ventana de comando y teclea tu número identificador')
    nomdoc = solicitar_nombre('Id: ')
    
    zimp, phs, freqs, vac, iac = trigger_lcr_temp(instr)
    
    instr.close() 
    
    print(f"Tiempo transcurrido: {time.perf_counter() - start_time:.4f} segundos")
    
    with open(nomdoc, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Freq(Hz)', 'Z(Ohm)', 'Phase(deg)', 'Vac(V)', 'Iac(A)'])
        
        for f, z, p, v, i in zip(freqs, zimp, phs, vac, iac):
            writer.writerow([f, z, p, v, i])