import asyncio
import socket
from dynamic_state_machine import DynamicStateMachine
from server_handlers import TCPServer, tcp_handler
from utils import load_config, generate_requirements
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    config = load_config()
    dynamic_state_machine = DynamicStateMachine()
    machine_system = dynamic_state_machine.machine_system
    
    # Start the initialization process
    asyncio.create_task(machine_system.on_enter_init())
    
    # Generate requirements.txt
    generate_requirements()
    
    server_type = config['server']['type']
    port = config['server']['port']

    # Get list of IP addresses
    hostname = socket.gethostname()
    ip_addresses = socket.gethostbyname_ex(hostname)[2]
    localhost = "127.0.0.1"

    print(f"Starting {server_type.upper()} server on port {port}")
    print(f"Server is accessible at:")
    print(f"  - Localhost: {localhost}:{port}")
    for ip in ip_addresses:
        if ip != localhost:
            print(f"  - {ip}:{port}")

    if server_type == 'tcp':
        print("Raw TCP server initialized. Waiting for connections...")
        tcp_server = TCPServer('0.0.0.0', port, lambda r, w: tcp_handler(r, w, machine_system))
        try:
            await tcp_server.start()
        except Exception as e:
            logger.error(f"Error starting TCP server: {str(e)}", exc_info=True)
    else:
        raise ValueError(f"Invalid server type: {server_type}")

if __name__ == "__main__":
    print("Initializing server...")
    asyncio.run(main())