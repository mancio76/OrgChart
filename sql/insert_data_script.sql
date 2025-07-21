-- Script per inserimento dati organigramma da JSON
-- Disabilita temporaneamente i trigger per performance
PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- Inserimento FUNCTIONS
INSERT INTO functions (name, reports_to, flags) VALUES
('Assemblea dei Soci', NULL, 'TOP_LEVEL'),
('CDA', 'Assemblea dei Soci', 'GOVERNANCE'),
('AD', 'CDA', 'EXECUTIVE'),
('SINDACO', 'Assemblea dei Soci', 'CONTROL'),
('ODV', 'CDA', 'COMPLIANCE'),
('INTERNAL AUDITING', 'CDA', 'AUDIT'),
('DATA PROTECTION OFFICE', 'AD', 'PRIVACY'),
('SEGRETERIA DI DIREZIONE', 'CDA', 'SUPPORT'),
('CORPORATE COMMUNICATION & MEDIA RELATIONS', 'CDA', 'COMMUNICATION'),
('COMMERCIAL', 'CDA', 'SALES'),
('SEGRETERIA SOCIETARIA', 'AD', 'LEGAL'),
('OPERATIONS', 'AD', 'OPERATIONS'),
('ARRANGEMENT', 'AD', 'CONSULTING'),
('COMPLIANCE', 'AD', 'COMPLIANCE'),
('EVALUATION', 'AD', 'ANALYSIS'),
('PRODUCT DESIGN & DELIVERY', 'AD', 'PRODUCT'),
('AMMINISTRAZIONE, FINANZA & CONTROLLO', 'AD', 'FINANCE'),
('HUMAN RESOURCES', 'AD', 'HR'),
('IT & SECURITY', 'AD', 'TECHNOLOGY');

-- Inserimento FUNCTION ALIASES
INSERT INTO function_aliases (function_name, alias, flags) VALUES
('CDA', 'Consiglio di Amministrazione', 'OFFICIAL'),
('AD', 'Amministratore Delegato', 'OFFICIAL'),
('ODV', 'Organo di Vigilanza', 'OFFICIAL'),
('AMMINISTRAZIONE, FINANZA & CONTROLLO', 'AFC', 'ABBREV');

-- Inserimento JOB TITLES con livelli gerarchici
INSERT INTO job_titles (name, level, flags) VALUES
('President', 1, 'C_LEVEL'),
('CEO', 1, 'C_LEVEL'),
('Associate', 2, 'BOARD'),
('Member', 3, 'BOARD'),
('DPO', 3, 'SPECIALIST'),
('IA', 3, 'SPECIALIST'),
('CIO', 1, 'C_LEVEL'),
('CTO', 1, 'C_LEVEL'),
('CIO/CTO', 1, 'C_LEVEL'),
('CFO', 1, 'C_LEVEL'),
('CISO', 2, 'SECURITY'),
('CCO', 1, 'C_LEVEL'),
('CPO', 1, 'C_LEVEL'),
('Head of Corporate Communication & Media Relations', 2, 'MANAGER'),
('Head of Marketing', 2, 'MANAGER'),
('Media Relations Manager', 3, 'MANAGER'),
('Sales Strategy & Partnership Director', 2, 'DIRECTOR'),
('Head of Planning & Analysis', 2, 'MANAGER'),
('Head of Direct Sales', 2, 'MANAGER'),
('Head of Indirect Sales', 2, 'MANAGER'),
('Key Account Manager', 3, 'MANAGER'),
('Digital Marketing Specialist', 4, 'SPECIALIST'),
('Head of Tender & Sales Support', 2, 'MANAGER'),
('Head of Operations', 2, 'MANAGER'),
('Service & Offering Management Manager', 3, 'MANAGER'),
('Tender Specialist', 4, 'SPECIALIST'),
('Staff', 4, 'SUPPORT'),
('Technical Coordination Manager', 3, 'MANAGER'),
('Technical Coordinator', 4, 'COORDINATOR'),
('Head of ARRANGEMENT', 2, 'MANAGER'),
('Project Manager', 3, 'MANAGER'),
('Senior Consultant', 4, 'CONSULTANT'),
('Consultant', 5, 'CONSULTANT'),
('Analyst', 5, 'ANALYST');

