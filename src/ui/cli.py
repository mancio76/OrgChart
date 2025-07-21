import click
import uvicorn
import signal
import sys
import os
import subprocess

@click.group()
def cli():
    """Organigramma Manager CLI"""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host address')
@click.option('--port', default=8000, help='Port number')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--debug', is_flag=True, help='Debug mode')
def start(host, port, reload, debug):
    """Avvia il server web"""
    click.echo(f"🚀 Avvio Organigramma Manager su http://{host}:{port}")
    
    config = {
        'host': host,
        'port': port,
        'reload': reload,
        'log_level': 'debug' if debug else 'info'
    }
    
    try:
        uvicorn.run("src.ui.app:app", **config)
    except KeyboardInterrupt:
        click.echo("\n✅ Server arrestato")

@cli.command()
def stop():
    """Arresta il server (cerca processi uvicorn)"""
    try:
        result = subprocess.run(['pkill', '-f', 'uvicorn.*organigramma'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("✅ Server arrestato")
        else:
            click.echo("❌ Nessun server trovato in esecuzione")
    except FileNotFoundError:
        click.echo("❌ Comando pkill non disponibile su questo sistema")

@cli.command()
@click.option('--check-db', is_flag=True, help='Verifica database')
def status(check_db):
    """Stato dell'applicazione"""
    click.echo("📊 Stato Organigramma Manager")
    
    # Verifica database
    if check_db:
        try:
            from src.database.connection import DatabaseConnection
            from src.database.repository import OrganigrammaRepository
            
            db = DatabaseConnection()
            repo = OrganigrammaRepository(db)
            stats = repo.get_stats()
            
            click.echo("✅ Database connesso:")
            for key, value in stats.items():
                click.echo(f"   {key}: {value}")
                
        except Exception as e:
            click.echo(f"❌ Errore database: {e}")
    
    # Verifica se server è attivo
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/stats", timeout=2)
        if response.status_code == 200:
            click.echo("✅ Server web attivo")
        else:
            click.echo("❌ Server web non risponde")
    except:
        click.echo("❌ Server web non attivo")

if __name__ == "__main__":
    cli()