import asyncio
import random
from utils import load_config

class MachineSystem:
    def __init__(self, simulation_mode=False):
        self.current_state = 'init'
        self.init_progress = 0
        self.simulation_mode = simulation_mode
        self.config = load_config()
        self.connected_clients = set()
        self.is_homed = False
        self.current_position = 0
        self.max_position = 860

    async def process_input(self, message):
        message = message.strip().upper()
        
        if self.current_state == 'init':
            return "System is still initializing. Please wait."
        
        if message == '?':
            return self.get_available_commands()
        elif message == 'HOM':
            self.is_homed = False  # Reset homing status
            return await self.home()
        elif message == 'SCAN':
            return await self.scan()
        elif message.startswith('MTP'):
            return await self.move_to_pod(message)
        elif message.startswith('MOVR'):
            return await self.move_relative(message)
        elif message.startswith('MOVA'):
            return await self.move_absolute(message)
        elif message == 'STAT':
            return "STAT command not implemented yet."
        elif message == 'CAL':
            return "CAL command not implemented yet."
        else:
            return f"Unknown command: {message}"

    def get_available_commands(self):
        return "Available commands: ?, HOM, SCAN, MTP, MOVR, MOVA, STAT, CAL"

    async def home(self):
        if self.simulation_mode:
            await asyncio.sleep(self.config['operations']['home']['duration'])
            if random.random() < 0.95:
                self.is_homed = True
                self.current_position = 0
                self.current_state = 'standby'
                return "H:0"
            else:
                self.current_state = 'fault'
                return "E:1"
        else:
            # Implement real homing logic here
            pass

    async def scan(self):
        if not self.is_homed:
            return "E:1 Machine not homed"
        
        if self.simulation_mode:
            await asyncio.sleep(self.config['operations']['scan']['duration'])
            if random.random() < 0.95:
                wafer_status = ['1' for _ in range(100)]
                # Introduce 0 or 2 with a 5% chance for each position
                for i in range(100):
                    if random.random() < 0.05:
                        wafer_status[i] = random.choice(['0', '2'])
                return f"A[{''.join(wafer_status)}]"
            else:
                return f"E:{random.choice([0, 2])}"
        else:
            # Implement real scanning logic here
            pass

    async def move_to_pod(self, message):
        try:
            pod = int(message.split()[1])
            if pod not in [1, 2, 3, 4]:
                return "E:0 Invalid pod number"
            
            if not self.is_homed:
                return "E:1 Machine not homed"
            
            target_position = (pod - 1) * 215
            return await self._move_to_position(target_position)
        except IndexError:
            return "E:0 Missing pod number"
        except ValueError:
            return "E:0 Invalid pod number format"

    async def move_relative(self, message):
        try:
            distance = int(message.split()[1])
            if not self.is_homed:
                return "E:1 Machine not homed"
            
            target_position = self.current_position + distance
            return await self._move_to_position(target_position)
        except IndexError:
            return "E:0 Missing distance"
        except ValueError:
            return "E:0 Invalid distance format"

    async def move_absolute(self, message):
        try:
            position = int(message.split()[1])
            if not self.is_homed:
                return "E:1 Machine not homed"
            
            return await self._move_to_position(position)
        except IndexError:
            return "E:0 Missing position"
        except ValueError:
            return "E:0 Invalid position format"

    async def _move_to_position(self, target_position):
        if target_position < 0 or target_position > self.max_position:
            return f"E:0 Position out of range (0-{self.max_position}mm)"
        
        if self.simulation_mode:
            await asyncio.sleep(abs(target_position - self.current_position) / 100)  # Simulate movement time
            self.current_position = target_position
            return f"T:0 Position: {self.current_position}mm"
        else:
            # Implement real movement logic here
            pass

    async def on_enter_init(self):
        self.current_state = 'init'
        print("Entering init state")
        await self.init_tasks()

    async def on_enter_home(self):
        self.current_state = 'home'
        print("Entering home state")

    async def on_enter_scan(self):
        self.current_state = 'scan'
        print("Entering scan state")

    async def on_enter_fault(self):
        self.current_state = 'fault'
        print("Entering fault state")

    async def on_enter_standby(self):
        self.current_state = 'standby'
        print("Entering standby state")

    async def init_tasks(self):
        total_time = self.config['initialization']['total_time']
        status_message = "System is initializing, please wait..."
        await self.broadcast_message(f"\r\n{status_message}\r\n")

        for i in range(total_time):
            self.init_progress = (i + 1) / total_time * 100
            status_bar = f"[{'#' * (i + 1)}{' ' * (total_time - i - 1)}] {self.init_progress:.2f}%"
            await self.broadcast_message(f"\r{status_bar}")
            await asyncio.sleep(1)

        self.init_progress = 100
        await self.broadcast_message("\r\nInitialization complete.\r\n")
        self.current_state = 'standby'

    async def broadcast_message(self, message):
        if not self.connected_clients:
            print(f"No clients connected. Message: {message.strip()}")
            return
        for writer in self.connected_clients:
            try:
                writer.write(message.encode())
                await writer.drain()
            except Exception as e:
                print(f"Error broadcasting to a client: {e}")
                self.connected_clients.remove(writer)

    async def perform_real_scan_operation(self):
        # TODO: Implement real scan operation using pyads to communicate with TwinCAT IPC/PLC
        return "Real scan operation not implemented yet"

    async def perform_real_home_operation(self):
        """Perform a real home operation using TwinCAT IPC/PLC."""
        # TODO: Implement real home operation using pyads to communicate with TwinCAT IPC/PLC
        pass
