# src/ui/app.py - AGGIORNAMENTO CON CRUD
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os

from ..database.connection import DatabaseConnection
from ..database.repository import OrganigrammaRepository
from ..services.organigramma_service import OrganigrammaService

# Import delle nuove routes CRUD
from ..web.routes.crud_api import router as crud_api_router
from ..web.routes.crud_web import router as crud_web_router

# Inizializzazione
app = FastAPI(title="Organigramma Manager", version="1.0.0")

# Setup database e servizi
db_connection = DatabaseConnection()
repository = OrganigrammaRepository(db_connection)
service = OrganigrammaService(repository)

# Setup templates
templates = Jinja2Templates(directory="src/web/templates")

# Mounting static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include CRUD routers
app.include_router(crud_api_router)
app.include_router(crud_web_router)

# ================================================================
# HELPER FUNCTIONS PER REPOSITORY
# ================================================================

def _dict_to_role(self, row_dict):
    """Converte dizionario in oggetto Role"""
    from src.database.models import Role
    return Role(**row_dict)

# Aggiungi questo metodo alla classe OrganigrammaRepository
OrganigrammaRepository._dict_to_role = _dict_to_role

# ================================================================
# UTILITY PER VALIDAZIONI
# ================================================================

# src/utils/validators.py
import re
from typing import Dict, List, Optional
from datetime import date, datetime

class ValidationError(Exception):
    """Eccezione per errori di validazione"""
    pass

class DataValidator:
    """Classe per validazioni comuni"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato email"""
        if not email:
            return True  # Email opzionale
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# ROUTE ESISTENTI (Dashboard, Employees, etc.)
# ================================================================

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

# ================================================================
# NUOVE ROUTE ADMIN
# ================================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard amministrativa"""
    stats = repository.get_detailed_stats()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "title": "Amministrazione",
        "stats": stats
    })

# API Endpoints esistenti
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
    try:
        # Test connessione database
        stats = repository.get_stats()
        return {
            "status": "ok", 
            "service": "organigramma-manager",
            "database": "connected",
            "total_persons": stats['total_persons']
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "organigramma-manager", 
            "database": "error",
            "error": str(e)
        }

# ================================================================
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> bool:
        """Valida formato employee ID"""
        if not employee_id:
            return True  # Employee ID opzionale
        # Formato: EMP001, EXT001, etc.
        pattern = r'^[A-Z]{3}\d{3}'
# ROUTE ESISTENTI (Dashboard, Employees, etc.)
# ================================================================

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

# ================================================================
# NUOVE ROUTE ADMIN
# ================================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard amministrativa"""
    stats = repository.get_detailed_stats()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "title": "Amministrazione",
        "stats": stats
    })

# API Endpoints esistenti
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
    try:
        # Test connessione database
        stats = repository.get_stats()
        return {
            "status": "ok", 
            "service": "organigramma-manager",
            "database": "connected",
            "total_persons": stats['total_persons']
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "organigramma-manager", 
            "database": "error",
            "error": str(e)
        }

