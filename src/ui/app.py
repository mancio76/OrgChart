from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os

from ..database.connection import DatabaseConnection
from ..database.repository import OrganigrammaRepository
from ..services.organigramma_service import OrganigrammaService

# Inizializzazione
app = FastAPI(title="Organigramma Manager", version="1.0.0")

# Setup database e servizi
db_connection = DatabaseConnection()
repository = OrganigrammaRepository(db_connection)
service = OrganigrammaService(repository)

# Setup templates
templates = Jinja2Templates(directory="src/web/templates")

# Mounting static files con path corretto
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Routes (resto del codice rimane uguale)
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principale"""
    data = service.get_dashboard_data()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard",
        **data
    })

@app.get("/employees", response_class=HTMLResponse)
async def employees_list(request: Request, search: Optional[str] = None):
    """Lista dipendenti con ricerca"""
    if search:
        employees = service.search_employees(search)
    else:
        employees = repository.get_all_persons()
    
    return templates.TemplateResponse("employees.html", {
        "request": request,
        "title": "Dipendenti",
        "employees": employees,
        "search_query": search or ""
    })

@app.get("/employee/{person_name}", response_class=HTMLResponse)
async def employee_profile(request: Request, person_name: str):
    """Profilo dipendente"""
    profile = service.get_employee_profile(person_name)
    if not profile:
        raise HTTPException(404, "Dipendente non trovato")
    
    return templates.TemplateResponse("employee_profile.html", {
        "request": request,
        "title": f"Profilo - {person_name}",
        **profile
    })

@app.get("/organization", response_class=HTMLResponse)
async def organization_chart(request: Request):
    """Organigramma"""
    org_tree = service.get_organization_tree()
    return templates.TemplateResponse("organization.html", {
        "request": request,
        "title": "Organigramma",
        "org_tree": org_tree
    })

@app.get("/functions", response_class=HTMLResponse)
async def functions_list(request: Request):
    """Lista funzioni"""
    functions = repository.get_all_functions()
    return templates.TemplateResponse("functions.html", {
        "request": request,
        "title": "Funzioni",
        "functions": functions
    })

@app.get("/function/{function_name}", response_class=HTMLResponse)
async def function_detail(request: Request, function_name: str):
    """Dettaglio funzione"""
    details = service.get_function_details(function_name)
    if not details:
        raise HTTPException(404, "Funzione non trovata")
    
    return templates.TemplateResponse("function_detail.html", {
        "request": request,
        "title": f"Funzione - {function_name}",
        **details
    })

# API Endpoints per AJAX
@app.get("/api/search/employees")
async def api_search_employees(q: str):
    """API ricerca dipendenti"""
    employees = service.search_employees(q)
    return [{"name": emp.name, "employee_id": emp.employee_id, "status": emp.status} 
            for emp in employees]

@app.get("/api/stats")
async def api_stats():
    """API statistiche"""
    return service.get_dashboard_data()['stats']

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "organigramma-manager"}