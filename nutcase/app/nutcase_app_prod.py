from app import create_app, cli, db
from app.models import LogEntry
from config import Config_Production

app = create_app(Config_Production)
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'LogEntry': LogEntry}
