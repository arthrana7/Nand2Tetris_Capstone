"""
Hack assembler: .asm -> .hack
Usage: python assembler.py Prog.asm

K = 5
Extra feature: Print a warning for duplicate labels
with their original line numbers.
"""

import sys

# Binary codes for Hack Assembly computations
COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101', '!A': '0110001',
    '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
    'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
}

# Generate M-based computation codes from A-based codes
for k, v in list(COMP.items()):
    if 'A' in k:
        COMP[k.replace('A', 'M')] = '1' + v[1:]

# Add alternative computation expressions
for a, b in [('A+D', 'D+A'), ('M+D', 'D+M'), ('A&D', 'D&A'),
             ('M&D', 'D&M'), ('A|D', 'D|A'), ('M|D', 'D|M')]:
    COMP[a] = COMP[b]

# Binary codes for jump instructions
JUMP = {
    '': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'
}

# Predefined Hack computer symbols and their memory addresses
SYMBOLS = {
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576
}

# Define R0 to R15 register symbols
for i in range(16):
    SYMBOLS['R' + str(i)] = i


def dest_bits(d):
    """Convert destination into A, D, M binary bits."""
    return ('1' if 'A' in d else '0') + \
           ('1' if 'D' in d else '0') + \
           ('1' if 'M' in d else '0')


def clean(line):
    """Remove comments and all whitespace from a line."""
    line = line.split('//')[0]
    return ''.join(line.split())


def assemble(lines):
    """Convert Hack Assembly instructions into binary machine code."""

    symbols = dict(SYMBOLS)
    program = []
    line_numbers = []
    label_lines = {}

    # First pass: Identify labels and store their ROM addresses
    for lineno, raw in enumerate(lines, start=1):
        line = clean(raw)

        if not line:
            continue

        if line.startswith('(') and line.endswith(')'):
            name = line[1:-1]

            # Check for invalid labels
            if not name:
                raise ValueError(f"Line {lineno}: invalid label")

            # Check for duplicate labels
            if name in label_lines:
                print(
                    f"Warning: line {lineno}: label '{name}' "
                    f"already defined on line {label_lines[name]}"
                )
                continue

            # Prevent redefining predefined symbols
            if name in symbols:
                raise ValueError(
                    f"Line {lineno}: label conflicts with predefined symbol"
                )

            # Store label and its original line number
            symbols[name] = len(program)
            label_lines[name] = lineno

        else:
            program.append(line)
            line_numbers.append(lineno)

    # Second pass: Convert instructions into 16-bit binary
    output = []
    next_var = 16

    for line, lineno in zip(program, line_numbers):
        try:
            # A-instruction: Starts with @
            if line.startswith('@'):
                value = line[1:]

                if not value:
                    raise ValueError("invalid A-instruction")

                # Check whether the value is numeric
                if value.isdigit():
                    n = int(value)
                else:
                    # Assign RAM addresses to new variables
                    if value not in symbols:
                        symbols[value] = next_var
                        next_var += 1

                    n = symbols[value]

                if n < 0 or n > 32767:
                    raise ValueError("address out of range")

                # Convert address into 16-bit binary
                output.append(format(n, '016b'))

            else:
                # C-instruction: Separate dest, comp and jump
                dest, jump = '', ''
                comp = line

                if '=' in comp:
                    dest, comp = comp.split('=', 1)

                if ';' in comp:
                    comp, jump = comp.split(';', 1)

                # Validate computation instruction
                if comp not in COMP:
                    raise ValueError("invalid computation")

                # Validate jump instruction
                if jump not in JUMP:
                    raise ValueError("invalid jump")

                # Validate destination instruction
                if any(c not in 'ADM' for c in dest) or len(set(dest)) != len(dest):
                    raise ValueError("invalid destination")

                # Generate final 16-bit C-instruction
                output.append(
                    '111' + COMP[comp] + dest_bits(dest) + JUMP[jump]
                )

        except (ValueError, KeyError) as e:
            # K = 5, print error with original line number
            raise ValueError(f"Line {lineno}: {e}") from e

    return output


def main():
    # Check command-line arguments
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.asm'):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)

    path = sys.argv[1]

    try:
        # Read the assembly file
        with open(path) as f:
            lines = f.read().splitlines()

        # Assemble the program
        result = assemble(lines)

        # Generate output .hack filename
        out_path = path[:-4] + '.hack'

        # Write binary instructions into the output file
        with open(out_path, 'w') as f:
            f.write('\n'.join(result) + '\n')

        print(f"Wrote {len(result)} instructions to {out_path}")

    except (ValueError, OSError) as e:
        # Display clear error message instead of crashing
        print(e)
        sys.exit(1)


# Execute main function when this file runs directly
if __name__ == '__main__':
    main()