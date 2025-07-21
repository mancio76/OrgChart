# OrgChart (v 1.0)

Web application per la gestione dell'organigramma aziendale con interfaccia moderna e funzionalità avanzate.

## 🚀 Caratteristiche

- **Dashboard interattiva** con statistiche in tempo reale
- **Gestione dipendenti** con ricerca avanzata
- **Organigramma visuale** multi-livello
- **Profili dettagliati** con ruoli e reporting
- **API REST** per integrazioni
- **Interfaccia responsive** mobile-friendly
- **CLI integrato** per gestione server

## 📋 Prerequisiti

- Python 3.8+
- SQLite 3
- Browser moderno

## 🛠 Installazione

1. **Clona il repository**

```bash
git clone <repository-url>
cd organigramma-manager
```

2. **Crea ambiente virtuale**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Installa dipendenze**

```bash
pip install -r requirements.txt
```

4. **Setup database**

```bash
# Crea il database con lo schema fornito
sqlite3 data/organigramma.db < schema.sql
sqlite3 data/organigramma.db < insert_data.sql
```

5. **Genera favicon**

```bash
python create_favicon.py
```

## 🚀 Avvio Applicazione

### Comandi CLI

```bash
# Avvia server (development)
python main.py start

# Avvia con debug
python main.py start --debug --reload

# Avvia su host/porta specifica
python main.py start --host 0.0.0.0 --port 8080

# Arresta server
python main.py stop

# Verifica stato
python main.py status --check-db
```

### Accesso Web

Apri il browser su: http://localhost:8000

## 📚 Struttura Progetto

```
organigramma_app/
├── src/
│   ├── database/          # Layer database
│   ├── services/          # Business logic
│   ├── web/              # Web application
│   │   ├── templates/    # Template HTML
│   │   └── static/       # CSS, JS, immagini
│   └── utils/            # Utilità
├── data/                 # Database SQLite
├── tests/                # Test automatici
├── requirements.txt      # Dipendenze Python
└── main.py              # Entry point CLI
```

## 🔧 Configurazione

### Database

Il database SQLite viene creato in `data/organigramma.db`. La struttura include:

- **functions** - Funzioni organizzative
- **persons** - Dipendenti
- **roles** - Ruoli e assegnazioni
- **job_titles** - Titoli di lavoro
- Tabelle aliases per nomi alternativi
- Audit trail automatico

### Environment Variables

Crea file `.env` per configurazioni:

```bash
DATABASE_PATH=data/organigramma.db
DEBUG=False
HOST=127.0.0.1
PORT=8000
```

## 🧪 Test

```bash
# Installa dipendenze test
pip install -e ".[dev]"

# Esegui test
pytest

# Con coverage
pytest --cov=src tests/
```

## 📊 API Endpoints

### REST API

- `GET /` - Dashboard principale
- `GET /employees` - Lista dipendenti
- `GET /employee/{name}` - Profilo dipendente
- `GET /organization` - Organigramma
- `GET /functions` - Lista funzioni
- `GET /api/search/employees?q=term` - Ricerca
- `GET /api/stats` - Statistiche JSON
- `GET /health` - Health check

## 🎨 Personalizzazione

### Stili CSS

Modifica `src/web/static/style.css` per personalizzare:

- Colori brand
- Layout responsive
- Componenti UI

### Template HTML

I template Jinja2 in `src/web/templates/` sono completamente personalizzabili.

## 🔒 Sicurezza

- Validazione input con Pydantic
- Protezione SQL injection
- Headers sicurezza HTTP
- Escape automatico template

## 📈 Performance

- Caching query frequenti
- Indici database ottimizzati
- Compressione static files
- Lazy loading componenti

## 🤝 Contributi

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 🐛 Bug Reports

Per segnalare bug o richiedere funzionalità, apri un issue su GitHub.

## ⚡ Quick Start

```bash
# Setup completo in 3 comandi
pip install -r requirements.txt
python create_favicon.py
python main.py start --debug
```

Apri http://localhost:8000 e inizia a esplorare! 🎉