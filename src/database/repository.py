from typing import List, Optional, Dict, Tuple
from datetime import datetime, date
from .connection import DatabaseConnection
from .models import Function, FunctionTreeNode, JobTitle, Person, Role, OrgChartNode

class OrganigrammaRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def _dict_to_role(self, row_dict):
        """Converte dizionario da row database in oggetto Role"""
        return Role(
            id=row_dict.get('id'),
            person_name=row_dict.get('person_name', ''),
            function_name=row_dict.get('function_name', ''),
            organizational_unit=row_dict.get('organizational_unit'),
            job_title_name=row_dict.get('job_title_name'),
            percentage=row_dict.get('percentage', 1.0),
            ad_interim=bool(row_dict.get('ad_interim', False)),
            reports_to=row_dict.get('reports_to'),
            start_date=row_dict.get('start_date'),
            end_date=row_dict.get('end_date'),
            flags=row_dict.get('flags'),
            created_at=row_dict.get('created_at'),
            updated_at=row_dict.get('updated_at')
        )
    
    # ================================================================
    # FUNCTIONS - CRUD COMPLETO
    # ================================================================
    
    def get_all_functions(self) -> List[Function]:
        """Recupera tutte le funzioni"""
        query = "SELECT * FROM functions ORDER BY name"
        rows = self.db.execute_query(query)
        return [Function(**dict(row)) for row in rows]
    
    def get_function_tree(self) -> List[FunctionTreeNode]:
        """Recupera funzioni in formato ad albero"""
        query = """
        SELECT * FROM function_chart ORDER BY level, name
        """
        rows = self.db.execute_query(query)
        return [FunctionTreeNode(**dict(row)) for row in rows]
    
    def get_function(self, name: str) -> Optional[Function]:
        """Recupera singola funzione per nome"""
        query = "SELECT * FROM functions WHERE name = ?"
        rows = self.db.execute_query(query, (name,))
        return Function(**dict(rows[0])) if rows else None
    
    def get_function_by_id(self, function_id: int) -> Optional[Function]:
        """Recupera singola funzione per ID"""
        query = "SELECT * FROM functions WHERE id = ?"
        rows = self.db.execute_query(query, (function_id,))
        return Function(**dict(rows[0])) if rows else None
    
    def create_function(self, function: Function) -> int:
        """Crea nuova funzione"""
        query = """
        INSERT INTO functions (name, reports_to, flags)
        VALUES (?, ?, ?)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (function.name, function.reports_to, function.flags))
            conn.commit()
            return cursor.lastrowid # type: ignore
    
    def update_function(self, name: str, function: Function) -> bool:
        """Aggiorna funzione esistente"""
        query = """
        UPDATE functions 
        SET reports_to = ?, flags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE name = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (function.reports_to, function.flags, name))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_function(self, name: str) -> bool:
        """Elimina funzione (solo se non ha dipendenze)"""
        # Verifica dipendenze
        deps = self.get_function_dependencies(name)
        if deps['has_dependencies']:
            return False
        
        query = "DELETE FROM functions WHERE name = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_function_dependencies(self, name: str) -> Dict:
        """Verifica dipendenze di una funzione"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Funzioni che riportano a questa
            cursor.execute("SELECT COUNT(*) as count FROM functions WHERE reports_to = ?", (name,))
            sub_functions = cursor.fetchone()['count']
            
            # Ruoli in questa funzione
            cursor.execute("SELECT COUNT(*) as count FROM roles WHERE function_name = ? AND end_date IS NULL", (name,))
            active_roles = cursor.fetchone()['count']
            
            return {
                'has_dependencies': sub_functions > 0 or active_roles > 0,
                'sub_functions': sub_functions,
                'active_roles': active_roles
            }
    
    # ================================================================
    # PERSONS - CRUD COMPLETO
    # ================================================================
    
    def get_all_persons(self, active_only: bool = True) -> List[Person]:
        """Recupera tutti i dipendenti"""
        query = "SELECT * FROM persons"
        if active_only:
            query += " WHERE status = 'ACTIVE'"
        query += " ORDER BY name"
        rows = self.db.execute_query(query)
        return [Person(**dict(row)) for row in rows]
    
    def get_person(self, name: str) -> Optional[Person]:
        """Recupera singolo dipendente per nome"""
        query = "SELECT * FROM persons WHERE name = ?"
        rows = self.db.execute_query(query, (name,))
        return Person(**dict(rows[0])) if rows else None
    
    def get_person_by_id(self, person_id: int) -> Optional[Person]:
        """Recupera singolo dipendente per ID"""
        query = "SELECT * FROM persons WHERE id = ?"
        rows = self.db.execute_query(query, (person_id,))
        return Person(**dict(rows[0])) if rows else None
    
    def get_person_by_employee_id(self, employee_id: str) -> Optional[Person]:
        """Recupera dipendente per Employee ID"""
        query = "SELECT * FROM persons WHERE employee_id = ?"
        rows = self.db.execute_query(query, (employee_id,))
        return Person(**dict(rows[0])) if rows else None
    
    def create_person(self, person: Person) -> int:
        """Crea nuovo dipendente"""
        query = """
        INSERT INTO persons (name, email, employee_id, hire_date, status, flags)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                person.name, person.email, person.employee_id,
                person.hire_date, person.status, person.flags
            ))
            conn.commit()
            return cursor.lastrowid # type: ignore
    
    def update_person(self, name: str, person: Person) -> bool:
        """Aggiorna dipendente esistente"""
        query = """
        UPDATE persons 
        SET email = ?, employee_id = ?, hire_date = ?, status = ?, 
            flags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE name = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                person.email, person.employee_id, person.hire_date,
                person.status, person.flags, name
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def deactivate_person(self, name: str) -> bool:
        """Disattiva dipendente (soft delete)"""
        query = """
        UPDATE persons 
        SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP
        WHERE name = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_person(self, name: str) -> bool:
        """Elimina dipendente (solo se non ha ruoli attivi)"""
        # Verifica ruoli attivi
        active_roles = self.get_person_roles(name, active_only=True)
        if active_roles:
            return False
        
        query = "DELETE FROM persons WHERE name = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_persons(self, search_term: str) -> List[Person]:
        """Ricerca dipendenti per nome o alias"""
        query = """
        SELECT DISTINCT p.* FROM persons p
        LEFT JOIN person_aliases pa ON p.name = pa.person_name
        WHERE p.name LIKE ? OR pa.alias LIKE ? OR p.employee_id LIKE ?
        ORDER BY p.name
        """
        term = f"%{search_term}%"
        rows = self.db.execute_query(query, (term, term, term))
        return [Person(**dict(row)) for row in rows]
    
    # ================================================================
    # JOB TITLES - CRUD COMPLETO
    # ================================================================
    
    def get_all_job_titles(self) -> List[JobTitle]:
        """Recupera tutti i job titles"""
        query = "SELECT * FROM job_titles ORDER BY level, name"
        rows = self.db.execute_query(query)
        return [JobTitle(**dict(row)) for row in rows]
    
    def get_job_title(self, name: str) -> Optional[JobTitle]:
        """Recupera singolo job title per nome"""
        query = "SELECT * FROM job_titles WHERE name = ?"
        rows = self.db.execute_query(query, (name,))
        return JobTitle(**dict(rows[0])) if rows else None
    
    def create_job_title(self, job_title: JobTitle) -> int:
        """Crea nuovo job title"""
        query = """
        INSERT INTO job_titles (name, level, flags)
        VALUES (?, ?, ?)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (job_title.name, job_title.level, job_title.flags))
            conn.commit()
            return cursor.lastrowid # type: ignore
    
    def update_job_title(self, name: str, job_title: JobTitle) -> bool:
        """Aggiorna job title esistente"""
        query = """
        UPDATE job_titles 
        SET level = ?, flags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE name = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (job_title.level, job_title.flags, name))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_job_title(self, name: str) -> bool:
        """Elimina job title (solo se non in uso)"""
        # Verifica se in uso
        query_check = "SELECT COUNT(*) as count FROM roles WHERE job_title_name = ? AND end_date IS NULL"
        rows = self.db.execute_query(query_check, (name,))
        if rows[0]['count'] > 0:
            return False
        
        query = "DELETE FROM job_titles WHERE name = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ================================================================
    # ROLES - CRUD COMPLETO
    # ================================================================
    
    def get_person_roles(self, person_name: str, active_only: bool = True) -> List[Role]:
        """Recupera ruoli di una persona"""
        query = "SELECT * FROM roles WHERE person_name = ?"
        if active_only:
            query += " AND end_date IS NULL"
        query += " ORDER BY function_name"
        rows = self.db.execute_query(query, (person_name,))
        return [Role(**dict(row)) for row in rows]
    
    def get_function_roles(self, function_name: str, active_only: bool = True) -> List[Role]:
        """Recupera ruoli di una funzione"""
        query = "SELECT * FROM roles WHERE function_name = ?"
        if active_only:
            query += " AND end_date IS NULL"
        query += " ORDER BY person_name"
        rows = self.db.execute_query(query, (function_name,))
        return [Role(**dict(row)) for row in rows]
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """Recupera singolo ruolo per ID"""
        query = "SELECT * FROM roles WHERE id = ?"
        rows = self.db.execute_query(query, (role_id,))
        return Role(**dict(rows[0])) if rows else None
    
    def create_role(self, role: Role) -> int:
        """Crea nuovo ruolo"""
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
                role.reports_to, role.start_date or date.today(), role.flags
            ))
            conn.commit()
            return cursor.lastrowid # type: ignore
    
    def update_role(self, role_id: int, role: Role) -> bool:
        """Aggiorna ruolo esistente"""
        query = """
        UPDATE roles 
        SET organizational_unit = ?, job_title_name = ?, percentage = ?,
            ad_interim = ?, reports_to = ?, flags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                role.organizational_unit, role.job_title_name, role.percentage,
                role.ad_interim, role.reports_to, role.flags, role_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def end_role(self, role_id: int, end_date: Optional[date] = None) -> bool:
        """Termina ruolo (soft delete)"""
        if not end_date:
            end_date = date.today()
        
        query = """
        UPDATE roles 
        SET end_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND end_date IS NULL
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (end_date, role_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_role(self, role_id: int) -> bool:
        """Elimina ruolo permanentemente"""
        query = "DELETE FROM roles WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (role_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def transfer_role(self, role_id: int, new_person_name: str, 
                     transfer_date: Optional[date] = None) -> Tuple[bool, Optional[int]]:
        """Trasferisce ruolo da una persona ad un'altra"""
        if not transfer_date:
            transfer_date = date.today()
        
        # Recupera ruolo originale
        original_role = self.get_role(role_id)
        if not original_role:
            return False, None
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Termina ruolo originale
            cursor.execute(
                "UPDATE roles SET end_date = ? WHERE id = ?",
                (transfer_date, role_id)
            )
            
            # Crea nuovo ruolo per nuova persona
            cursor.execute("""
                INSERT INTO roles (person_name, function_name, organizational_unit,
                                  job_title_name, percentage, ad_interim, reports_to,
                                  start_date, flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_person_name, original_role.function_name, original_role.organizational_unit,
                original_role.job_title_name, original_role.percentage, original_role.ad_interim,
                original_role.reports_to, transfer_date, original_role.flags
            ))
            
            new_role_id = cursor.lastrowid
            conn.commit()
            
            return True, new_role_id
    
    # ================================================================
    # ALIASES - CRUD COMPLETO
    # ================================================================
    
    def get_person_aliases(self, person_name: str) -> List[str]:
        """Recupera alias di una persona"""
        query = "SELECT alias FROM person_aliases WHERE person_name = ?"
        rows = self.db.execute_query(query, (person_name,))
        return [row['alias'] for row in rows]
    
    def add_person_alias(self, person_name: str, alias: str, flags: Optional[str] = None) -> bool:
        """Aggiunge alias a una persona"""
        query = "INSERT OR IGNORE INTO person_aliases (person_name, alias, flags) VALUES (?, ?, ?)"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (person_name, alias, flags))
            conn.commit()
            return cursor.rowcount > 0
    
    def remove_person_alias(self, person_name: str, alias: str) -> bool:
        """Rimuove alias da una persona"""
        query = "DELETE FROM person_aliases WHERE person_name = ? AND alias = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (person_name, alias))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_function_aliases(self, function_name: str) -> List[str]:
        """Recupera alias di una funzione"""
        query = "SELECT alias FROM function_aliases WHERE function_name = ?"
        rows = self.db.execute_query(query, (function_name,))
        return [row['alias'] for row in rows]
    
    def add_function_alias(self, function_name: str, alias: str, flags: Optional[str] = None) -> bool:
        """Aggiunge alias a una funzione"""
        query = "INSERT OR IGNORE INTO function_aliases (function_name, alias, flags) VALUES (?, ?, ?)"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (function_name, alias, flags))
            conn.commit()
            return cursor.rowcount > 0
    
    # ================================================================
    # ORGANIZATION CHART - READONLY
    # ================================================================
    
    def get_organization_chart(self) -> List[OrgChartNode]:
        """Recupera organigramma completo"""
        query = "SELECT * FROM organization_chart ORDER BY level, function_name, person_name"
        rows = self.db.execute_query(query)
        return [OrgChartNode(**dict(row)) for row in rows]
    
    def get_direct_reports(self, manager_name: str) -> List[Role]:
        """Recupera persone che riportano a un manager"""
        query = """
        SELECT * FROM roles 
        WHERE reports_to = ? AND end_date IS NULL
        ORDER BY function_name, person_name
        """
        rows = self.db.execute_query(query, (manager_name,))
        return [Role(**dict(row)) for row in rows]
    
    # ================================================================
    # STATISTICS
    # ================================================================
    
    def get_stats(self) -> Dict:
        """Recupera statistiche generali"""
        stats = {}
        
        # Conteggi base
        stats['total_persons'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM persons WHERE status='ACTIVE'"
        )[0]['count']
        
        stats['total_functions'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM functions"
        )[0]['count']
        
        stats['total_roles'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM roles WHERE end_date IS NULL"
        )[0]['count']
        
        stats['interim_roles'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM roles WHERE ad_interim=1 AND end_date IS NULL"
        )[0]['count']
        
        # Persone con ruoli multipli
        multi_role_query = """
        SELECT COUNT(*) as count FROM (
            SELECT person_name FROM roles WHERE end_date IS NULL 
            GROUP BY person_name HAVING COUNT(*) > 1
        )
        """
        stats['multi_role_persons'] = self.db.execute_query(multi_role_query)[0]['count']
        
        return stats
    
    def get_detailed_stats(self) -> Dict:
        """Statistiche dettagliate per dashboard admin"""
        stats = self.get_stats()
        
        # Statistiche per funzione
        function_stats = self.db.execute_query("""
            SELECT f.name, COUNT(r.id) as role_count
            FROM functions f
            LEFT JOIN roles r ON f.name = r.function_name AND r.end_date IS NULL
            GROUP BY f.name
            ORDER BY role_count DESC
        """)
        stats['functions_by_headcount'] = [dict(row) for row in function_stats]
        
        # Job titles più comuni
        job_title_stats = self.db.execute_query("""
            SELECT job_title_name, COUNT(*) as count
            FROM roles 
            WHERE end_date IS NULL AND job_title_name IS NOT NULL
            GROUP BY job_title_name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_job_titles'] = [dict(row) for row in job_title_stats]
        
        # Persone con più ruoli
        multi_role_details = self.db.execute_query("""
            SELECT person_name, COUNT(*) as role_count
            FROM roles 
            WHERE end_date IS NULL
            GROUP BY person_name
            HAVING COUNT(*) > 1
            ORDER BY role_count DESC
        """)
        stats['multi_role_details'] = [dict(row) for row in multi_role_details]
        
        return stats
    
    # ================================================================
    # BULK OPERATIONS
    # ================================================================
    
    def bulk_update_roles_reports_to(self, old_manager: str, new_manager: str) -> int:
        """Aggiorna in massa i report per cambio manager"""
        query = """
        UPDATE roles 
        SET reports_to = ?, updated_at = CURRENT_TIMESTAMP
        WHERE reports_to = ? AND end_date IS NULL
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (new_manager, old_manager))
            conn.commit()
            return cursor.rowcount
    
    def bulk_end_person_roles(self, person_name: str, end_date: Optional[date] = None) -> int:
        """Termina tutti i ruoli di una persona"""
        if not end_date:
            end_date = date.today()
        
        query = """
        UPDATE roles 
        SET end_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE person_name = ? AND end_date IS NULL
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (end_date, person_name))
            conn.commit()
            return cursor.rowcount
