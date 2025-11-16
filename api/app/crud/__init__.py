# CRUD modules - functions are exported at module level
# Import like: from app.crud import server as crud_server
# Then use: crud_server.get_servers(...)

# Import all CRUD modules to make them available
from app.crud import (
    user,
    server,
    alert,
    api_key,
    metric,
    log_entry,
    command_history,
    connection_event,
    audit_log,
)