# ================================================================
        return bool(re.match(pattern, employee_id))
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Valida nome persona o funzione"""
        if not name or not name.strip():
            return False
        return len(name.strip()) >= 2
    
    @staticmethod
    def validate_percentage(percentage: float) -> bool:
        """Valida percentuale ruolo"""
        return 0.01 <= percentage <= 1.0
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """Valida stato persona"""
        return status in ['ACTIVE', 'INACTIVE', 'TERMINATED']
    
    @staticmethod
    def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> bool:
        """Valida range di date"""
        if start_date and end_date:
            return start_date <= end_date
        return True

# ================================================================
# TEMPLATE ADMIN DASHBOARD
# ================================================================

# src/web/templates/admin/dashboard.html
admin_dashboard_template = '''
{% extends "base.html" %}

{% block title %}Amministrazione - Organigramma Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h1>🛠️ Amministrazione</h1>
    <p class="page-subtitle">Gestione completa dell'organigramma aziendale</p>
</div>

<div class="admin-nav">
    <div class="nav-grid">
        <a href="/admin/persons" class="admin-nav-card">
            <div class="nav-icon">👥</div>
            <h3>Dipendenti</h3>
            <p>{{ stats.total_persons }} dipendenti</p>
            <span class="nav-action">Gestisci →</span>
        </a>
        
        <a href="/admin/functions" class="admin-nav-card">
            <div class="nav-icon">🏢</div>
            <h3>Funzioni</h3>
            <p>{{ stats.total_functions }} funzioni</p>
            <span class="nav-action">Gestisci →</span>
        </a>
        
        <a href="/admin/roles" class="admin-nav-card">
            <div class="nav-icon">💼</div>
            <h3>Ruoli</h3>
            <p>{{ stats.total_roles }} ruoli attivi</p>
            <span class="nav-action">Gestisci →</span>
        </a>
        
        <a href="/admin/bulk" class="admin-nav-card">
            <div class="nav-icon">⚡</div>
            <h3>Operazioni</h3>
            <p>Modifiche in blocco</p>
            <span class="nav-action">Esegui →</span>
        </a>
    </div>
</div>

<div class="admin-sections">
    <div class="admin-section">
        <h2>📊 Statistiche Dettagliate</h2>
        <div class="stats-details">
            <div class="stat-item">
                <span class="stat-label">Dipendenti con ruoli multipli:</span>
                <span class="stat-value">{{ stats.multi_role_persons }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Ruoli ad interim:</span>
                <span class="stat-value">{{ stats.interim_roles }}</span>
            </div>
        </div>
        
        {% if stats.functions_by_headcount %}
        <div class="chart-container">
            <h3>Funzioni per Headcount</h3>
            <div class="horizontal-chart">
                {% for func in stats.functions_by_headcount[:10] %}
                <div class="chart-item">
                    <span class="chart-label">{{ func.name[:30] }}</span>
                    <div class="chart-bar">
                        <div class="chart-fill" style="width: {{ (func.role_count / stats.functions_by_headcount[0].role_count * 100)|round }}%"></div>
                    </div>
                    <span class="chart-value">{{ func.role_count }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
    
    <div class="admin-section">
        <h2>🔄 Attività Recenti</h2>
        <div class="recent-activity">
            <div class="activity-item">
                <span class="activity-icon">➕</span>
                <div class="activity-content">
                    <p>Sistema CRUD implementato</p>
                    <small>Tutte le operazioni sono ora disponibili</small>
                </div>
                <span class="activity-time">Ora</span>
            </div>
        </div>
        
        <div class="admin-actions">
            <h3>Azioni Rapide</h3>
            <div class="quick-actions">
                <a href="/admin/persons/new" class="quick-action">➕ Nuovo Dipendente</a>
                <a href="/admin/functions/new" class="quick-action">🏢 Nuova Funzione</a>
                <a href="/admin/roles/new" class="quick-action">💼 Nuovo Ruolo</a>
            </div>
        </div>
    </div>
</div>

<style>
.admin-nav {
    margin-bottom: 3rem;
}

.nav-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.admin-nav-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
    border-left: 4px solid #2563eb;
}

.admin-nav-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    text-decoration: none;
}

.nav-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
}

.admin-nav-card h3 {
    color: #1f2937;
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
}

.admin-nav-card p {
    color: #6b7280;
    margin-bottom: 1rem;
}

.nav-action {
    color: #2563eb;
    font-weight: 500;
    font-size: 0.875rem;
}

.admin-sections {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

.admin-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.admin-section h2 {
    color: #1f2937;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

.stats-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 6px;
}

.stat-label {
    color: #374151;
    font-weight: 500;
}

.stat-value {
    color: #2563eb;
    font-weight: 700;
    font-size: 1.25rem;
}

.chart-container {
    margin-top: 2rem;
}

.chart-container h3 {
    color: #1f2937;
    margin-bottom: 1rem;
}

.horizontal-chart {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.chart-item {
    display: grid;
    grid-template-columns: 150px 1fr 40px;
    align-items: center;
    gap: 1rem;
}

.chart-label {
    font-size: 0.875rem;
    color: #374151;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.chart-bar {
    background: #e5e7eb;
    height: 20px;
    border-radius: 10px;
    overflow: hidden;
}

.chart-fill {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    height: 100%;
    transition: width 0.3s ease;
}

.chart-value {
    color: #374151;
    font-weight: 500;
    text-align: right;
}

.recent-activity {
    margin-bottom: 2rem;
}

.activity-item {
    display: flex;
    align-items: start;
    gap: 1rem;
    padding: 1rem;
    border-radius: 8px;
    background: #f8fafc;
}

.activity-icon {
    font-size: 1.25rem;
    background: #2563eb;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.activity-content {
    flex: 1;
}

.activity-content p {
    color: #1f2937;
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.activity-content small {
    color: #6b7280;
}

.activity-time {
    color: #9ca3af;
    font-size: 0.875rem;
}

.admin-actions h3 {
    color: #1f2937;
    margin-bottom: 1rem;
}

.quick-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.quick-action {
    padding: 0.75rem 1rem;
    background: #f3f4f6;
    border-radius: 6px;
    color: #374151;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.2s;
}

.quick-action:hover {
    background: #e5e7eb;
    text-decoration: none;
}

@media (max-width: 768px) {
    .admin-sections {
        grid-template-columns: 1fr;
    }
    
    .chart-item {
        grid-template-columns: 100px 1fr 30px;
        gap: 0.5rem;
    }
    
    .chart-label {
        font-size: 0.75rem;
    }
}
</style>
{% endblock %}
'''

# ================================================================
# AGGIORNAMENTO NAVBAR PER INCLUDERE ADMIN
# ================================================================

# src/web/templates/base.html - AGGIORNAMENTO
base_template_update = '''
<!-- Nel template base.html, aggiorna la navbar: -->
<div class="nav-menu">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="/employees" class="nav-link">Dipendenti</a>
    <a href="/organization" class="nav-link">Organigramma</a>
    <a href="/functions" class="nav-link">Funzioni</a>
    <a href="/admin" class="nav-link admin-link">🛠️ Admin</a>
</div>

<!-- Aggiungi questi stili CSS: -->
<style>
.admin-link {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
}

.admin-link:hover {
    background: rgba(255, 255, 255, 0.2);
}
</style>
'''

# ================================================================
# SCRIPT DI SETUP COMPLETO
# ================================================================

# setup_crud.py - Script per setup ambiente CRUD
setup_script = '''
#!/usr/bin/env python3
"""
Script di setup per sistema CRUD Organigramma Manager
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def create_directories():
    """Crea le directory necessarie"""
    directories = [
        "src/web/templates/admin",
        "src/web/routes",
        "src/utils",
        "data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory creata: {directory}")

