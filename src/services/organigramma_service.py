from typing import List, Optional, Dict, Tuple
from datetime import date
from ..database.repository import OrganigrammaRepository
from ..database.models import Person, Role, Function, JobTitle, OrgChartNode

class CRUDValidationError(Exception):
    """Eccezione per errori di validazione CRUD"""
    pass

class OrganigrammaService:
    def __init__(self, repository: OrganigrammaRepository):
        self.repo = repository
    
    # ================================================================
    # PERSONS - CRUD SERVICE LAYER
    # ================================================================
    
    def create_person(self, person_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Crea nuovo dipendente con validazione"""
        try:
            # Validazione
            if not person_data.get('name', '').strip():
                return False, "Nome richiesto", None
            
            # Verifica duplicati
            if self.repo.get_person(person_data['name']):
                return False, "Dipendente già esistente", None
            
            if person_data.get('employee_id'):
                if self.repo.get_person_by_employee_id(person_data['employee_id']):
                    return False, "Employee ID già in uso", None
            
            # Crea oggetto Person
            person = Person(
                name=person_data['name'],
                email=person_data.get('email'),
                employee_id=person_data.get('employee_id'),
                hire_date=person_data.get('hire_date'),
                status=person_data.get('status', 'ACTIVE'),
                flags=person_data.get('flags')
            )
            
            person_id = self.repo.create_person(person)
            
            # Aggiungi aliases se presenti
            for alias in person_data.get('aliases', []):
                self.repo.add_person_alias(person.name, alias)
            
            return True, "Dipendente creato con successo", person_id
            
        except Exception as e:
            return False, f"Errore durante la creazione: {str(e)}", None
    
    def update_person(self, person_name: str, person_data: Dict) -> Tuple[bool, str]:
        """Aggiorna dipendente esistente"""
        try:
            # Verifica esistenza
            existing = self.repo.get_person(person_name)
            if not existing:
                return False, "Dipendente non trovato"
            
            # Aggiorna oggetto
            existing.email = person_data.get('email', existing.email)
            existing.employee_id = person_data.get('employee_id', existing.employee_id)
            existing.hire_date = person_data.get('hire_date', existing.hire_date)
            existing.status = person_data.get('status', existing.status)
            existing.flags = person_data.get('flags', existing.flags)
            
            success = self.repo.update_person(person_name, existing)
            return success, "Dipendente aggiornato" if success else "Errore aggiornamento"
            
        except Exception as e:
            return False, f"Errore durante l'aggiornamento: {str(e)}"
    
    def delete_person(self, person_name: str) -> Tuple[bool, str]:
        """Elimina dipendente (con controlli)"""
        try:
            # Verifica ruoli attivi
            active_roles = self.repo.get_person_roles(person_name, active_only=True)
            if active_roles:
                return False, f"Impossibile eliminare: {len(active_roles)} ruoli attivi"
            
            success = self.repo.delete_person(person_name)
            return success, "Dipendente eliminato" if success else "Errore eliminazione"
            
        except Exception as e:
            return False, f"Errore durante l'eliminazione: {str(e)}"
    
    # ================================================================
    # FUNCTIONS - CRUD SERVICE LAYER
    # ================================================================
    
    def create_function(self, function_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Crea nuova funzione con validazione"""
        try:
            if not function_data.get('name', '').strip():
                return False, "Nome funzione richiesto", None
            
            # Verifica duplicati
            if self.repo.get_function(function_data['name']):
                return False, "Funzione già esistente", None
            
            function = Function(
                name=function_data['name'],
                reports_to=function_data.get('reports_to'),
                flags=function_data.get('flags')
            )
            
            function_id = self.repo.create_function(function)
            return True, "Funzione creata con successo", function_id
            
        except Exception as e:
            return False, f"Errore durante la creazione: {str(e)}", None
    
    def update_function(self, function_name: str, function_data: Dict) -> Tuple[bool, str]:
        """Aggiorna funzione esistente"""
        try:
            existing = self.repo.get_function(function_name)
            if not existing:
                return False, "Funzione non trovata"
            
            existing.reports_to = function_data.get('reports_to', existing.reports_to)
            existing.flags = function_data.get('flags', existing.flags)
            
            success = self.repo.update_function(function_name, existing)
            return success, "Funzione aggiornata" if success else "Errore aggiornamento"
            
        except Exception as e:
            return False, f"Errore durante l'aggiornamento: {str(e)}"
    
    def delete_function(self, function_name: str) -> Tuple[bool, str]:
        """Elimina funzione (con controlli dipendenze)"""
        try:
            deps = self.repo.get_function_dependencies(function_name)
            if deps['has_dependencies']:
                msg = f"Impossibile eliminare: {deps['sub_functions']} sotto-funzioni, {deps['active_roles']} ruoli attivi"
                return False, msg
            
            success = self.repo.delete_function(function_name)
            return success, "Funzione eliminata" if success else "Errore eliminazione"
            
        except Exception as e:
            return False, f"Errore durante l'eliminazione: {str(e)}"
    
    # ================================================================
    # ROLES - CRUD SERVICE LAYER
    # ================================================================
    
    def create_role(self, role_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Crea nuovo ruolo con validazione"""
        try:
            # Validazioni
            if not role_data.get('person_name'):
                return False, "Nome persona richiesto", None
            if not role_data.get('function_name'):
                return False, "Nome funzione richiesto", None
            
            # Verifica esistenza persona e funzione
            if not self.repo.get_person(role_data['person_name']):
                return False, "Persona non trovata", None
            if not self.repo.get_function(role_data['function_name']):
                return False, "Funzione non trovata", None
            
            role = Role(
                person_name=role_data['person_name'],
                function_name=role_data['function_name'],
                organizational_unit=role_data.get('organizational_unit'),
                job_title_name=role_data.get('job_title_name'),
                percentage=float(role_data.get('percentage', 1.0)),
                ad_interim=bool(role_data.get('ad_interim', False)),
                reports_to=role_data.get('reports_to'),
                start_date=role_data.get('start_date'),
                flags=role_data.get('flags')
            )
            
            role_id = self.repo.create_role(role)
            return True, "Ruolo creato con successo", role_id
            
        except Exception as e:
            return False, f"Errore durante la creazione: {str(e)}", None
    
    def update_role(self, role_id: int, role_data: Dict) -> Tuple[bool, str]:
        """Aggiorna ruolo esistente"""
        try:
            existing = self.repo.get_role(role_id)
            if not existing:
                return False, "Ruolo non trovato"
            
            existing.organizational_unit = role_data.get('organizational_unit', existing.organizational_unit)
            existing.job_title_name = role_data.get('job_title_name', existing.job_title_name)
            existing.percentage = float(role_data.get('percentage', existing.percentage))
            existing.ad_interim = bool(role_data.get('ad_interim', existing.ad_interim))
            existing.reports_to = role_data.get('reports_to', existing.reports_to)
            existing.flags = role_data.get('flags', existing.flags)
            
            success = self.repo.update_role(role_id, existing)
            return success, "Ruolo aggiornato" if success else "Errore aggiornamento"
            
        except Exception as e:
            return False, f"Errore durante l'aggiornamento: {str(e)}"
    
    def end_role(self, role_id: int, end_date: Optional[date] = None) -> Tuple[bool, str]:
        """Termina ruolo"""
        try:
            success = self.repo.end_role(role_id, end_date)
            return success, "Ruolo terminato" if success else "Errore terminazione"
        except Exception as e:
            return False, f"Errore durante la terminazione: {str(e)}"
    
    def transfer_role(self, role_id: int, new_person_name: str, 
                     transfer_date: Optional[date] = None) -> Tuple[bool, str, Optional[int]]:
        """Trasferisce ruolo ad altra persona"""
        try:
            # Verifica esistenza nuova persona
            if not self.repo.get_person(new_person_name):
                return False, "Persona destinataria non trovata", None
            
            success, new_role_id = self.repo.transfer_role(role_id, new_person_name, transfer_date)
            return success, "Ruolo trasferito" if success else "Errore trasferimento", new_role_id
            
        except Exception as e:
            return False, f"Errore durante il trasferimento: {str(e)}", None
    
    # ================================================================
    # JOB TITLES - CRUD SERVICE LAYER
    # ================================================================
    
    def create_job_title(self, job_title_data: Dict) -> Tuple[bool, str, Optional[int]]:
        """Crea nuovo job title"""
        try:
            if not job_title_data.get('name', '').strip():
                return False, "Nome job title richiesto", None
            
            if self.repo.get_job_title(job_title_data['name']):
                return False, "Job title già esistente", None
            
            job_title = JobTitle(
                name=job_title_data['name'],
                level=job_title_data.get('level'),
                flags=job_title_data.get('flags')
            )
            
            job_title_id = self.repo.create_job_title(job_title)
            return True, "Job title creato con successo", job_title_id
            
        except Exception as e:
            return False, f"Errore durante la creazione: {str(e)}", None
    
    def update_job_title(self, job_title_name: str, job_title_data: Dict) -> Tuple[bool, str]:
        """Aggiorna job title esistente"""
        try:
            existing = self.repo.get_job_title(job_title_name)
            if not existing:
                return False, "Job title non trovato"
            
            existing.level = job_title_data.get('level', existing.level)
            existing.flags = job_title_data.get('flags', existing.flags)
            
            success = self.repo.update_job_title(job_title_name, existing)
            return success, "Job title aggiornato" if success else "Errore aggiornamento"
            
        except Exception as e:
            return False, f"Errore durante l'aggiornamento: {str(e)}"
    
    def delete_job_title(self, job_title_name: str) -> Tuple[bool, str]:
        """Elimina job title"""
        try:
            success = self.repo.delete_job_title(job_title_name)
            if not success:
                return False, "Job title in uso, impossibile eliminare"
            return True, "Job title eliminato"
            
        except Exception as e:
            return False, f"Errore durante l'eliminazione: {str(e)}"
    
    # ================================================================
    # ADVANCED OPERATIONS
    # ================================================================
    
    def reorganize_function(self, function_name: str, new_reports_to: Optional[str]) -> Tuple[bool, str]:
        """Sposta funzione nella gerarchia"""
        try:
            # Verifica cicli nella gerarchia
            if new_reports_to and self._would_create_cycle(function_name, new_reports_to):
                return False, "Operazione creerebbe un ciclo nella gerarchia"
            
            function = self.repo.get_function(function_name)
            if not function:
                return False, "Funzione non trovata"
            
            function.reports_to = new_reports_to
            success = self.repo.update_function(function_name, function)
            return success, "Funzione riorganizzata" if success else "Errore riorganizzazione"
            
        except Exception as e:
            return False, f"Errore durante la riorganizzazione: {str(e)}"
    
    def _would_create_cycle(self, function_name: str, new_parent: str) -> bool:
        """Verifica se assegnare new_parent come parent di function_name creerebbe un ciclo"""
        current = new_parent
        visited = set()
        
        while current:
            if current == function_name:
                return True
            if current in visited:
                break  # Ciclo esistente, ma non coinvolge function_name
            visited.add(current)
            
            parent_function = self.repo.get_function(current)
            current = parent_function.reports_to if parent_function else None
        
        return False
    
    def bulk_change_manager(self, old_manager: str, new_manager: str) -> Tuple[bool, str, int]:
        """Cambia manager per tutti i report"""
        try:
            # Verifica esistenza nuovo manager
            if not self.repo.get_person(new_manager):
                return False, "Nuovo manager non trovato", 0
            
            affected_count = self.repo.bulk_update_roles_reports_to(old_manager, new_manager)
            return True, f"{affected_count} ruoli aggiornati", affected_count
            
        except Exception as e:
            return False, f"Errore durante il cambio manager: {str(e)}", 0
    
    def terminate_employee(self, person_name: str, termination_date: Optional[date] = None) -> Tuple[bool, str, int]:
        """Termina dipendente e tutti i suoi ruoli"""
        try:
            if not termination_date:
                termination_date = date.today()
            
            # Termina tutti i ruoli
            roles_count = self.repo.bulk_end_person_roles(person_name, termination_date)
            
            # Disattiva persona
            person_success, person_msg = self.update_person(person_name, {'status': 'TERMINATED'})
            
            if person_success:
                return True, f"Dipendente terminato, {roles_count} ruoli terminati", roles_count
            else:
                return False, f"Errore durante terminazione: {person_msg}", roles_count
                
        except Exception as e:
            return False, f"Errore durante la terminazione: {str(e)}", 0
    
    # ================================================================
    # VALIDATION HELPERS
    # ================================================================
    
    def validate_person_data(self, person_data: Dict) -> List[str]:
        """Valida dati persona"""
        errors = []
        
        if not person_data.get('name', '').strip():
            errors.append("Nome richiesto")
        
        if person_data.get('email') and '@' not in person_data['email']:
            errors.append("Email non valida")
        
        if person_data.get('status') not in ['ACTIVE', 'INACTIVE', 'TERMINATED']:
            errors.append("Status non valido")
        
        return errors
    
    def validate_role_data(self, role_data: Dict) -> List[str]:
        """Valida dati ruolo"""
        errors = []
        
        if not role_data.get('person_name'):
            errors.append("Nome persona richiesto")
        
        if not role_data.get('function_name'):
            errors.append("Nome funzione richiesto")
        
        try:
            percentage = float(role_data.get('percentage', 1.0))
            if percentage <= 0 or percentage > 1:
                errors.append("Percentuale deve essere tra 0.01 e 1.0")
        except (ValueError, TypeError):
            errors.append("Percentuale non valida")
        
        return errors
    
    # ================================================================
    # EXISTING METHODS (from original service)
    # ================================================================
    
    def get_dashboard_data(self) -> Dict:
        """Dati per dashboard principale"""
        return {
            'stats': self.repo.get_stats(),
            'recent_changes': self._get_recent_changes(),
            'interim_roles': self._get_interim_roles()
        }
    
    def search_employees(self, query: str) -> List[Person]:
        """Ricerca dipendenti per nome o alias"""
        if len(query) < 2:
            return []
        return self.repo.search_persons(query)
    
    def get_employee_profile(self, person_name: str) -> Optional[Dict]:
        """Profilo completo dipendente con ruoli e reporting"""
        person = self.repo.get_person(person_name)
        if not person:
            return None
        
        roles = self.repo.get_person_roles(person_name)
        reports = self.repo.get_direct_reports(person_name)
        
        return {
            'person': person,
            'roles': roles,
            'direct_reports': reports,
            'reports_count': len(reports)
        }
    
    def get_organization_tree(self) -> List[OrgChartNode]:
        """Organigramma completo strutturato"""
        return self.repo.get_organization_chart()
    
    def get_function_details(self, function_name: str) -> Optional[Dict]:
        """Dettagli funzione con persone assegnate"""
        function = self.repo.get_function(function_name)
        if not function:
            return None
        
        roles = self.repo.get_function_roles(function_name)
        return {
            'function': function,
            'roles': roles,
            'headcount': len(roles)
        }
    
    def _get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Modifiche recenti (implementazione con audit trail)"""
        query = """
        SELECT * FROM role_history 
        ORDER BY change_date DESC 
        LIMIT ?
        """
        rows = self.repo.db.execute_query(query, (limit,))
        return [dict(row) for row in rows]
    
    def _get_interim_roles(self) -> List[Role]:
        """Ruoli ad interim attivi"""
        query = "SELECT * FROM roles WHERE ad_interim=1 AND end_date IS NULL ORDER BY start_date DESC"
        rows = self.repo.db.execute_query(query)
        return [Role(**dict(row)) for row in rows]