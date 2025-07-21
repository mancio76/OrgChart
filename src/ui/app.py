# src/ui/app.py - Versione pulita
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional
import os
import logging

from ..database.connection import DatabaseConnection
from ..database.repository import OrganigrammaRepository
from ..services.organigramma_service import OrganigrammaService

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inizializzazione FastAPI
app = FastAPI(title="Organigramma Manager", version="2.0.0")

# Setup database e servizi con gestione errori
try:
    db_connection = DatabaseConnection()
    repository = OrganigrammaRepository(db_connection)
    service = OrganigrammaService(repository)
    logger.info("Database e servizi inizializzati con successo")
except Exception as e:
    logger.error(f"Errore inizializzazione: {e}")
    raise

# Setup templates
templates = Jinja2Templates(directory="src/web/templates")

# Mount static files se esistono
static_path = "src/web/static"
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    logger.warning(f"Directory static non trovata: {static_path}")

# Include CRUD routers solo se disponibili
try:
    from ..web.routes.crud_api import router as crud_api_router
    from ..web.routes.crud_web import router as crud_web_router
    app.include_router(crud_api_router)
    app.include_router(crud_web_router)
    logger.info("Router CRUD caricati")
except ImportError as e:
    logger.warning(f"Router CRUD non disponibili: {e}")

# ================================================================
# ROUTE PRINCIPALI
# ================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principale"""
    try:
        data = service.get_dashboard_data()
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "title": "Dashboard",
            **data
        })
    except Exception as e:
        logger.error(f"Errore dashboard: {e}")
        raise HTTPException(500, "Errore interno del server")

@app.get("/employees", response_class=HTMLResponse)
async def employees_list(request: Request, search: Optional[str] = None):
    """Lista dipendenti"""
    try:
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
    except Exception as e:
        logger.error(f"Errore lista dipendenti: {e}")
        raise HTTPException(500, "Errore interno del server")

@app.get("/employee/{person_name}", response_class=HTMLResponse)
async def employee_profile(request: Request, person_name: str):
    """Profilo dipendente"""
    try:
        profile = service.get_employee_profile(person_name)
        if not profile:
            raise HTTPException(404, "Dipendente non trovato")
        
        return templates.TemplateResponse("employee_profile.html", {
            "request": request,
            "title": f"Profilo - {person_name}",
            **profile
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore profilo dipendente {person_name}: {e}")
        raise HTTPException(500, "Errore interno del server")

@app.get("/organization", response_class=HTMLResponse)
async def organization_chart(request: Request):
    """Organigramma"""
    try:
        org_tree = service.get_organization_tree()
        return templates.TemplateResponse("organization.html", {
            "request": request,
            "title": "Organigramma",
            "org_tree": org_tree
        })
    except Exception as e:
        logger.error(f"Errore organigramma: {e}")
        raise HTTPException(500, "Errore interno del server")

@app.get("/functions", response_class=HTMLResponse)
async def functions_list(request: Request):
    """Lista funzioni"""
    try:
        functions = repository.get_all_functions()
        return templates.TemplateResponse("functions.html", {
            "request": request,
            "title": "Funzioni",
            "functions": functions
        })
    except Exception as e:
        logger.error(f"Errore lista funzioni: {e}")
        raise HTTPException(500, "Errore interno del server")

@app.get("/function/{function_name}", response_class=HTMLResponse)
async def function_detail(request: Request, function_name: str):
    """Dettaglio funzione"""
    try:
        details = service.get_function_details(function_name)
        if not details:
            raise HTTPException(404, "Funzione non trovata")
        
        return templates.TemplateResponse("function_detail.html", {
            "request": request,
            "title": f"Funzione - {function_name}",
            **details
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore dettaglio funzione {function_name}: {e}")
        raise HTTPException(500, "Errore interno del server")

# ================================================================
# ADMIN DASHBOARD
# ================================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard amministrativa"""
    try:
        stats = repository.get_detailed_stats()
        return templates.TemplateResponse("admin/dashboard.html", {
            "request": request,
            "title": "Amministrazione",
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Errore admin dashboard: {e}")
        # Fallback con stats base
        try:
            stats = repository.get_stats()
            return templates.TemplateResponse("admin/dashboard.html", {
                "request": request,
                "title": "Amministrazione",
                "stats": stats
            })
        except:
            raise HTTPException(500, "Errore interno del server")

# ================================================================
# API ENDPOINTS
# ================================================================

@app.get("/api/search/employees")
async def api_search_employees(q: str):
    """API ricerca dipendenti"""
    try:
        employees = service.search_employees(q)
        return [{"name": emp.name, "employee_id": emp.employee_id, "status": emp.status} 
                for emp in employees]
    except Exception as e:
        logger.error(f"Errore ricerca API: {e}")
        return []

@app.get("/api/stats")
async def api_stats():
    """API statistiche"""
    try:
        return service.get_dashboard_data()['stats']
    except Exception as e:
        logger.error(f"Errore stats API: {e}")
        return {"error": "Dati non disponibili"}

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        stats = repository.get_stats()
        return {
            "status": "ok", 
            "service": "organigramma-manager",
            "database": "connected",
            "total_persons": stats.get('total_persons', 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "service": "organigramma-manager", 
            "database": "error",
            "error": str(e)
        }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {
        "request": request,
        "title": "Pagina non trovata"
    }, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {
        "request": request,
        "title": "Errore del server"
    }, status_code=500)