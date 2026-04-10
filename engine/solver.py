from ortools.sat.python import cp_model

def resolver_modelo(modelo: cp_model.CpModel, variables_x: dict, max_tiempo_segundos: int = 60) -> dict:
    """
    Ejecuta el resolver CP-SAT sobre el modelo generado y extrae los resultados.
    
    Args:
        modelo: El objeto CpModel con las variables y restricciones
        variables_x: El diccionario O(1) de las variables booleanas instanciadas
        max_tiempo_segundos: Tiempo límite para la búsqueda profunda
        
    Returns:
        Diccionario con un status de ejecución y la asignación resultante.
    """
    solver = cp_model.CpSolver()
    
    # Parámetros del solver
    solver.parameters.max_time_in_seconds = max_tiempo_segundos
    # Permite que intente encontrar múltiples soluciones en paralelo para ser más rápido
    solver.parameters.num_search_workers = 8
    
    print("\n--- Ejecutando Solver CP-SAT ---")
    status = solver.Solve(modelo)
    
    resultado = {
        "estado": "",
        "mensaje": "",
        "estadisticas": {
            "tiempo_segundos": solver.WallTime(),
            "ramas_exploradas": solver.NumBranches(),
            "conflictos": solver.NumConflicts()
        },
        "asignaciones": []
    }
    
    if status == cp_model.OPTIMAL:
        resultado["estado"] = "OPTIMAL"
        resultado["mensaje"] = "Se encontró la solución óptima del horario."
    elif status == cp_model.FEASIBLE:
        resultado["estado"] = "FEASIBLE"
        resultado["mensaje"] = "Se encontró una solución válida, pero no está comprobado que sea la óptima absoluta bajo el límite de tiempo."
    elif status == cp_model.INFEASIBLE:
        resultado["estado"] = "INFEASIBLE"
        resultado["mensaje"] = "El modelo es irresoluble. Las restricciones actuales chocan irremediablemente (ej. faltan profesores o espacio para la malla requerida)."
        return resultado
    else:
        resultado["estado"] = "UNKNOWN"
        resultado["mensaje"] = "No se encontró solución antes de agotar el límite de tiempo."
        return resultado

    # Si llegamos aquí, fue factible u óptimo. Extraer la solución:
    asignaciones_exitosas = []
    for llave, variable in variables_x.items():
        if solver.BooleanValue(variable):
            # llave es una tupla: (s_id, c_id, p_id, dia, turno, slot)
            s_id, c_id, p_id, dia, turno, slot = llave
            asignaciones_exitosas.append({
                "seccion_id": s_id,
                "curso_id": c_id,
                "profesor_id": p_id,
                "dia": dia,
                "turno": turno,
                "slot": slot
            })
            
    resultado["asignaciones"] = asignaciones_exitosas
    return resultado
