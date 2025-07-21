from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, validator
import json

from ...database.connection import DatabaseConnection
from ...database.repository import OrganigrammaRepository
from ...services.organigramma_service import OrganigrammaService

# Inizializzazione
router = APIRouter(prefix="/api", tags=["CRUD"])
db_connection = DatabaseConnection()
repository = OrganigrammaRepository(db_connection)
service = OrganigrammaService(repository)

# ================================================================
# PYDANTIC MODELS PER VALIDAZIONE
# ================================================================

class PersonCreate(BaseModel):
    name: str
    email: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[date] = None
    status: str = "ACTIVE"
    flags: Optional[str] = None
    aliases: Optional[list] = []
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['ACTIVE', 'INACTIVE', 'TERMINATED']:
            raise ValueError('Status deve essere ACTIVE, INACTIVE o TERMINATED')
        return v

class PersonUpdate(BaseModel):
    email: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None
    flags: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['ACTIVE', 'INACTIVE', 'TERMINATED']:
            raise ValueError('Status deve essere ACTIVE, INACTIVE o TERMINATED')
        return v

class FunctionCreate(BaseModel):
    name: str
    reports_to: Optional[str] = None
    flags: Optional[str] = None

class FunctionUpdate(BaseModel):
    reports_to: Optional[str] = None
    flags: Optional[str] = None

class RoleCreate(BaseModel):
    person_name: str
    function_name: str
    organizational_unit: Optional[str] = None
    job_title_name: Optional[str] = None
    percentage: float = 1.0
    ad_interim: bool = False
    reports_to: Optional[str] = None
    start_date: Optional[date] = None
    flags: Optional[str] = None
    
    @validator('percentage')
    def validate_percentage(cls, v):
        if v <= 0 or v > 1:
            raise ValueError('Percentuale deve essere tra 0.01 e 1.0')
        return v

class RoleUpdate(BaseModel):
    organizational_unit: Optional[str] = None
    job_title_name: Optional[str] = None
    percentage: Optional[float] = None
    ad_interim: Optional[bool] = None
    reports_to: Optional[str] = None
    flags: Optional[str] = None
    
    @validator('percentage')
    def validate_percentage(cls, v):
        if v is not None and (v <= 0 or v > 1):
            raise ValueError('Percentuale deve essere tra 0.01 e 1.0')
        return v

class JobTitleCreate(BaseModel):
    name: str
    level: Optional[int] = None
    flags: Optional[str] = None

# ================================================================
# PERSONS API ENDPOINTS
# ================================================================

