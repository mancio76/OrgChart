from typing import List, Optional, Dict
from ..database.repository import OrganigrammaRepository
from ..database.models import Person, Role, OrgChartNode

class OrganigrammaService:
    def __init__(self, repository: OrganigrammaRepository):
        self.repo = repository
    
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
        """Modifiche recenti (da implementare con audit trail)"""
        return []  # Placeholder
    
    def _get_interim_roles(self) -> List[Role]:
        """Ruoli ad interim attivi"""
        query = "SELECT * FROM roles WHERE ad_interim=1 AND end_date IS NULL ORDER BY start_date DESC"
        rows = self.repo.db.execute_query(query)
        return [Role(**dict(row)) for row in rows]