-- Organigramma Database SQLite Schema
-- Database per gestione organigramma aziendale con flags e ottimizzazioni

-- Tabella funzioni organizzative
CREATE TABLE functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    reports_to TEXT REFERENCES functions(name),
    flags TEXT(25),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alias delle funzioni
CREATE TABLE function_aliases (
    function_name TEXT REFERENCES functions(name) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    flags TEXT(25),
    PRIMARY KEY (function_name, alias)
);

-- Tabella job titles
CREATE TABLE job_titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    level INTEGER,  -- Livello gerarchico (1=C-Level, 2=Manager, etc.)
    flags TEXT(25),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alias dei job titles
CREATE TABLE job_title_aliases (
    job_title_name TEXT REFERENCES job_titles(name) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    flags TEXT(25),
    PRIMARY KEY (job_title_name, alias)
);

-- Tabella persone
CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    employee_id TEXT UNIQUE,
    hire_date DATE,
    status TEXT CHECK (status IN ('ACTIVE', 'INACTIVE', 'TERMINATED')) DEFAULT 'ACTIVE',
    flags TEXT(25),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alias delle persone
CREATE TABLE person_aliases (
    person_name TEXT REFERENCES persons(name) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    flags TEXT(25),
    PRIMARY KEY (person_name, alias)
);

-- Tabella ruoli (relazione molti-a-molti)
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT NOT NULL REFERENCES persons(name) ON DELETE CASCADE,
    function_name TEXT NOT NULL REFERENCES functions(name) ON DELETE CASCADE,
    organizational_unit TEXT,
    job_title_name TEXT REFERENCES job_titles(name),
    percentage REAL DEFAULT 1.0 CHECK (percentage > 0 AND percentage <= 1),
    ad_interim BOOLEAN DEFAULT FALSE,
    reports_to TEXT REFERENCES persons(name),
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    flags TEXT(25),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Tabella storico ruoli per audit trail
CREATE TABLE role_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER REFERENCES roles(id),
    person_name TEXT NOT NULL,
    function_name TEXT NOT NULL,
    organizational_unit TEXT,
    job_title_name TEXT,
    percentage REAL,
    ad_interim BOOLEAN,
    reports_to TEXT,
    start_date DATE,
    end_date DATE,
    action TEXT CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_by TEXT,
    change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    flags TEXT(25)
);

-- Indici per performance
CREATE INDEX idx_functions_reports_to ON functions(reports_to);
CREATE INDEX idx_persons_status ON persons(status);
CREATE INDEX idx_persons_employee_id ON persons(employee_id);
CREATE INDEX idx_roles_person ON roles(person_name);
CREATE INDEX idx_roles_function ON roles(function_name);
CREATE INDEX idx_roles_reports_to ON roles(reports_to);
CREATE INDEX idx_roles_dates ON roles(start_date, end_date);
CREATE INDEX idx_roles_active ON roles(person_name, function_name) WHERE end_date IS NULL;
CREATE INDEX idx_job_titles_level ON job_titles(level);

-- Trigger per updated_at automatico
CREATE TRIGGER update_functions_timestamp 
    AFTER UPDATE ON functions
BEGIN
    UPDATE functions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_job_titles_timestamp 
    AFTER UPDATE ON job_titles
BEGIN
    UPDATE job_titles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_persons_timestamp 
    AFTER UPDATE ON persons
BEGIN
    UPDATE persons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_roles_timestamp 
    AFTER UPDATE ON roles
BEGIN
    UPDATE roles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger per audit trail
CREATE TRIGGER role_audit_insert 
    AFTER INSERT ON roles
BEGIN
    INSERT INTO role_history (
        role_id, person_name, function_name, organizational_unit,
        job_title_name, percentage, ad_interim, reports_to,
        start_date, end_date, action, flags
    ) VALUES (
        NEW.id, NEW.person_name, NEW.function_name, NEW.organizational_unit,
        NEW.job_title_name, NEW.percentage, NEW.ad_interim, NEW.reports_to,
        NEW.start_date, NEW.end_date, 'INSERT', NEW.flags
    );
END;

CREATE TRIGGER role_audit_update 
    AFTER UPDATE ON roles
BEGIN
    INSERT INTO role_history (
        role_id, person_name, function_name, organizational_unit,
        job_title_name, percentage, ad_interim, reports_to,
        start_date, end_date, action, flags
    ) VALUES (
        NEW.id, NEW.person_name, NEW.function_name, NEW.organizational_unit,
        NEW.job_title_name, NEW.percentage, NEW.ad_interim, NEW.reports_to,
        NEW.start_date, NEW.end_date, 'UPDATE', NEW.flags
    );
END;

-- View per ruoli attivi
CREATE VIEW active_roles AS
SELECT 
    r.*,
    p.email,
    p.employee_id,
    p.status as person_status,
    jt.level as job_level
FROM roles r
JOIN persons p ON r.person_name = p.name
LEFT JOIN job_titles jt ON r.job_title_name = jt.name
WHERE r.end_date IS NULL 
AND p.status = 'ACTIVE';

-- View per organigramma completo
CREATE VIEW organization_chart AS
WITH RECURSIVE org_tree AS (
    -- Base case: top-level functions
    SELECT 
        f.name as function_name,
        f.reports_to,
        0 as level,
        f.name as path
    FROM functions f
    WHERE f.reports_to IS NULL OR f.reports_to = ''
    
    UNION ALL
    
    -- Recursive case
    SELECT 
        f.name,
        f.reports_to,
        ot.level + 1,
        ot.path || ' > ' || f.name
    FROM functions f
    JOIN org_tree ot ON f.reports_to = ot.function_name
)
SELECT 
    ot.*,
    ar.person_name,
    ar.job_title_name,
    ar.organizational_unit,
    ar.ad_interim,
    ar.reports_to as person_reports_to
FROM org_tree ot
LEFT JOIN active_roles ar ON ot.function_name = ar.function_name
ORDER BY ot.level, ot.function_name, ar.person_name;