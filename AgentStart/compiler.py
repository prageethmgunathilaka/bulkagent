"""
Compiler for AgentStart language.
Takes .as files and compiles them to executable Python.
"""

import os
import sys
from parser import AgentStartParser

def compile_file(input_file, output_file=None):
    """Compile an AgentStart file to Python"""
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".py"
        
    parser = AgentStartParser()
    result = parser.compile(input_file, output_file)
    
    print(f"Compiled {input_file} to {result}")
    return result

def run_file(input_file):
    """Compile and run an AgentStart file"""
    py_file = compile_file(input_file)
    
    # Execute the compiled Python file
    exec(open(py_file).read())
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input_file> [--run]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if "--run" in sys.argv:
        run_file(input_file)
    else:
        compile_file(input_file) 