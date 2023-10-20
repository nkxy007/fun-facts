from typing import Callable, List, Dict, Any
from enum import Enum, auto
from dataclasses import dataclass


class ProcesStatus(Enum):
    STARTED = auto()
    FAILED = auto()
    COMPLETED = auto()

@dataclass
class NetworkingProcess:
    status:ProcesStatus
    artefacts: Dict[Any, Any]

def order_hardware(context:dict) -> NetworkingProcess:
    pass 

def stage_hardware(context:dict) -> NetworkingProcess:
    pass 

def configure_device(context:dict) -> NetworkingProcess:
    pass

def verify_service(context:dict) -> NetworkingProcess:
    pass

def close_project(context:dict) -> NetworkingProcess:
    pass

steps: List[Callable] = [order_hardware, stage_hardware, configure_device, verify_service, close_project]

if __name__ == "__main__":
    print("Starting .....")