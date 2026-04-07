import sys
from engine.loader import (
    cargar_datos,
    extraer_configuracion,
    extraer_categorias,
    extraer_cursos,
    extraer_profesores,
    extraer_secciones,
    extraer_grados,
)
from utils.validators import validar_todo
from engine.preprocessor import preprocesar
from engine.model import construir_modelo
 
 
def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <ruta_al_json>")
        print("Ejemplo: python main.py data/input/datos.json")
        sys.exit(1)
 
    ruta_json = sys.argv[1]
 
    # --- Carga ---
    print(f"Cargando datos desde: {ruta_json}")
    try:
        datos = cargar_datos(ruta_json)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error al cargar el archivo: {e}")
        sys.exit(1)
 
    configuracion = extraer_configuracion(datos)
    categorias    = extraer_categorias(datos)
    cursos        = extraer_cursos(datos)
    profesores    = extraer_profesores(datos)
    secciones     = extraer_secciones(datos)
    grados        = extraer_grados(datos)
 
    print(f"  Categorías cargadas : {len(categorias)}")
    print(f"  Cursos cargados     : {len(cursos)}")
    print(f"  Profesores cargados : {len(profesores)}")
    print(f"  Secciones cargadas  : {len(secciones)}")
    print(f"  Grados cargados     : {len(grados)}")
 
    # --- Validación ---
    print("\nValidando integridad de los datos...")
    errores = validar_todo(datos)
 
    if errores:
        print(f"\nSe encontraron {len(errores)} error(es):\n")
        for error in errores:
            print(f"  • {error}")
        sys.exit(1)
 
    print("Validación exitosa. Datos listos para el preprocessor.")
 
    print("\nEjecutando el preprocessor...")
    datos_procesados = preprocesar(datos)
    
    print(f"  Total requerimientos (secciones): {len(datos_procesados['requerimientos_seccion'])}")
    
    print("\nConstruyendo el modelo CP-SAT...")
    modelo, variables_x = construir_modelo(datos_procesados)
    print(f"  Número de variables declaradas: {len(variables_x)}")
    
    # Los siguientes módulos se irán añadiendo aquí:
    # solver → exporter
 
 
if __name__ == "__main__":
    main()