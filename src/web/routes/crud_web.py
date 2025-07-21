from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from datetime import date

from ...database.connection import DatabaseConnection
from ...database.repository import OrganigrammaRepository
from ...services.organigramma_service import OrganigrammaService

# Setup
router = APIRouter(tags=["CRUD Web"])
templates = Jinja2Templates(directory="src/web/templates")
db_connection = DatabaseConnection()
repository = OrganigrammaRepository(db_connection)
service = OrganigrammaService(repository)

# ================================================================
# PERSONS - WEB CRUD
# ================================================================

@router.get("/admin/persons", response_class=HTMLResponse)
async def admin_persons(request: Request):
    """Pagina amministrazione dipendenti"""
    persons = repository.get_all_persons(active_only=False)
    functions = repository.get_all_functions()
    job_titles = repository.get_all_job_titles()
    
    return templates.TemplateResponse("admin/persons.html", {
        "request": request,
        "title": "Gestione Dipendenti",
        "persons": persons,
        "functions": functions,
        "job_titles": job_titles
    })

@router.get("/admin/persons/new", response_class=HTMLResponse)
async def new_person_form(request: Request):
    """Form creazione nuovo dipendente"""
    return templates.TemplateResponse("admin/person_form.html", {
        "request": request,
        "title": "Nuovo Dipendente",
        "action": "create",
        "person": None
    })

@router.post("/admin/persons/new")
async def create_person_web(
    request: Request,
    name: str = Form(...),
    email: Optional[str] = Form(None),
    employee_id: Optional[str] = Form(None),
    hire_date: Optional[date] = Form(None),
    status: str = Form("ACTIVE"),
    flags: Optional[str] = Form(None)
):
    """Crea dipendente via form web"""
    person_data = {
        "name": name,
        "email": email if email else None,
        "employee_id": employee_id if employee_id else None,
        "hire_date": hire_date,
        "status": status,
        "flags": flags if flags else None
    }
    
    success, message, person_id = service.create_person(person_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/persons?success={message}",
            status_code=303
        )
    else:
        # Re-render form con errore
        return templates.TemplateResponse("admin/person_form.html", {
            "request": request,
            "title": "Nuovo Dipendente",
            "action": "create",
            "person": person_data,
            "error": message
        })

@router.get("/admin/persons/{person_name}/edit", response_class=HTMLResponse)
async def edit_person_form(request: Request, person_name: str):
    """Form modifica dipendente"""
    person = repository.get_person(person_name)
    if not person:
        raise HTTPException(404, "Dipendente non trovato")
    
    return templates.TemplateResponse("admin/person_form.html", {
        "request": request,
        "title": f"Modifica {person.name}",
        "action": "edit",
        "person": person
    })

@router.post("/admin/persons/{person_name}/edit")
async def update_person_web(
    request: Request,
    person_name: str,
    email: Optional[str] = Form(None),
    employee_id: Optional[str] = Form(None),
    hire_date: Optional[date] = Form(None),
    status: str = Form("ACTIVE"),
    flags: Optional[str] = Form(None)
):
    """Aggiorna dipendente via form web"""
    person_data = {
        "email": email if email else None,
        "employee_id": employee_id if employee_id else None,
        "hire_date": hire_date,
        "status": status,
        "flags": flags if flags else None
    }
    
    success, message = service.update_person(person_name, person_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/persons?success={message}",
            status_code=303
        )
    else:
        person = repository.get_person(person_name)
        return templates.TemplateResponse("admin/person_form.html", {
            "request": request,
            "title": f"Modifica {person_name}",
            "action": "edit",
            "person": person,
            "error": message
        })

@router.post("/admin/persons/{person_name}/delete")
async def delete_person_web(person_name: str):
    """Elimina dipendente"""
    success, message = service.delete_person(person_name)
    
    if success:
        return RedirectResponse(
            url=f"/admin/persons?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin/persons?error={message}",
            status_code=303
        )

# ================================================================
# FUNCTIONS - WEB CRUD
# ================================================================

@router.get("/admin/functions", response_class=HTMLResponse)
async def admin_functions(request: Request):
    """Pagina amministrazione funzioni"""
    functions = repository.get_all_functions()
    
    # Aggiungi info dipendenze per ogni funzione
    functions_with_deps = []
    for func in functions:
        deps = repository.get_function_dependencies(func.name)
        roles = repository.get_function_roles(func.name, active_only=True)
        functions_with_deps.append({
            "function": func,
            "dependencies": deps,
            "active_roles": len(roles),
            "can_delete": not deps['has_dependencies']
        })
    
    return templates.TemplateResponse("admin/functions.html", {
        "request": request,
        "title": "Gestione Funzioni",
        "functions": functions_with_deps,
        "all_functions": functions  # Per dropdown parent
    })

