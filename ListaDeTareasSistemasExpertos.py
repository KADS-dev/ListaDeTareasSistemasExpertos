import sqlite3
from datetime import datetime, timedelta

# Conexión a la base de datos SQLite
conn = sqlite3.connect('tareas.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''
          CREATE TABLE IF NOT EXISTS tareas (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              tipo TEXT,
              nombre TEXT,
              duracion_min INTEGER,
              duracion_max INTEGER,
              hora_limite TEXT,
              prioridad INTEGER,
              repetir_diariamente INTEGER
          )
          ''')
conn.commit()

def agregar_tarea():
    print("\nSeleccione el tipo de tarea:")
    print("1. Tarea Estática")
    print("2. Tarea Dinámica")
    tipo_tarea = input("Ingrese el número correspondiente al tipo de tarea: ")

    nombre = input("Ingrese el nombre de la tarea: ")

    if tipo_tarea == '1':  # Tarea Estática
        duracion_horas = int(input("Ingrese la duración en horas: "))
        duracion_minutos = int(input("Ingrese la duración en minutos: "))
        duracion_total = duracion_horas * 60 + duracion_minutos
        while(True):
            
            hora_inicio_horas = int(input("Ingrese la hora de inicio (formato de 24 horas, ej. 14 para las 2 PM): "))
            hora_inicio_minutos = int(input("Ingrese los minutos de inicio: "))
            hora_inicio = f"{hora_inicio_horas:02d}:{hora_inicio_minutos:02d}"
            if(hora_inicio_horas <= 23 and hora_inicio_minutos < 60):
                break
            print("hora de inicio no valida, ingrese otra...")
        print(hora_inicio)
        
        intercambio=datetime.now()
        hora_inicio = (hora_inicio)
        repetir_diariamente = input("¿Repetir diariamente? (si/no): ").lower() == 'si'
            
        # Calcular la hora de finalización para tareas estáticas
        hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M")
        hora_finalizacion_dt = hora_inicio_dt + timedelta(minutes=duracion_total)
        hora_finalizacion = hora_finalizacion_dt.strftime("%H:%M")

        # Insertar tarea en la base de datos
        c.execute("INSERT INTO tareas (tipo, nombre, duracion_min, duracion_max, hora_limite, prioridad, repetir_diariamente) "
                  "VALUES (?, ?, ?, NULL, ?, 11, ?)",
                  (tipo_tarea, nombre, duracion_total, (hora_finalizacion), repetir_diariamente))
        conn.commit()

    elif tipo_tarea == '2':  # Tarea Dinámica
        while(True):
            duracion_minima_horas = int(input("Ingrese la duración mínima en horas: "))
            duracion_minima_minutos = int(input("Ingrese la duración mínima en minutos: "))
            duracion_minima_total = duracion_minima_horas * 60 + duracion_minima_minutos
            if(duracion_minima_total < 24*60 - 1):
                break
            print("hora de inicio no valida, ingrese otra...")
        while(True):
            
            duracion_maxima_horas = int(input("Ingrese la duración máxima en horas: "))
            duracion_maxima_minutos = int(input("Ingrese la duración máxima en minutos: "))
            duracion_maxima_total = duracion_maxima_horas * 60 + duracion_maxima_minutos
            if(duracion_maxima_total < 24*60 - 1):
                break
            print("duracion maxima no valida, ingrese otra...")                        
            
        while(True):
            hora_limite_horas = int(input("Ingrese la hora límite (formato de 24 horas, ej. 18 para las 6 PM): "))
            hora_limite_minutos = int(input("Ingrese los minutos de la hora límite: "))
            hora_limite = f"{hora_limite_horas:02d}:{hora_limite_minutos:02d}"
            if(hora_limite_horas <= 23 and hora_limite_minutos <=59):
                break
            print("hora limite no valida, ingrese otra...")
        while(True):                
            prioridad = int(input("Ingrese la prioridad (1-10): "))
            if(prioridad < 11 and prioridad > 0):
                break
            print("error, ingrese un valor entre el 1 y el 10")
        repetir_diariamente = input("¿Repetir diariamente? (si/no): ").lower() == 'si'
            
        # Insertar tarea en la base de datos
        c.execute("INSERT INTO tareas (tipo, nombre, duracion_min, duracion_max, hora_limite, prioridad, repetir_diariamente) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (tipo_tarea, nombre, duracion_minima_total, duracion_maxima_total, hora_limite, prioridad, repetir_diariamente))
        conn.commit()

    else:
        print("Tipo de tarea no válido.")
        return

    print("Tarea agregada con éxito!")

def mostrar_tareas():
    # Mostrar tareas ordenadas por prioridad y hora de finalización
#####Hacer que se seleccionen las tareas que no tienen una hora límite tan corta.    
    c.execute("SELECT * FROM tareas WHERE hora_limite > ? ORDER BY prioridad DESC, hora_limite", (datetime.now().strftime("%H:%M"),))
    tareas = c.fetchall()
    print("\nLista de tareas:")
    for tarea in tareas:
        print(f"ID: {tarea[0]}, Tipo: {tarea[1]}, Nombre: {tarea[2]}, Duración Mínima: {tarea[3]} minutos, "
              f"Duración Máxima: {tarea[4]} minutos, Hora Límite: {tarea[5]}, Prioridad: {tarea[6]}, "
              f"Repetir diariamente: {tarea[7]}")

def eliminar_tarea():
    tarea_id = input("Ingrese el ID de la tarea que desea eliminar: ")

    # Obtener información de la tarea antes de eliminarla
    c.execute("SELECT * FROM tareas WHERE id=?", (tarea_id,))
    tarea = c.fetchone()

    # Eliminar la tarea de la base de datos
    c.execute("DELETE FROM tareas WHERE id=?", (tarea_id,))
    conn.commit()

    if tarea and tarea[7] == 1:  # Si la tarea debe repetirse diariamente
        # Calcular la hora de inicio para el día siguiente
        hora_limite_dt = datetime.strptime(tarea[5], "%H:%M")
        hora_limite_dt_siguiente = hora_limite_dt + timedelta(days=1)
        hora_limite_siguiente = hora_limite_dt_siguiente.strftime("%H:%M")

        # Insertar una nueva tarea para el día siguiente
        c.execute("INSERT INTO tareas (tipo, nombre, duracion_min, duracion_max, hora_limite, prioridad, repetir_diariamente) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (tarea[1], tarea[2], tarea[3], tarea[4], hora_limite_siguiente, tarea[6], tarea[7]))
        conn.commit()

    print("Tarea eliminada correctamente.")

def verificar_tareas_vencidas():
    now = datetime.now().strftime("%H:%M")
    c.execute("SELECT * FROM tareas WHERE hora_limite <= ?", (now,))
    tareas_vencidas = c.fetchall()

    for tarea in tareas_vencidas:
        if(tarea[7] != 1):
            print(f"La tarea '{tarea[2]}' ha vencido. Eliminando automáticamente.")
            c.execute("DELETE FROM tareas WHERE id=?", (tarea[0],))
            conn.commit()

def mostrar_tiempo_restante(tarea, tareas):
    if(tarea[1] == '2'):
        ahora = datetime.now()
        minutosActual = ahora.hour * 60 + ahora.minute 
        hora_limite = datetime.strptime(tarea[5], "%H:%M")
        minutosTarea = hora_limite.hour * 60 + hora_limite.minute
        
        #tiempo_restante = hora_limite - ahora
        #Calcular el tiempo restante debido a la prioridad de las tareas
        #tiempo_restante = minutosTarea - minutosActual
        tiempo_restante = minutosTarea
        if(tarea[6]!=11):
            for otrasTareas in tareas:
                if(otrasTareas[0]!= tarea[0]):
                
                    if(tarea[6]<=otrasTareas[6]):
                        tiempo_restante -= otrasTareas[3]
                
        print("Tarea: ", tarea[2])
        print("Hora limite:", hora_limite.hour, ":", hora_limite.minute)
        #print("Ahora:", ahora)
        #print("Minutos ahora: ", minutosActual)
        #print("Minutos tarea: ", minutosTarea)
        print("Tiempo restante:", int(tiempo_restante/60), ":", int(((tiempo_restante/60)-int(tiempo_restante/60))*60))
        #if tiempo_restante.total_seconds() < 0:
        if tiempo_restante < 0:
              print(f"¡Advertencia! La tarea '{tarea[2]}' está vencida.")
              #elif tiempo_restante.total_seconds() < 300:  # Menos de 5 minutos
        elif tiempo_restante < 5:  # Menos de 5 minutos
              print(f"¡Advertencia! Quedan menos de 5 minutos para la tarea '{tarea[2]}'. ¡Realícela lo antes posible!")
    
def mostrar_tiempo_restante_tareas():
    c.execute("SELECT * FROM tareas WHERE tipo = '1'  AND hora_limite > ?",
              (datetime.now().strftime("%H:%M"),))
    tareas_estaticas = c.fetchall()
    c.execute("SELECT * FROM tareas WHERE tipo = '2'  AND hora_limite > ?",
              (datetime.now().strftime("%H:%M"),))
    tareas_dinamicas = c.fetchall()
    
    c.execute("SELECT * FROM tareas WHERE hora_limite > ?",
              (datetime.now().strftime("%H:%M"),))
    tareas_ambos_tipos = c.fetchall()
    print("\n------ Tiempo Restante para Tareas ------")

    for tarea in tareas_estaticas:
        print("Hay tareas estaticas")
        #mostrar_tiempo_restante(tarea)
    for tarea in tareas_dinamicas:
        print("Hay tareas dinamicas:")
        mostrar_tiempo_restante(tarea, tareas_ambos_tipos)

def main():
    while True:
        verificar_tareas_vencidas()
        mostrar_tiempo_restante_tareas()

        print("\n------ Organizador de Tareas ------")
        print("1. Agregar tarea")
        print("2. Mostrar tareas")
        print("3. Eliminar tarea")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            agregar_tarea()
        elif opcion == '2':
            mostrar_tareas()
        elif opcion == '3':
            eliminar_tarea()
        elif opcion == '4':
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, elija una opción válida.")

if __name__ == "__main__":
    main()

# Cerrar la conexión a la base de datos al finalizar
conn.close()
