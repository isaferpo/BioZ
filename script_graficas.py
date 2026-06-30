import csv
import matplotlib.pyplot as plt

def graficar_impedancia(archivo_csv: str):
    """Lee el CSV, filtra el overload y grafica |Z| vs Frecuencia"""
    freqs = []
    zimp = []
    
    try:
        with open(archivo_csv, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            for row in reader:
                try:
                    # Extraemos la frecuencia (columna 0) y la impedancia (columna 1)
                    f = float(row[0])
                    z = float(row[1])
                    
                    # Filtro de Overload: Ignoramos cualquier valor colosal (como 9e37 o 9.9e37)
                    # Usamos < 1e37 para evitar problemas de precisión con decimales flotantes
                    if z < 1e37:
                        freqs.append(f)
                        zimp.append(z)
                        
                except (ValueError, IndexError):
                    # Si la fila tiene texto (como los encabezados) o está vacía, la saltamos
                    continue
                    
    except FileNotFoundError:
        print(f"[❌] Error: No se ha encontrado el archivo '{archivo_csv}'.")
        return

    if not freqs:
        print("[⚠️] No se han encontrado datos válidos para graficar en el archivo.")
        return

    # --- Configuración de la Gráfica ---
    plt.figure(figsize=(10, 6))
    
    # Dibujamos los puntos y la línea
    plt.plot(freqs, zimp, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=6)
    
    # Ejes en escala logarítmica
    plt.xscale('log') 
    plt.yscale('log') # Opcional pero recomendado: Z también suele verse mejor en log
    
    # Etiquetas y título
    plt.title('Módulo de la Impedancia frente a Frecuencia', fontsize=14, fontweight='bold')
    plt.xlabel('Frecuencia (Hz)', fontsize=12)
    plt.ylabel('Impedancia |Z| (Ω)', fontsize=12)
    
    # Rejilla (grid) adaptada para escalas logarítmicas
    plt.grid(True, which="major", linestyle='-', linewidth=0.8, alpha=0.7)
    plt.grid(True, which="minor", linestyle='--', linewidth=0.5, alpha=0.5)
    
    # Ajusta los márgenes automáticamente para que no se corte el texto
    plt.tight_layout()
    
    # Muestra la ventana interactiva
    plt.show()

if __name__ == '__main__':
    print("==== Visor de Impedancia LCR ====")
    archivo = input("Introduce el nombre del archivo .csv (incluyendo la extensión): ").strip()
    
    graficar_impedancia(archivo)