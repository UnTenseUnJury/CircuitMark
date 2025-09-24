# parser.py - The CircuitMark Language Parser

import shlex
from models import Component, Circuit, SubcircuitDefinition

# This schema defines the valid pin names for each component type.
COMPONENT_SCHEMA = {
    'resistor': {'pins': ['from', 'to']},
    'capacitor': {'pins': ['from', 'to']},
    'inductor': {'pins': ['from', 'to']},
    'diode': {'pins': ['from', 'to']},
    'battery': {'pins': ['from', 'to']},
    'acsource': {'pins': ['from', 'to']},
    'switch': {'pins': ['from', 'to']},
}

# These are valid properties that are not connection pins.
KNOWN_PROPERTIES = ['model', 'tolerance', 'power', 'color', 'state', 'amplitude', 'frequency']


class Parser:
    """Parses CircuitMark text to create a Circuit object."""

    def parse(self, text: str) -> Circuit:
        """Parses the full text of a .circ file, including all declarations and blocks."""
        circuit = Circuit()
        lines = text.strip().split('\n')

        in_subcircuit_block = False
        current_subcircuit_name = None
        subcircuit_lines = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            try:
                # --- Subcircuit Block Handling ---
                if line.startswith('[/subcircuit]'):
                    if not in_subcircuit_block:
                        raise ValueError("Found end of block '[/subcircuit]' without a start.")
                    self._parse_subcircuit_block(current_subcircuit_name, subcircuit_lines, circuit)
                    in_subcircuit_block = False
                    current_subcircuit_name = None
                    subcircuit_lines = []
                    continue

                if line.startswith('[subcircuit'):
                    if in_subcircuit_block:
                        raise ValueError("Cannot nest subcircuits.")
                    parts = line.split(maxsplit=1)
                    if len(parts) < 2:
                        raise ValueError("Subcircuit declaration must include a name, e.g. [subcircuit NAME].")
                    in_subcircuit_block = True
                    current_subcircuit_name = parts[1].strip(' ]')
                    subcircuit_lines = []
                    continue

                if in_subcircuit_block:
                    subcircuit_lines.append(line)
                    continue

                # --- Regular Line Handling ---
                if not line or line.startswith('#'):
                    continue

                tokens = shlex.split(line)
                if not tokens:
                    continue

                command = tokens[0].lower()

                if command == 'node':
                    if len(tokens) < 2:
                        raise ValueError("'node' requires a comma-separated list of node names.")
                    node_names = " ".join(tokens[1:]).split(',')
                    for name in node_names:
                        name = name.strip()
                        if not name:
                            continue
                        circuit.declare_node(name)
                elif command == 'ground':
                    if len(tokens) != 2:
                        raise ValueError("'ground' declaration must have exactly one node name.")
                    circuit.set_ground_node(tokens[1])
                elif command in COMPONENT_SCHEMA or command in circuit.subcircuit_definitions:
                    self._parse_component_line(line, circuit)
                else:
                    raise ValueError(f"Unknown command or component type '{command}'")

            except Exception as e:
                # Add line number to any error message for easier debugging
                raise type(e)(f"On line {line_num}: {e}")

        # At EOF, ensure no unclosed subcircuit blocks remain
        if in_subcircuit_block:
            raise ValueError(f"Subcircuit '{current_subcircuit_name}' not closed with [/subcircuit].")

        return circuit

    def _parse_subcircuit_block(self, name: str, lines: list, circuit: Circuit):
        """Processes the collected lines of a subcircuit definition."""
        sub_def = SubcircuitDefinition(name)
        body_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('expose'):
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    raise ValueError("Subcircuit 'expose' line must list pins, e.g. 'expose a,b=c'.")
                pin_defs = [p.strip() for p in parts[1].split(',')]
                for pin_def in pin_defs:
                    if '=' in pin_def:
                        public_name = pin_def.split('=')[0].strip()
                        if not public_name:
                            raise ValueError("Invalid expose mapping in subcircuit.")
                        sub_def.interface.append(public_name)
                    else:
                        if not pin_def:
                            raise ValueError("Invalid expose pin name.")
                        sub_def.interface.append(pin_def)
            else:
                body_lines.append(line)

        if not sub_def.interface:
            raise ValueError(f"Subcircuit '{name}' has no 'expose' line defining its interface.")

        sub_def.body_text = "\n".join(body_lines)
        circuit.subcircuit_definitions[name] = sub_def

    def _parse_component_line(self, line: str, circuit: Circuit):
        """Parses a single line defining a component, with all validation checks."""
        tokens = shlex.split(line)
        if len(tokens) < 2:
            raise ValueError("Component line must include at least a type and a name.")

        comp_type = tokens.pop(0).lower()
        comp_name = tokens.pop(0)

        primary_value = None
        if tokens and '=' not in tokens[0] and tokens[0] not in ['from', 'to']:
            primary_value = tokens.pop(0)

        component = Component(comp_type, comp_name, primary_value)

        # Helper to require token availability
        def require_tokens(count, context_msg):
            if len(tokens) < count:
                raise ValueError(f"Malformed component '{comp_name}': {context_msg}")

        while tokens:
            token = tokens.pop(0)
            if token == 'from':
                # expect: from <node> to <node>
                require_tokens(3, "'from' must be followed by '<node> to <node>'")
                from_node_name = tokens.pop(0)
                if not from_node_name:
                    raise ValueError("'from' missing node name.")
                component.add_connection('from', circuit.get_node(from_node_name))

                next_tok = tokens.pop(0)
                if next_tok != 'to':
                    raise ValueError("'from' clause must be followed by 'to'.")
                to_node_name = tokens.pop(0)
                if not to_node_name:
                    raise ValueError("'to' missing node name.")
                component.add_connection('to', circuit.get_node(to_node_name))

            elif '=' in token:
                key, value = token.split('=', 1)
                if not key:
                    raise ValueError(f"Invalid key in token '{token}'.")
                if not value:
                    raise ValueError(f"Invalid value in token '{token}'.")
                valid_pins = COMPONENT_SCHEMA.get(comp_type, {}).get('pins', [])
                if key in valid_pins:
                    component.add_connection(key, circuit.get_node(value))
                elif key in KNOWN_PROPERTIES:
                    component.add_property(key, value)
                else:
                    raise ValueError(f"Invalid pin or property '{key}' for component type '{comp_type}'")
            else:
                raise ValueError(f"Unexpected token '{token}' in component '{comp_name}'.")

        # Shorted Component Check (robust to Node.__eq__ changes)
        con_nodes = list(component.connections.values())
        if len(con_nodes) > 1:
            unique_ids = {id(n) for n in con_nodes}
            if len(unique_ids) == 1:
                raise ValueError(f"Component '{component.name}' is shorted (all pins connect to the same node)")

        circuit.add_component(component)
