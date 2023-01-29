
from app.util.log import logger

from .base import Agent
from .agents import RelayAgent, PwmAgent


def create_agent_from_json(json) -> Agent:
    type = json['type']
    if type == 'relay':
        return RelayAgent(
            json['name'],
            type,
            json['failsafe'],
            json['gpio'],
        )
    elif type == 'pwm':
        return PwmAgent(
            json['name'],
            type,
            json['failsafe'],
            json['gpio']['write'],
            json['gpio']['control'],
        )
    else:
        raise NotImplementedError(f'Invalid agent-type: {type}')