-- Inserimento JOB TITLE ALIASES
INSERT INTO job_title_aliases (job_title_name, alias, flags) VALUES
('President', 'Presidente', 'IT'),
('President', 'Presidente CdA', 'IT_FULL'),
('CEO', 'Chief Executive Officer', 'EN_FULL'),
('CEO', 'AD', 'IT_ABBREV'),
('CEO', 'Amministratore Delegato', 'IT_FULL'),
('Associate', 'Socio', 'IT'),
('Member', 'Membro', 'IT'),
('DPO', 'Data Protection Officer', 'EN_FULL'),
('IA', 'Internal Auditor', 'EN_FULL'),
('CIO', 'Chief Information Officer', 'EN_FULL'),
('CTO', 'Chief Technology Officer', 'EN_FULL'),
('CIO/CTO', 'Chief Information & Technology Officer', 'EN_FULL'),
('CFO', 'Chief Financial Officer', 'EN_FULL'),
('CISO', 'Chief Information Security Officer', 'EN_FULL'),
('CCO', 'Chief Commercial Officer', 'EN_FULL'),
('CPO', 'Chief Product Officer', 'EN_FULL');

-- Inserimento PERSONS
INSERT INTO persons (name, employee_id, status, flags) VALUES
('Gianluca Calvosa', 'EMP001', 'ACTIVE', 'PRESIDENT'),
('Raffaele Nardone', 'EMP002', 'ACTIVE', 'CEO'),
('Francesco Becchelli', 'EMP003', 'ACTIVE', 'BOARD'),
('F. Orioli', 'EMP004', 'ACTIVE', 'SINDACO'),
('C. Padovani', 'EMP005', 'ACTIVE', 'ODV'),
('FINDATA', 'EXT001', 'ACTIVE', 'EXTERNAL'),
('Benedetto Verdino', 'EMP006', 'ACTIVE', 'AUDITOR'),
('Martina Casani', 'EMP007', 'ACTIVE', 'MULTI_ROLE'),
('Andrea Zanini', 'EMP008', 'ACTIVE', 'COMM'),
('Giovanni Uboldi', 'EMP009', 'ACTIVE', 'MULTI_ROLE'),
('Giovanni Arrigoni', 'EMP010', 'ACTIVE', 'MULTI_ROLE'),
('Vera Moretti', 'EMP011', 'ACTIVE', 'SALES'),
('Luca Barbon', 'EMP012', 'ACTIVE', 'SALES'),
('Federico Chiarello', 'EMP013', 'ACTIVE', 'SALES'),
('Mattia Petrongari', 'EMP014', 'ACTIVE', 'SALES'),
('Margherita Nobiloni', 'EMP015', 'ACTIVE', 'MARKETING'),
('Luca Minotti', 'EMP016', 'ACTIVE', 'MULTI_ROLE'),
('Giovanna Crupi', 'EMP017', 'ACTIVE', 'TENDER'),
('Alfredo Scermino', 'EMP018', 'ACTIVE', 'SUPPORT'),
('Chiara D''Orazi', 'EMP019', 'ACTIVE', 'TECH'),
('Noemi Giaconi', 'EMP020', 'ACTIVE', 'TECH'),
('Filippo La Rosa', 'EMP021', 'ACTIVE', 'TECH'),
('Alberto Di Loreto', 'EMP022', 'ACTIVE', 'ARRANGEMENT'),
('Eva Fazio', 'EMP023', 'ACTIVE', 'PM'),
('Jacopo Ales', 'EMP024', 'ACTIVE', 'PM'),
('Antonio Maisto', 'EMP025', 'ACTIVE', 'PM'),
('Michele Marino', 'EMP026', 'ACTIVE', 'CONSULTANT'),
('Giuseppe Gambino', 'EMP027', 'ACTIVE', 'CONSULTANT'),
('Arianna Grispigni', 'EMP028', 'ACTIVE', 'CONSULTANT'),
('Roberta Tiseo', 'EMP029', 'ACTIVE', 'CONSULTANT'),
('Sofiya Rinci', 'EMP030', 'ACTIVE', 'CONSULTANT'),
('Francesco Montanari', 'EMP031', 'ACTIVE', 'CONSULTANT'),
('Alessandra Leoncini', 'EMP032', 'ACTIVE', 'ANALYST'),
('Alessio Paoloni', 'EMP033', 'ACTIVE', 'ANALYST');

