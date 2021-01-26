import code
from composition_root import CommandBusContainer


variables = globals().copy()
variables.update({
  'command_bus': CommandBusContainer.command_bus_factory(),
})
shell = code.InteractiveConsole(variables)
shell.interact()
