import pyvisa
import time

def comando_seguro(instr, cmd, *args):
    """Envía un comando y verifica si hubo errores en el instrumento."""
    if args:
        cmd_final = cmd % args
    else:
        cmd_final = cmd
        
    if cmd_final.strip().endswith('?'):
        res = instr.query(cmd_final).strip()
    else:
        instr.write(cmd_final)
        res = ""
    
    # Verificación de errores según el manual (capítulo de comandos SYSTem)
    error = instr.query(":SYST:ERR?").strip()
    if '+0,"No error"' not in error:
        print(f"ERROR en comando '{cmd_final}': {error}")
    
    return res

# --- Configuración de la conexión ---
rm = pyvisa.ResourceManager()
# Cambia esta dirección por la de tu equipo
visadevObj = "USB0::0x2A8D::0x2F01::MY46620824::0::INSTR"

try:
    # 1. Apertura con terminadores explícitos según el manual
    instr = rm.open_resource(visadevObj, read_termination='\n', write_termination='\n')
    instr.timeout = 30000 
    
    print("Inicializando equipo...")
    
    # 2. Reset y sincronización (Esperar a que el equipo esté listo)
    instr.write("*RST")
    instr.query("*OPC?") # El script se detiene aquí hasta que el reset termine
    
    # 3. Configuración de parámetros
    comando_seguro(instr, ":FUNC:IMP:TYPE ZTD")   # Impedancia y Fase
    comando_seguro(instr, ":VOLT 1.0")            # 1 Voltio
    
    # 4. Configuración de la lista de frecuencias
    freqs = [20, 100, 1000, 10000, 50000, 100000, 1000000, 2000000]
    freq_str = ",".join(map(str, freqs))
    
    print(f"Cargando lista de {len(freqs)} frecuencias...")
    comando_seguro(instr, "LIST:FREQ %s", freq_str)
    instr.query("*OPC?") # Crucial: esperar a que la lista se cargue en memoria
    
    # 5. Promediado (Averaging)
    # LONG con 16 promedios toma tiempo. 
    # El manual advierte que esto aumenta el tiempo de respuesta.
    comando_seguro(instr, ":APER LONG, 16")
    
    print("Configuración completada con éxito.")

except Exception as e:
    print(f"Fallo en la comunicación: {e}")
finally:
    if 'instr' in locals():
        instr.close()