-- Inserimento PERSON ALIASES
INSERT INTO person_aliases (person_name, alias, flags) VALUES
('Gianluca Calvosa', 'CALVOSA G.', 'SHORT'),
('Gianluca Calvosa', 'Calvosa', 'SURNAME'),
('Raffaele Nardone', 'NARDONE R.', 'SHORT'),
('Francesco Becchelli', 'BECCHELLI F.', 'SHORT'),
('F. Orioli', 'ORIOLI F.', 'SHORT'),
('C. Padovani', 'PADOVANI C.', 'SHORT'),
('FINDATA', 'FINDATA Srl', 'COMPANY'),
('Benedetto Verdino', 'VERDINO B.', 'SHORT'),
('Martina Casani', 'CASANI M.', 'SHORT'),
('Andrea Zanini', 'ZANINI A.', 'SHORT'),
('Giovanni Uboldi', 'UBOLDI G.', 'SHORT'),
('Giovanni Arrigoni', 'ARRIGONI G.', 'SHORT'),
('Vera Moretti', 'MORETTI V.', 'SHORT'),
('Luca Barbon', 'BARBON L.', 'SHORT'),
('Federico Chiarello', 'CHIARELLO F.', 'SHORT'),
('Mattia Petrongari', 'PETRONGARI M.', 'SHORT'),
('Margherita Nobiloni', 'NOBILONI M.', 'SHORT'),
('Luca Minotti', 'MINOTTI L.', 'SHORT'),
('Giovanna Crupi', 'CRUPI G.', 'SHORT'),
('Alfredo Scermino', 'SCERMINO A.', 'SHORT'),
('Chiara D''Orazi', 'D''ORAZI C.', 'SHORT'),
('Noemi Giaconi', 'GIACONI N.', 'SHORT'),
('Filippo La Rosa', 'LA ROSA F.', 'SHORT'),
('Alberto Di Loreto', 'DI LORETO A.', 'SHORT'),
('Eva Fazio', 'FAZIO E.', 'SHORT'),
('Jacopo Ales', 'ALES J.', 'SHORT'),
('Antonio Maisto', 'MAISTO A.', 'SHORT'),
('Michele Marino', 'MARINO M.', 'SHORT'),
('Giuseppe Gambino', 'GAMBINO G.', 'SHORT'),
('Arianna Grispigni', 'GRISPIGNI A.', 'SHORT'),
('Roberta Tiseo', 'TISEO R.', 'SHORT'),
('Sofiya Rinci', 'RINCI S.', 'SHORT'),
('Francesco Montanari', 'MONTANARI F.', 'SHORT'),
('Alessandra Leoncini', 'LEONCINI A.', 'SHORT'),
('Alessio Paoloni', 'PAOLONI A.', 'SHORT');

-- Inserimento ROLES - Parte 1: Governance e Top Management
INSERT INTO roles (person_name, function_name, organizational_unit, job_title_name, percentage, ad_interim, reports_to, flags) VALUES
('Gianluca Calvosa', 'CDA', '', 'President', 1.0, 0, NULL, 'BOARD_ROLE'),
('Raffaele Nardone', 'AD', '', 'CEO', 1.0, 0, NULL, 'EXEC_ROLE'),
('Raffaele Nardone', 'CDA', '', 'Member', 1.0, 0, NULL, 'BOARD_ROLE'),
('Francesco Becchelli', 'CDA', '', 'Associate', 1.0, 0, NULL, 'BOARD_ROLE'),
('F. Orioli', 'SINDACO', '', 'Member', 1.0, 0, NULL, 'CONTROL_ROLE'),
('C. Padovani', 'ODV', '', 'Member', 1.0, 0, NULL, 'COMPLIANCE_ROLE'),
('FINDATA', 'DATA PROTECTION OFFICE', '', 'DPO', 1.0, 0, NULL, 'EXTERNAL'),
('Benedetto Verdino', 'INTERNAL AUDITING', '', 'IA', 1.0, 0, NULL, 'AUDIT_ROLE');

