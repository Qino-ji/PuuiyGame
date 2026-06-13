import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler.interpreter import execute_file, InterpreterError
from compiler.lexer import LexerError
from compiler.parser import ParseError


def main():
    if len(sys.argv) < 2:
        print("Puuiy Language Runtime v0.1")
        print("usage: python puuiy.py <file.piy>")
        print("       python puuiy.py -e \"<code>\"")
        sys.exit(1)

    if sys.argv[1] == "-e":
        code = " ".join(sys.argv[2:])
        try:
            from compiler.interpreter import execute
            execute(code)
        except LexerError as e:
            print(f"[lexer] {e}")
            sys.exit(1)
        except ParseError as e:
            print(f"[parser] {e}")
            sys.exit(1)
        except InterpreterError as e:
            print(f"[runtime] {e}")
            sys.exit(1)
        return

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"file not found: {filepath}")
        sys.exit(1)

    try:
        execute_file(filepath)
    except LexerError as e:
        print(f"[lexer] {e}")
        sys.exit(1)
    except ParseError as e:
        print(f"[parser] {e}")
        sys.exit(1)
    except InterpreterError as e:
        print(f"[runtime] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()