@router.get("/admin/functions/new", response_class=HTMLResponse)
async def new_function_form(request: Request):
    """Form creazione nuova funzione"""
    functions = repository.get_all_functions()
    return templates.TemplateResponse("admin/function_form.html", {
        "request": request,
        "title": "Nuova Funzione",
        "action": "create",
        "function": None,
        "all_functions": functions
    })

@router.post("/admin/functions/new")
async def create_function_web(
    request: Request,
    name: str = Form(...),
    reports_to: Optional[str] = Form(None),
    flags: Optional[str] = Form(None)
):
    """Crea funzione via form web"""
    function_data = {
        "name": name,
        "reports_to": reports_to if reports_to else None,
        "flags": flags if flags else None
    }
    
    success, message, function_id = service.create_function(function_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/functions?success={message}",
            status_code=303
        )
    else:
        functions = repository.get_all_functions()
        return templates.TemplateResponse("admin/function_form.html", {
            "request": request,
            "title": "Nuova Funzione",
            "action": "create",
            "function": function_data,
            "all_functions": functions,
            "error": message
        })

@router.get("/admin/functions/{function_name}/edit", response_class=HTMLResponse)
async def edit_function_form(request: Request, function_name: str):
    """Form modifica funzione"""
    function = repository.get_function(function_name)
    
    if not function:
        raise HTTPException(404, "Funzione non trovata")
    
    all_functions = repository.get_all_functions()
    return templates.TemplateResponse("admin/function_form.html", {
        "request": request,
        "title": f"Modifica {function.name}",
        "action": "edit",
        "function": function,
        "all_functions": [f for f in all_functions if f.name != function_name],
    })

@router.post("/admin/functions/{function_name}/edit")
async def update_functions_web(
    request: Request,
    function_name: str,
    reports_to: Optional[str] = Form(None),
    flags: Optional[str] = Form(None)
):
    """Aggiorna funzione via form web"""
    function_data = {
        "reports_to": reports_to if reports_to else None,
        "flags": flags if flags else None
    }
    
    success, message = service.update_function(function_name, function_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/functions?success={message}",
            status_code=303
        )
    else:
        function = repository.get_function(function_name)
        return templates.TemplateResponse("admin/function_form.html", {
            "request": request,
            "title": f"Modifica {function_name}",
            "action": "edit",
            "function": function,
            "error": message
        })

@router.post("/admin/functions/{person_name}/delete")
async def delete_function_web(function_name: str):
    """Elimina funzione"""
    success, message = service.delete_function(function_name)
    
    if success:
        return RedirectResponse(
            url=f"/admin/functions?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin/functions?error={message}",
            status_code=303
        )

# ================================================================
# ROLES - WEB CRUD
# ================================================================

@router.get("/admin/roles", response_class=HTMLResponse)
async def admin_roles(request: Request, person_name: Optional[str] = None):
    """Pagina amministrazione ruoli"""
    if person_name:
        roles = repository.get_person_roles(person_name, active_only=False)
        title = f"Ruoli di {person_name}"
    else:
        # Recupera tutti i ruoli attivi
        query = "SELECT * FROM roles WHERE end_date IS NULL ORDER BY person_name, function_name"
        rows = repository.db.execute_query(query)
        roles = [repository._dict_to_role(dict(row)) for row in rows]
        title = "Tutti i Ruoli"
    
    persons = repository.get_all_persons()
    functions = repository.get_all_functions()
    job_titles = repository.get_all_job_titles()
    
    return templates.TemplateResponse("admin/roles.html", {
        "request": request,
        "title": title,
        "roles": roles,
        "persons": persons,
        "functions": functions,
        "job_titles": job_titles,
        "filter_person": person_name
    })

@router.get("/admin/roles/new", response_class=HTMLResponse)
async def new_role_form(request: Request):
    """Form creazione nuovo ruolo"""
    persons = repository.get_all_persons()
    functions = repository.get_all_functions()
    job_titles = repository.get_all_job_titles()
    
    return templates.TemplateResponse("admin/role_form.html", {
        "request": request,
        "title": "Nuovo Ruolo",
        "action": "create",
        "role": None,
        "persons": persons,
        "functions": functions,
        "job_titles": job_titles
    })

