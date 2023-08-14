from .base import Agent
from .agents import RelayAgent, PwmAgent, RfdAgent


def create_agent_from_json(json) -> Agent:
    type = json["type"]
    if type == "relay":
        return RelayAgent(
            json["name"],
            type,
            json["failsafe"],
            json["gpio"],
        )
    elif type == "pwm":
        return PwmAgent(
            json["name"],
            type,
            json["failsafe"],
            json["gpio"]["write"],
            json["gpio"]["control"],
        )
    elif type == "rfd":
        return RfdAgent(
            json["name"],
            type,
            json["failsafe"],
            json["gpio"],
            json["code"]["on"],
            json["code"]["off"],
        )
    else:
        raise NotImplementedError(f"Invalid agent-type: {type}")
