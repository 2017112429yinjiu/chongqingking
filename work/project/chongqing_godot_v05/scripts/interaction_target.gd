extends Node3D
## One stable interaction identity. UI and world objects share this contract.
var interaction_id: String = ""
var radius: float = 2.5
var prompt: Callable
var enabled: Callable
var action: Callable

func available() -> bool:
	return enabled.is_valid() and bool(enabled.call())

func label() -> String:
	return str(prompt.call()) if prompt.is_valid() else "交互"

func execute() -> void:
	if available() and action.is_valid():
		action.call()
