import json
from pathlib import Path
import collections

def exportar_resultados(resultados_solver: dict, ruta_salida: str) -> None:
    """
    Toma los resultados puros del solver y los serializa a un archivo JSON.
    Adicionalmente, reorganiza la lista plana de asignaciones en un árbol por secciones
    y por profesor para que sea inmediato de consumir por un Frontend o por Django.
    """
    # 1. Crear el árbol jerárquico
    asignaciones_planas = resultados_solver.get("asignaciones", [])
    
    # Agrupación 1: Por Sección
    horario_por_seccion = collections.defaultdict(list)
    # Agrupación 2: Por Profesor
    horario_por_profesor = collections.defaultdict(list)
    
    for asig in asignaciones_planas:
        # Copiamos para no mutar el original en caso de múltiples llamadas
        clase = dict(asig)
        
        # Guardamos en la vista de Seccion
        horario_por_seccion[clase["seccion_id"]].append(clase)
        
        # Guardamos en la vista de Profesor
        horario_por_profesor[clase["profesor_id"]].append(clase)
        
    
    # Estructuramos el payload final
    payload = {
        "metadata": {
            "estado": resultados_solver.get("estado"),
            "mensaje": resultados_solver.get("mensaje"),
            "estadisticas_solver": resultados_solver.get("estadisticas")
        },
        "asignaciones_lista": asignaciones_planas,
        "vista_secciones": dict(horario_por_seccion),
        "vista_profesores": dict(horario_por_profesor)
    }
    
    # 2. Asegurar el path y escribir a disco
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