-- Inserimento ROLES - Parte 2: Communication & Marketing
INSERT INTO roles (person_name, function_name, organizational_unit, job_title_name, percentage, ad_interim, reports_to, flags) VALUES
('Martina Casani', 'CORPORATE COMMUNICATION & MEDIA RELATIONS', '', 'Head of Corporate Communication & Media Relations', 1.0, 1, NULL, 'INTERIM'),
('Martina Casani', 'COMMERCIAL', 'Marketing', 'Head of Marketing', 1.0, 0, NULL, 'MARKETING'),
('Andrea Zanini', 'CORPORATE COMMUNICATION & MEDIA RELATIONS', '', 'Media Relations Manager', 1.0, 0, 'Martina Casani', 'COMM'),
('Margherita Nobiloni', 'COMMERCIAL', 'Marketing', 'Digital Marketing Specialist', 1.0, 0, 'Martina Casani', 'DIGITAL');

-- Inserimento ROLES - Parte 3: Commercial
INSERT INTO roles (person_name, function_name, organizational_unit, job_title_name, percentage, ad_interim, reports_to, flags) VALUES
('Giovanni Uboldi', 'COMMERCIAL', '', 'CCO', 1.0, 0, 'Gianluca Calvosa', 'C_LEVEL'),
('Giovanni Uboldi', 'COMMERCIAL', 'Planning & Analysis', 'Head of Planning & Analysis', 1.0, 0, 'Gianluca Calvosa', 'ANALYSIS'),
('Giovanni Uboldi', 'COMMERCIAL', 'Direct Sales', 'Head of Direct Sales', 1.0, 1, 'Gianluca Calvosa', 'INTERIM_SALES'),
('Giovanni Arrigoni', 'COMMERCIAL', '', 'Sales Strategy & Partnership Director', 1.0, 0, 'Giovanni Uboldi', 'STRATEGY'),
('Giovanni Arrigoni', 'COMMERCIAL', 'Indirect Sales', 'Head of Indirect Sales', 1.0, 1, 'Giovanni Uboldi', 'INTERIM_SALES'),
('Vera Moretti', 'COMMERCIAL', 'Direct Sales', 'Key Account Manager', 1.0, 0, 'Giovanni Uboldi', 'KAM'),
('Luca Barbon', 'COMMERCIAL', 'Direct Sales', 'Key Account Manager', 1.0, 0, 'Giovanni Uboldi', 'KAM'),
('Federico Chiarello', 'COMMERCIAL', 'Direct Sales', 'Key Account Manager', 1.0, 0, 'Giovanni Uboldi', 'KAM'),
('Mattia Petrongari', 'COMMERCIAL', 'Direct Sales', 'Key Account Manager', 1.0, 0, 'Giovanni Uboldi', 'KAM'),
('Luca Minotti', 'COMMERCIAL', 'Tender & Sales Support', 'Head of Tender & Sales Support', 1.0, 1, 'Giovanni Uboldi', 'INTERIM_TENDER'),
('Giovanna Crupi', 'COMMERCIAL', 'Tender & Sales Support', 'Tender Specialist', 1.0, 1, 'Luca Minotti', 'INTERIM_SPEC');

-- Inserimento ROLES - Parte 4: Operations & Support
INSERT INTO roles (person_name, function_name, organizational_unit, job_title_name, percentage, ad_interim, reports_to, flags) VALUES
('Alfredo Scermino', 'SEGRETERIA SOCIETARIA', '', 'Staff', 1.0, 1, 'Raffaele Nardone', 'INTERIM_SUPPORT'),
('Luca Minotti', 'OPERATIONS', '', 'Head of Operations', 1.0, 0, 'Raffaele Nardone', 'OPERATIONS'),
('Luca Minotti', 'OPERATIONS', 'Service & Offering Management', 'Service & Offering Management Manager', 1.0, 1, 'Raffaele Nardone', 'INTERIM_SERVICE'),
('Chiara D''Orazi', 'OPERATIONS', 'Technical Coordination', 'Technical Coordination Manager', 1.0, 0, 'Luca Minotti', 'TECH_COORD'),
('Noemi Giaconi', 'OPERATIONS', 'Technical Coordination', 'Technical Coordinator', 1.0, 0, 'Luca Minotti', 'TECH_COORD'),
('Filippo La Rosa', 'OPERATIONS', 'Technical Coordination', 'Technical Coordinator', 1.0, 0, 'Luca Minotti', 'TECH_COORD');

