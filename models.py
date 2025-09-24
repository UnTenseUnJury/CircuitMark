# models.py

class Node:
    """Represents a connection point (or net) in the circuit."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Node({self.name})"


class Component:
    def __init__(self, component_type: str, name: str, primary_value: str = None):
        self.component_type = component_type
        self.name = name
        self.primary_value = primary_value
        self.properties = {}
        self.connections = {}

    def add_property(self, key: str, value: str):
        self.properties[key] = value

    def add_connection(self, pin_name: str, node: 'Node'):
        self.connections[pin_name] = node

    def __repr__(self) -> str:
        return (f"{self.component_type.capitalize()}({self.name}, "
                f"value={self.primary_value}, props={self.properties}, "
                f"conns={self.connections})")


class SubcircuitDefinition:
    def __init__(self, name: str):
        self.name = name
        self.interface = []
        self.body_text = ""

    def __repr__(self) -> str:
        return f"SubcircuitDef({self.name}, pins={self.interface})"


class Circuit:
    """The main container for the entire circuit netlist."""
    def __init__(self):
        self.components = {}
        self.nodes = {}
        self.subcircuit_definitions = {}
        self.ground_node_name = None

    def add_component(self, component: Component):
        if component.name in self.components:
            raise ValueError(f"Component name '{component.name}' already exists.")
        self.components[component.name] = component

    # --- NODE HANDLING ---
    def declare_node(self, node_name: str):
        """Adds a new, declared node to the circuit."""
        if node_name in self.nodes:
            raise ValueError(f"Node '{node_name}' has already been declared.")
        self.nodes[node_name] = Node(node_name)

    def set_ground_node(self, node_name: str):
        """Designates one of the nodes as ground.
        Automatically declares the node if it hasn’t been declared yet (original behaviour)."""
        if self.ground_node_name:
            raise ValueError("Ground node has already been set.")
        if node_name not in self.nodes:
            self.declare_node(node_name)  # auto-declare ground node
        self.ground_node_name = node_name

    def get_node(self, node_name: str) -> Node:
        """Retrieves a previously declared node."""
        if node_name not in self.nodes:
            raise ValueError(f"Undeclared node '{node_name}'. All nodes must be declared before use.")
        return self.nodes[node_name]

    def __repr__(self) -> str:
        return (f"Circuit(components={list(self.components.keys())}, "
                f"nodes={list(self.nodes.keys())}, ground='{self.ground_node_name}')")