@router.post("/persons")
async def create_person(person: PersonCreate):
    """Crea nuovo dipendente"""
    success, message, person_id = service.create_person(person.dict())
    
    if success:
        return JSONResponse(
            status_code=201,
            content={"success": True, "message": message, "id": person_id}
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.get("/persons")
async def list_persons(active_only: bool = True, search: Optional[str] = None):
    """Lista dipendenti"""
    if search:
        persons = service.search_employees(search)
    else:
        persons = repository.get_all_persons(active_only)
    
    return [person.__dict__ for person in persons]

@router.get("/persons/{person_name}")
async def get_person(person_name: str):
    """Recupera singolo dipendente"""
    person = repository.get_person(person_name)
    if not person:
        raise HTTPException(status_code=404, detail="Dipendente non trovato")
    
    return person.__dict__

@router.put("/persons/{person_name}")
async def update_person(person_name: str, person: PersonUpdate):
    """Aggiorna dipendente"""
    success, message = service.update_person(person_name, person.dict(exclude_unset=True))
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.delete("/persons/{person_name}")
async def delete_person(person_name: str, soft_delete: bool = True):
    """Elimina dipendente"""
    if soft_delete:
        success, message = service.update_person(person_name, {"status": "TERMINATED"})
    else:
        success, message = service.delete_person(person_name)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/persons/{person_name}/terminate")
async def terminate_employee(person_name: str, termination_date: Optional[date] = None):
    """Termina dipendente e tutti i ruoli"""
    success, message, roles_count = service.terminate_employee(person_name, termination_date)
    
    if success:
        return {"success": True, "message": message, "terminated_roles": roles_count}
    else:
        raise HTTPException(status_code=400, detail=message)

# ================================================================
# FUNCTIONS API ENDPOINTS
# ================================================================

@router.post("/functions")
async def create_function(function: FunctionCreate):
    """Crea nuova funzione"""
    success, message, function_id = service.create_function(function.dict())
    
    if success:
        return JSONResponse(
            status_code=201,
            content={"success": True, "message": message, "id": function_id}
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.get("/functions")
async def list_functions():
    """Lista funzioni"""
    functions = repository.get_all_functions()
    return [func.__dict__ for func in functions]

@router.get("/functions/{function_name}")
async def get_function(function_name: str):
    """Recupera singola funzione"""
    function = repository.get_function(function_name)
    if not function:
        raise HTTPException(status_code=404, detail="Funzione non trovata")
    
    # Aggiungi informazioni aggiuntive
    deps = repository.get_function_dependencies(function_name)
    roles = repository.get_function_roles(function_name)
    
    return {
        **function.__dict__,
        "dependencies": deps,
        "roles": [role.__dict__ for role in roles]
    }

@router.put("/functions/{function_name}")
async def update_function(function_name: str, function: FunctionUpdate):
    """Aggiorna funzione"""
    success, message = service.update_function(function_name, function.dict(exclude_unset=True))
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.delete("/functions/{function_name}")
async def delete_function(function_name: str):
    """Elimina funzione"""
    success, message = service.delete_function(function_name)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/functions/{function_name}/reorganize")
async def reorganize_function(function_name: str, new_reports_to: Optional[str] = None):
    """Riorganizza funzione nella gerarchia"""
    success, message = service.reorganize_function(function_name, new_reports_to)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

# ================================================================
# ROLES API ENDPOINTS
# ================================================================

@router.post("/roles")
async def create_role(role: RoleCreate):
    """Crea nuovo ruolo"""
    success, message, role_id = service.create_role(role.dict())
    
    if success:
        return JSONResponse(
            status_code=201,
            content={"success": True, "message": message, "id": role_id}
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.get("/roles/{role_id}")
async def get_role(role_id: int):
    """Recupera singolo ruolo"""
    role = repository.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Ruolo non trovato")
    
    return role.__dict__

@router.put("/roles/{role_id}")
async def update_role(role_id: int, role: RoleUpdate):
    """Aggiorna ruolo"""
    success, message = service.update_role(role_id, role.dict(exclude_unset=True))
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/roles/{role_id}/end")
async def end_role(role_id: int, end_date: Optional[date] = None):
    """Termina ruolo"""
    success, message = service.end_role(role_id, end_date)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/roles/{role_id}/transfer")
async def transfer_role(role_id: int, new_person_name: str, transfer_date: Optional[date] = None):
    """Trasferisce ruolo ad altra persona"""
    success, message, new_role_id = service.transfer_role(role_id, new_person_name, transfer_date)
    
    if success:
        return {"success": True, "message": message, "new_role_id": new_role_id}
    else:
        raise HTTPException(status_code=400, detail=message)

# ================================================================
# JOB TITLES API ENDPOINTS
# ================================================================

@router.post("/job-titles")
async def create_job_title(job_title: JobTitleCreate):
    """Crea nuovo job title"""
    success, message, job_title_id = service.create_job_title(job_title.dict())
    
    if success:
        return JSONResponse(
            status_code=201,
            content={"success": True, "message": message, "id": job_title_id}
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.get("/job-titles")
async def list_job_titles():
    """Lista job titles"""
    job_titles = repository.get_all_job_titles()
    return [jt.__dict__ for jt in job_titles]

@router.delete("/job-titles/{job_title_name}")
async def delete_job_title(job_title_name: str):
    """Elimina job title"""
    success, message = service.delete_job_title(job_title_name)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

# ================================================================
# BULK OPERATIONS
# ================================================================

@router.post("/bulk/change-manager")
async def bulk_change_manager(old_manager: str, new_manager: str):
    """Cambia manager per tutti i report"""
    success, message, count = service.bulk_change_manager(old_manager, new_manager)
    
    if success:
        return {"success": True, "message": message, "affected_count": count}
    else:
        raise HTTPException(status_code=400, detail=message)

# ================================================================
# ALIASES API ENDPOINTS
# ================================================================

@router.post("/persons/{person_name}/aliases")
async def add_person_alias(person_name: str, alias: str, flags: Optional[str] = None):
    """Aggiungi alias a persona"""
    success = repository.add_person_alias(person_name, alias, flags)
    
    if success:
        return {"success": True, "message": "Alias aggiunto"}
    else:
        raise HTTPException(status_code=400, detail="Errore aggiunta alias")

@router.delete("/persons/{person_name}/aliases/{alias}")
async def remove_person_alias(person_name: str, alias: str):
    """Rimuovi alias da persona"""
    success = repository.remove_person_alias(person_name, alias)
    
    if success:
        return {"success": True, "message": "Alias rimosso"}
    else:
        raise HTTPException(status_code=404, detail="Alias non trovato")
