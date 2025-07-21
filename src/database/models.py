from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date

@dataclass
class Function:
    id: Optional[int] = None
    name: str = ""
    reports_to: Optional[str] = None
    flags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class JobTitle:
    id: Optional[int] = None
    name: str = ""
    level: Optional[int] = None
    flags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Person:
    id: Optional[int] = None
    name: str = ""
    email: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[date] = None
    status: str = "ACTIVE"
    flags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Role:
    id: Optional[int] = None
    person_name: str = ""
    function_name: str = ""
    organizational_unit: Optional[str] = None
    job_title_name: Optional[str] = None
    percentage: float = 1.0
    ad_interim: bool = False
    reports_to: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    flags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OrgChartNode:
    function_name: str
    level: int
    path: str
    person_name: Optional[str] = None
    job_title_name: Optional[str] = None
    organizational_unit: Optional[str] = None
    ad_interim: bool = False
    reports_to: Optional[str] = None
    person_reports_to: Optional[str] = None