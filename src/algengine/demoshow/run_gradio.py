import os
from ..utils import (
    get_local_ip, 
    is_local_port_occupied, 
    Config
)

os.environ["NO_PROXY"] = os.environ["no_proxy"] = f"localhost, {get_local_ip()}"
# os.environ['GRADIO_EXAMPLES_CACHE'] = './examples_cache_ref'

import click


from .registries import GRADIO_SERVICES
from .configs import DEFAULT_CONFIGS


@click.command
@click.option('-n', '--name', help='Service Name')
@click.option('-c', '--config', type=str, default=None, help='Service Configuration (YAML)')
@click.option('-p', '--port', type=int, default=0, help='Service Port')
@click.option('--server_name', type=str, default=None, help='Service Name')
@click.option('-o', '--root_path', type=str, default=None, help='Root Path For Service')
def run_gradio(name: str, 
               config: str,
               port: int,
               server_name: str,
               root_path: str):
    if is_local_port_occupied(port):
        click.echo(f"Target port for service is occupied! ({port})")
        return
    
    if config is None:
        config = DEFAULT_CONFIGS[GRADIO_SERVICES.get(name).DEFAULT_CONFIG_NAME]
    else:
        config = Config.from_file(config)
    
    app = GRADIO_SERVICES.build(config, recursive=False) 
    service = app.create_service()
    
    allowed_paths = []
    if getattr(app, 'example_root', None):
        allowed_paths.append(app.example_root)
    if getattr(app, 'cache_dir', None):
        allowed_paths.append(app.cache_dir)
    service.launch(
        css=app.CSS,
        server_name=server_name if server_name is not None else get_local_ip(),
        server_port=port or None,
        root_path=root_path,
        allowed_paths=allowed_paths,
        # root_path="/style-transfer-252"
    )