@router.post("/admin/roles/new")
async def create_role_web(
    request: Request,
    person_name: str = Form(...),
    function_name: str = Form(...),
    organizational_unit: Optional[str] = Form(None),
    job_title_name: Optional[str] = Form(None),
    percentage: float = Form(1.0),
    ad_interim: bool = Form(False),
    reports_to: Optional[str] = Form(None),
    start_date: Optional[date] = Form(None),
    flags: Optional[str] = Form(None)
):
    """Crea ruolo via form web"""
    role_data = {
        "person_name": person_name,
        "function_name": function_name,
        "organizational_unit": organizational_unit if organizational_unit else None,
        "job_title_name": job_title_name if job_title_name else None,
        "percentage": percentage,
        "ad_interim": ad_interim,
        "reports_to": reports_to if reports_to else None,
        "start_date": start_date,
        "flags": flags if flags else None
    }
    
    success, message, role_id = service.create_role(role_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/roles?success={message}",
            status_code=303
        )
    else:
        persons = repository.get_all_persons()
        functions = repository.get_all_functions()
        job_titles = repository.get_all_job_titles()
        
        return templates.TemplateResponse("admin/role_form.html", {
            "request": request,
            "title": "Nuovo Ruolo",
            "action": "create",
            "role": role_data,
            "persons": persons,
            "functions": functions,
            "job_titles": job_titles,
            "error": message
        })

@router.get("/admin/roles/{role_id}/edit", response_class=HTMLResponse)
async def edit_role_form(request: Request, role_id: int):
    """Form modifica ruolo"""
    role = repository.get_role(role_id)
    
    if not role:
        raise HTTPException(404, "Ruolo non trovata")
    
    all_persons = repository.get_all_persons()
    all_functions = repository.get_all_functions()
    all_job_titles = repository.get_all_job_titles()
    
    return templates.TemplateResponse("admin/role_form.html", {
        "request": request,
        "title": f"Modifica {role.person_name}",
        "action": "edit",
        "role": role,
        "persons": [p for p in all_persons if p is not None],
        "functions": [f for f in all_functions if f is not None],
        "job_titles": [j for j in all_job_titles if j is not None],
    })

@router.post("/admin/roles/{role_name}/edit")
async def update_roles_web(
    request: Request,
    role_id: int,
    reports_to: Optional[str] = Form(None),
    flags: Optional[str] = Form(None)
):
    """Aggiorna role via form web"""
    role_data = {
        "reports_to": reports_to if reports_to else None,
        "flags": flags if flags else None
    }
    
    success, message = service.update_role(role_id, role_data)
    
    if success:
        return RedirectResponse(
            url=f"/admin/roles?success={message}",
            status_code=303
        )
    else:
        role = repository.get_role(role_id)
        return templates.TemplateResponse("admin/role_form.html", {
            "request": request,
            "title": f"Modifica {role_id}",
            "action": "edit",
            "role": role,
            "error": message
        })

@router.post("/admin/roles/{role_id}/end")
async def end_role_web(role_id: int, end_date: Optional[date] = Form(None)):
    """Termina ruolo"""
    success, message = service.end_role(role_id, end_date)
    
    if success:
        return RedirectResponse(
            url=f"/admin/roles?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin/roles?error={message}",
            status_code=303
        )

# ================================================================
# BULK OPERATIONS - WEB
# ================================================================

@router.get("/admin/bulk", response_class=HTMLResponse)
async def admin_bulk_operations(request: Request):
    """Pagina operazioni in blocco"""
    persons = repository.get_all_persons()
    functions = repository.get_all_functions()
    
    return templates.TemplateResponse("admin/bulk_operations.html", {
        "request": request,
        "title": "Operazioni in Blocco",
        "persons": persons,
        "functions": functions
    })

@router.post("/admin/bulk/change-manager")
async def bulk_change_manager_web(
    old_manager: str = Form(...),
    new_manager: str = Form(...)
):
    """Cambio manager in blocco"""
    success, message, count = service.bulk_change_manager(old_manager, new_manager)
    
    if success:
        return RedirectResponse(
            url=f"/admin/bulk?success={message} ({count} ruoli aggiornati)",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin/bulk?error={message}",
            status_code=303
        )

@router.post("/admin/bulk/terminate-employee")
async def terminate_employee_web(
    person_name: str = Form(...),
    termination_date: Optional[date] = Form(None)
):
    """Terminazione dipendente con tutti i ruoli"""
    success, message, count = service.terminate_employee(person_name, termination_date)
    
    if success:
        return RedirectResponse(
            url=f"/admin/bulk?success={message} ({count} ruoli terminati)",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/admin/bulk?error={message}",
            status_code=303
        )