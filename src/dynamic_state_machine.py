from transitions import Machine
import importlib
from utils import load_config
from machine_system import MachineSystem

class DynamicStateMachine:
    def __init__(self):
        self.config = load_config()
        self.simulation_mode = self.config['simulation']['enabled']
        
        states = self.config['states']
        self.machine_system = MachineSystem(self.simulation_mode)
        transitions = self._create_transitions()

        self.machine = Machine(model=self.machine_system, states=states, transitions=transitions, initial='init')

    def _create_transitions(self):
        transitions = []
        for transition in self.config['transitions']:
            method_name = self.config['methods'].get(f"on_enter_{transition['dest']}")
            method = self._load_method(method_name) if method_name else None
            transitions.append({
                'trigger': transition['trigger'],
                'source': transition['source'],
                'dest': transition['dest'],
                'before': method
            })
        return transitions

    def _load_method(self, method_name):
        if not method_name:
            return None
        if hasattr(self.machine_system, method_name):
            return getattr(self.machine_system, method_name)
        else:
            print(f"Warning: Method {method_name} not found in MachineSystem")
            return None

    async def list_commands(self, writer):
        commands = self.config['transitions']
        for command in commands:
            writer.write(f"{command['trigger']}: Transition from {command['source']} to {command['dest']}\r\n".encode())
        await writer.drain()