def create_init_files():
    """Crea file __init__.py mancanti"""
    init_files = [
        "src/__init__.py",
        "src/database/__init__.py",
        "src/services/__init__.py", 
        "src/ui/__init__.py",
        "src/web/__init__.py",
        "src/web/routes/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ File init creato: {init_file}")

def install_dependencies():
    """Installa dipendenze Python"""
    dependencies = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.2",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "click>=8.1.7",
        "aiofiles>=23.2.1",
        "pillow>=10.0.0"
    ]
    
    print("📦 Installazione dipendenze...")
    for dep in dependencies:
        subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                      capture_output=True)
    print("✅ Dipendenze installate")

def create_templates():
    """Crea template HTML mancanti"""
    templates = {
        "src/web/templates/admin/persons.html": admin_persons_template,
        "src/web/templates/admin/person_form.html": person_form_template,
        "src/web/templates/admin/dashboard.html": admin_dashboard_template
    }
    
    for template_path, content in templates.items():
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Template creato: {template_path}")

def check_database():
    """Verifica esistenza e struttura database"""
    db_path = "data/organigramma.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database non trovato: {db_path}")
        print("   Esegui prima gli script SQL per creare il database")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica tabelle principali
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('persons', 'functions', 'roles')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if len(tables) == 3:
            print("✅ Database verificato")
            return True
        else:
            print(f"❌ Database incompleto. Tabelle trovate: {tables}")
            return False
            
    except Exception as e:
        print(f"❌ Errore verifica database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Funzione principale setup"""
    print("🚀 Setup CRUD Organigramma Manager")
    print("=" * 40)
    
    create_directories()
    create_init_files()
    install_dependencies()
    create_templates()
    
    if check_database():
        print("\n✅ Setup completato con successo!")
        print("\nComandi disponibili:")
        print("  python main.py start          # Avvia server")
        print("  python main.py start --debug  # Avvia con debug")
        print("  python main.py status --check-db  # Verifica stato")
        print("\nEndpoints CRUD:")
        print("  http://localhost:8000/admin   # Dashboard admin")
        print("  http://localhost:8000/api     # API endpoints")
    else:
        print("\n❌ Setup incompleto - verificare database")

if __name__ == "__main__":
    main()
'''

# ================================================================
# REQUIREMENTS.TXT COMPLETO
# ================================================================

requirements_complete = '''
# Core FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Templates e UI
jinja2==3.1.2
aiofiles==23.2.1

# Validazione dati
pydantic==2.5.0

# CLI
click==8.1.7

# Immagini (favicon)
pillow==10.0.0

# Utilities
python-dateutil==2.8.2

# Development (opzionali)
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
isort>=5.12.0
httpx>=0.25.0  # Per test API
'''

print("✅ Sistema CRUD completo implementato!")
print("\nCaratteristiche principali:")
print("- Repository pattern con metodi CRUD completi")
print("- Service layer con validazioni e business logic")
print("- API REST endpoints con Pydantic validation")
print("- Interfaccia web amministrativa")
print("- Operazioni bulk per modifiche massive")
print("- Sistema di audit trail integrato")
print("- Gestione soft delete e trasferimenti")
print("- Validazioni avanzate e gestione errori")
print("\nProssimi passi:")
print("1. Eseguire setup_crud.py per configurazione")
print("2. Testare endpoints API con /docs (Swagger)")
print("3. Utilizzare interfaccia admin su /admin")
print("4. Implementare eventuali personalizzazioni")

# ROUTE ESISTENTI (Dashboard, Employees, etc.)
# ================================================================

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

# ================================================================
# NUOVE ROUTE ADMIN
# ================================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard amministrativa"""
    stats = repository.get_detailed_stats()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "title": "Amministrazione",
        "stats": stats
    })

# API Endpoints esistenti
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
    try:
        # Test connessione database
        stats = repository.get_stats()
        return {
            "status": "ok", 
            "service": "organigramma-manager",
            "database": "connected",
            "total_persons": stats['total_persons']
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "organigramma-manager", 
            "database": "error",
            "error": str(e)
        }

# ================================================================