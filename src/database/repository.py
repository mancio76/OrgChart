from typing import List, Optional
from .connection import DatabaseConnection
from .models import Function, JobTitle, Person, Role, OrgChartNode

class OrganigrammaRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    # FUNCTIONS
    def get_all_functions(self) -> List[Function]:
        query = "SELECT * FROM functions ORDER BY name"
        rows = self.db.execute_query(query)
        return [Function(**dict(row)) for row in rows]
    
    def get_function(self, name: str) -> Optional[Function]:
        query = "SELECT * FROM functions WHERE name = ?"
        rows = self.db.execute_query(query, (name,))
        return Function(**dict(rows[0])) if rows else None
    
    # PERSONS
    def get_all_persons(self, active_only: bool = True) -> List[Person]:
        query = "SELECT * FROM persons"
        if active_only:
            query += " WHERE status = 'ACTIVE'"
        query += " ORDER BY name"
        rows = self.db.execute_query(query)
        return [Person(**dict(row)) for row in rows]
    
    def get_person(self, name: str) -> Optional[Person]:
        query = "SELECT * FROM persons WHERE name = ?"
        rows = self.db.execute_query(query, (name,))
        return Person(**dict(rows[0])) if rows else None
    
    def search_persons(self, search_term: str) -> List[Person]:
        query = """
        SELECT DISTINCT p.* FROM persons p
        LEFT JOIN person_aliases pa ON p.name = pa.person_name
        WHERE p.name LIKE ? OR pa.alias LIKE ?
        ORDER BY p.name
        """
        term = f"%{search_term}%"
        rows = self.db.execute_query(query, (term, term))
        return [Person(**dict(row)) for row in rows]
    
    # ROLES
    def get_person_roles(self, person_name: str, active_only: bool = True) -> List[Role]:
        query = "SELECT * FROM roles WHERE person_name = ?"
        if active_only:
            query += " AND end_date IS NULL"
        query += " ORDER BY function_name"
        rows = self.db.execute_query(query, (person_name,))
        return [Role(**dict(row)) for row in rows]
    
    def get_function_roles(self, function_name: str, active_only: bool = True) -> List[Role]:
        query = "SELECT * FROM roles WHERE function_name = ?"
        if active_only:
            query += " AND end_date IS NULL"
        query += " ORDER BY person_name"
        rows = self.db.execute_query(query, (function_name,))
        return [Role(**dict(row)) for row in rows]
    
    def add_role(self, role: Role) -> int:
        query = """
        INSERT INTO roles (person_name, function_name, organizational_unit,
                          job_title_name, percentage, ad_interim, reports_to,
                          start_date, flags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                role.person_name, role.function_name, role.organizational_unit,
                role.job_title_name, role.percentage, role.ad_interim,
                role.reports_to, role.start_date, role.flags
            ))
            conn.commit()
            return cursor.lastrowid
    
    # ORGANIZATION CHART
    def get_organization_chart(self) -> List[OrgChartNode]:
        query = "SELECT * FROM organization_chart ORDER BY level, function_name, person_name"
        rows = self.db.execute_query(query)
        return [OrgChartNode(**dict(row)) for row in rows]
    
    def get_direct_reports(self, manager_name: str) -> List[Role]:
        query = """
        SELECT * FROM roles 
        WHERE reports_to = ? AND end_date IS NULL
        ORDER BY function_name, person_name
        """
        rows = self.db.execute_query(query, (manager_name,))
        return [Role(**dict(row)) for row in rows]
    
    # STATISTICS
    def get_stats(self) -> dict:
        stats = {}
        
        # Conteggi base
        stats['total_persons'] = self.db.execute_query("SELECT COUNT(*) as count FROM persons WHERE status='ACTIVE'")[0]['count']
        stats['total_functions'] = self.db.execute_query("SELECT COUNT(*) as count FROM functions")[0]['count']
        stats['total_roles'] = self.db.execute_query("SELECT COUNT(*) as count FROM roles WHERE end_date IS NULL")[0]['count']
        stats['interim_roles'] = self.db.execute_query("SELECT COUNT(*) as count FROM roles WHERE ad_interim=1 AND end_date IS NULL")[0]['count']
        
        # Persone con ruoli multipli
        multi_role_query = """
        SELECT COUNT(*) as count FROM (
            SELECT person_name FROM roles WHERE end_date IS NULL 
            GROUP BY person_name HAVING COUNT(*) > 1
        )
        """
        stats['multi_role_persons'] = self.db.execute_query(multi_role_query)[0]['count']
        
        return stats