from ortools.sat.python import cp_model
import collections

def construir_modelo(datos_procesados: dict) -> tuple[cp_model.CpModel, dict]:
    """
    Construye el modelo CP-SAT, genera el espacio booleano y añade las restricciones.
    """
    model = cp_model.CpModel()
    
    config = datos_procesados["configuracion"]
    cursos = datos_procesados["cursos"]
    categorias = datos_procesados["categorias"]
    profesores_dict = datos_procesados["profesores"]
    
    profesores_por_curso = datos_procesados["profesores_por_curso"]
    requerimientos_seccion = datos_procesados["requerimientos_seccion"]
    disp_seccion = datos_procesados["disp_seccion"]
    disp_profesor = datos_procesados["disp_profesor"]
    
    dias = config["dias"]
    turnos = config["turnos"]
    slots_por_turno = config["slots_por_turno"]

    # Diccionario para almacenar las variables creadas
    x = {}
    
    # Agrupadores para constraints rápidas (se evita iterar Múltiples veces el dominio completo)
    cobertura_clases = collections.defaultdict(list)          # (seccion_id, curso_id) -> vars
    unicidad_seccion = collections.defaultdict(list)          # (seccion_id, dia, turno, slot) -> vars
    unicidad_profesor = collections.defaultdict(list)         # (profesor_id, dia, turno, slot) -> vars
    limite_dia_profesor = collections.defaultdict(list)       # (profesor_id, dia) -> vars
    limite_dia_categoria_sec = collections.defaultdict(list)  # (seccion_id, dia, categoria_id) -> vars

    # 1. GENERACIÓN DEL ESPACIO BOOLEANO DE VARIABLES
    for s_id, reqs in requerimientos_seccion.items():
        s_disp = disp_seccion.get(s_id, set())
        for c_id, horas in reqs.items():
            cat_id = cursos[c_id]["categoria_id"]
            
            for p_id in profesores_por_curso.get(c_id, []):
                p_disp = disp_profesor.get(p_id, set())
                
                for dia in dias:
                    for turno in turnos:
                        # Condición estricta: slot válido sólo si AMBOS tienen disponibilidad
                        if (dia, turno) in s_disp and (dia, turno) in p_disp:
                            for slot in range(slots_por_turno):
                                variable_name = f"x_{s_id}_{c_id}_{p_id}_{dia}_{turno}_{slot}"
                                var = model.NewBoolVar(variable_name)
                                
                                x[(s_id, c_id, p_id, dia, turno, slot)] = var
                                
                                cobertura_clases[(s_id, c_id)].append(var)
                                unicidad_seccion[(s_id, dia, turno, slot)].append(var)
                                unicidad_profesor[(p_id, dia, turno, slot)].append(var)
                                limite_dia_profesor[(p_id, dia)].append(var)
                                limite_dia_categoria_sec[(s_id, dia, cat_id)].append(var)

    # 2. DECLARACIÓN DE RESTRICCIONES (CONSTRAINTS)
    
    # [A] Cobertura exacta: Cumplir con las horas semanales por curso y sección
    for (s_id, c_id), vars_list in cobertura_clases.items():
        horas_requeridas = requerimientos_seccion[s_id][c_id]
        model.Add(sum(vars_list) == horas_requeridas)
        
    # [B] Conflicto Sección: Una sección sólo puede tener un curso/profesor por slot
    for vars_list in unicidad_seccion.values():
        model.AddAtMostOne(vars_list)
        
    # [C] Conflicto Profesor: Un profesor sólo puede dictar en un curso/sección por slot
    for vars_list in unicidad_profesor.values():
        model.AddAtMostOne(vars_list)
        
    # [D] Límite de carga diaria por Profesor
    for (p_id, dia), vars_list in limite_dia_profesor.items():
        max_horas = profesores_dict[p_id]["max_horas_dia"]
        model.Add(sum(vars_list) <= max_horas)
        
    # [E] Límite de carga diaria por Categoría (para Secciones, ej: max 3h Matemáticas por día)
    for (s_id, dia, cat_id), vars_list in limite_dia_categoria_sec.items():
        max_horas_cat = categorias[cat_id]["max_horas_dia"]
        model.Add(sum(vars_list) <= max_horas_cat)
        
    return model, x
