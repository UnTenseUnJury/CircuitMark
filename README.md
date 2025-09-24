# CircuitMark

[![Version](https://img.shields.io/badge/version-v0.1-blue.svg)](https://shields.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://shields.io/)

**CircuitMark is an open-source, text-based markup language for easily defining and sharing electronic circuits.**

It offers a human-friendly alternative to graphical schematic capture tools and complex SPICE netlists. The goal is to provide a simple, approachable language for students, hobbyists, and developers.

---
## Core Idea

Instead of drawing, you write. CircuitMark parses your text description and generates a visual schematic.

**CircuitMark Code:**
```
# Voltage Divider Circuit

ground GND
node v_in, v_out

battery V1 +9V from GND to v_out
resistor R1 10k from v_in to v_out
resistor R2 5k from v_out to GND
```

**Example ASCII**
```
                       v_in
                        o
                        |
                     .--^^^^--.
                     |   R1   |
                     '--^^^^--'
                        | 10k Ohm
                        |
+9V (V1) ---------------o v_out
  |                     |
  |                  .--^^^^--.
  |                  |   R2   |
  |                  '--^^^^--'
  |                     | 5k Ohm
  |                     |
  ----------------------o GND


```


## Key Features

* **Human-Readable Syntax:** Circuits are defined line-by-line using plain words, making the format easy to learn and read.
* **Automatic Schematic Generation:** The toolchain can parse CircuitMark files and render them into clean SVG or ASCII art diagrams.
* **Hierarchical Design:** Define component blocks as subcircuits and reuse them in larger designs to manage complexity.
* **Version-Control Friendly:** Because the source is plain text, it's perfect for versioning with Git, allowing for easy collaboration and change tracking.

## Example Syntax

CircuitMark uses a flexible syntax to define components, from simple resistors to multi-pin transistors.

```
# A simple two-terminal component
resistor R1 1k tolerance=5% from v_in to v_out

# A multi-terminal component with named pins
transistor Q1 model=2N3904 base=q1_base collector=q1_collector emitter=GND
```

## Project Status

This project is currently a **v0.1 prototype**.

  * The markup language specification is defined with support for core components and strict syntax rules.
  * A Python-based parser can process `.cml` files, including hierarchical subcircuits.


## Getting Started

To use the CircuitMark parser and renderer, you will need Python 3.x installed.

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/UnTenseUnJury/CircuitMark.git
cd CircuitMark
```

### Usage

The `main.py` script is the primary entry point for the tool.

1.  Create a `main.cml` file and store your CircuitMark code in that file. (This can be renamed in `main.py`)
2.  Run the `main.py` script from your terminal:
    
    ```bash
    python main.py
    ```

The script will generate the node list of the circuit to the console.


## Contributing

This is an open-source project and contributions are welcome\! Feel free to open an issue to discuss a bug or a new feature, or submit a pull request with your improvements.


## License

This project is licensed under the MIT License.
