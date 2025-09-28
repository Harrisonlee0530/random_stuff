"""
Code written by Steven Yu
"""
from typing import Dict, List

BF_COMMANDS = set("+-<>[].,")


def text_to_brainfuck(text: str) -> str:
    """
    Generate a compact Brainfuck program that prints `text`.
    Strategy: keep one data cell as the current ASCII value and only emit
    +/- deltas between consecutive characters; print with '.' each step.
    This is short and robust (no loops), though not the absolute shortest.
    """
    code = []
    curr = 0  # current cell value we maintain
    for ch in text:
        target = ord(ch)
        delta = target - curr
        if delta > 0:
            code.append("+" * delta)
        elif delta < 0:
            code.append("-" * (-delta))
        code.append(".")
        curr = target
    return "".join(code)


def brainfuck_to_hex(bf_code: str) -> str:
    """Encode Brainfuck source (ASCII) to lowercase hexadecimal string."""
    return bf_code.encode("ascii").hex()


def hex_to_brainfuck(hex_str: str) -> str:
    """Decode a lowercase/uppercase hex string to ASCII Brainfuck source."""
    return bytes.fromhex(hex_str).decode("ascii")


def run_brainfuck(code: str, inp: str = "") -> str:
    """
    Minimal Brainfuck interpreter (8 commands).
    - Ignores non-BF characters (so comments are fine).
    - Tape is unbounded to the right; cells are 0..255 with wraparound.
    - Input is optional (`,` reads from `inp`, empty => 0).
    Returns the output string produced by '.' commands.
    """
    # Precompute bracket jumps
    jumps: Dict[int, int] = {}
    stack: List[int] = []
    filtered = [c for c in code if c in BF_COMMANDS]
    for i, c in enumerate(filtered):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if not stack:
                raise ValueError(f"Unmatched ']' at position {i}")
            j = stack.pop()
            jumps[i] = j
            jumps[j] = i
    if stack:
        raise ValueError(f"Unmatched '[' at position {stack[-1]}")

    tape = [0]
    ptr = 0
    pc = 0
    out_chars: List[str] = []
    in_buf = list(inp.encode("latin1"))  # raw bytes; BF is byte-oriented

    while pc < len(filtered):
        c = filtered[pc]
        if c == ">":
            ptr += 1
            if ptr == len(tape):
                tape.append(0)
        elif c == "<":
            if ptr == 0:
                # extend tape to the left by inserting at head
                tape.insert(0, 0)
            else:
                ptr -= 1
        elif c == "+":
            tape[ptr] = (tape[ptr] + 1) & 0xFF
        elif c == "-":
            tape[ptr] = (tape[ptr] - 1) & 0xFF
        elif c == ".":
            out_chars.append(chr(tape[ptr]))
        elif c == ",":
            tape[ptr] = in_buf.pop(0) if in_buf else 0
        elif c == "[":
            if tape[ptr] == 0:
                pc = jumps[pc]
        elif c == "]":
            if tape[ptr] != 0:
                pc = jumps[pc]
        pc += 1

    return "".join(out_chars)


def encode_to_hex(text: str) -> str:
    """Convenience: text -> brainfuck -> hex."""
    bf = text_to_brainfuck(text)
    return brainfuck_to_hex(bf)


def decode_from_hex(hex_str: str) -> str:
    """Convenience: hex -> brainfuck -> text."""
    bf = hex_to_brainfuck(hex_str)
    return run_brainfuck(bf)