-- Inserimento ROLES - Parte 5: Arrangement Team
INSERT INTO roles (person_name, function_name, organizational_unit, job_title_name, percentage, ad_interim, reports_to, flags) VALUES
('Alberto Di Loreto', 'ARRANGEMENT', '', 'Head of ARRANGEMENT', 1.0, 0, 'Raffaele Nardone', 'CONSULTING'),
('Eva Fazio', 'ARRANGEMENT', '', 'Project Manager', 1.0, 0, 'Alberto Di Loreto', 'PM'),
('Jacopo Ales', 'ARRANGEMENT', '', 'Project Manager', 1.0, 0, 'Alberto Di Loreto', 'PM'),
('Antonio Maisto', 'ARRANGEMENT', '', 'Project Manager', 1.0, 0, 'Alberto Di Loreto', 'PM'),
('Michele Marino', 'ARRANGEMENT', '', 'Senior Consultant', 1.0, 0, 'Alberto Di Loreto', 'SR_CONSULTANT'),
('Giuseppe Gambino', 'ARRANGEMENT', '', 'Senior Consultant', 1.0, 0, 'Alberto Di Loreto', 'SR_CONSULTANT'),
('Arianna Grispigni', 'ARRANGEMENT', '', 'Consultant', 1.0, 0, 'Alberto Di Loreto', 'CONSULTANT'),
('Roberta Tiseo', 'ARRANGEMENT', '', 'Consultant', 1.0, 0, 'Alberto Di Loreto', 'CONSULTANT'),
('Sofiya Rinci', 'ARRANGEMENT', '', 'Consultant', 1.0, 0, 'Alberto Di Loreto', 'CONSULTANT'),
('Francesco Montanari', 'ARRANGEMENT', '', 'Consultant', 1.0, 0, 'Alberto Di Loreto', 'CONSULTANT'),
('Alessandra Leoncini', 'ARRANGEMENT', '', 'Analyst', 1.0, 0, 'Alberto Di Loreto', 'ANALYST'),
('Alessio Paoloni', 'ARRANGEMENT', '', 'Analyst', 1.0, 0, 'Alberto Di Loreto', 'ANALYST');

COMMIT;

-- Riabilita foreign keys
PRAGMA foreign_keys = ON;

-- Aggiorna statistiche per ottimizzazione query
ANALYZE;

-- Query di verifica dati inseriti
SELECT 'Functions' as table_name, COUNT(*) as count FROM functions
UNION ALL
SELECT 'Function Aliases', COUNT(*) FROM function_aliases
UNION ALL
SELECT 'Job Titles', COUNT(*) FROM job_titles
UNION ALL
SELECT 'Job Title Aliases', COUNT(*) FROM job_title_aliases
UNION ALL
SELECT 'Persons', COUNT(*) FROM persons
UNION ALL
SELECT 'Person Aliases', COUNT(*) FROM person_aliases
UNION ALL
SELECT 'Roles', COUNT(*) FROM roles;

-- Query di controllo integrità
SELECT 'Roles senza persona' as check_type, COUNT(*) as issues
FROM roles r LEFT JOIN persons p ON r.person_name = p.name WHERE p.name IS NULL
UNION ALL
SELECT 'Roles senza funzione', COUNT(*)
FROM roles r LEFT JOIN functions f ON r.function_name = f.name WHERE f.name IS NULL
UNION ALL
SELECT 'Reports_to inesistenti', COUNT(*)
FROM roles r LEFT JOIN persons p ON r.reports_to = p.name 
WHERE r.reports_to IS NOT NULL AND r.reports_to != '' AND p.name IS NULL;