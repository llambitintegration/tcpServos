import asyncio
from utils import load_config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host, port, handler):
        self.host = host
        self.port = port
        self.handler = handler

    async def start(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

async def tcp_handler(reader, writer, machine_system):
    addr = writer.get_extra_info('peername')
    machine_system.connected_clients.add(writer)
    print(f"New client connected: {addr}")
    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            
            message = data.decode().strip()
            logger.info(f"Received {message!r} from {addr!r}")
            print(f"Received from {addr}: {message}")

            if message.lower() == "!clients":
                client_info = f"Connected clients: {len(machine_system.connected_clients)}"
                response = client_info
            else:
                try:
                    response = await machine_system.process_input(message)
                except Exception as e:
                    logger.error(f"Error processing input: {str(e)}", exc_info=True)
                    response = f"E:1 Internal server error"
            
            if response:
                logger.info(f"Sending to {addr}: {response!r}")
                print(f"Sending to {addr}: {response}")
                writer.write(response.encode() + b'\r\n')
                await writer.drain()
            else:
                logger.warning(f"Empty response for input: {message!r}")

    except Exception as e:
        logger.error(f"Error in tcp_handler for {addr}: {str(e)}", exc_info=True)
    finally:
        machine_system.connected_clients.remove(writer)
        print(f"Client disconnected: {addr}")
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing writer for {addr}: {str(e)}", exc_info=True)
                
async def send_current_status(writer, system):
    try:
        if system.current_state == 'init':
            writer.write("System is currently initializing...\r\n".encode())
            progress_bar = f"[{'#' * int(system.init_progress // 6.67)}{' ' * (15 - int(system.init_progress // 6.67))}] {system.init_progress:.2f}%"
            writer.write(f"\r{progress_bar}\r\n".encode())
        else:
            writer.write(f"Current State: {system.current_state}\r\n".encode())
        await writer.drain()
    except Exception as e:
        print(f"Failed to send current status to the client: {e}")

async def send_error(writer, message):
    try:
        await writer.write(f"Error: {message}\r\n".encode())
        await writer.drain()
    except Exception as e:
        print(f"Failed to send error message to the client: {e}")
