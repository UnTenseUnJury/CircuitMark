from parser import Parser

with open("main.cml","r+") as cd:
    circuit_definition = cd.read()


def main():
    """Parses the circuit definition and prints the result."""
    print("\n--- Running CircuitMark Parser (v0.1) ---")
    parser = Parser()

    try:
        # Attempt to parse the circuit definition
        circuit = parser.parse(circuit_definition)

        # If successful, print the results
        print("\n Parse Successful!")
        print("\n--- Parsed Circuit Object ---")
        print(circuit)
        print("\n--- Components ---")
        for name, comp in circuit.components.items():
            print(f"  - {comp}")

    except Exception as e:
        print(f"Parse Failed!")
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
