# In-memory state store for multi-step flows
# Format: { user_id: { "step": str, "data": dict } }

_states: dict = {}


def set_state(user_id: int, step: str, data: dict = {}):
    _states[user_id] = {"step": step, "data": dict(data)}


def get_state(user_id: int) -> dict | None:
    return _states.get(user_id)


def update_data(user_id: int, key: str, value):
    if user_id in _states:
        _states[user_id]["data"][key] = value


def clear_state(user_id: int):
    _states.pop(user_id, None)
