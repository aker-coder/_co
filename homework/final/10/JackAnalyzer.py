import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def analyze_file(input_file):
    output_file = input_file.replace('.jack', '.xml')
    print(f"Compiling {input_file} -> {output_file}")
    
    tokenizer = JackTokenizer(input_file)
    engine = CompilationEngine(tokenizer, output_file)
    engine.compileClass()
    engine.close()

if __name__ == "__main__":
    target = sys.argv[1]
    if os.path.isdir(target):
        for filename in os.listdir(target):
            if filename.endswith(".jack"):
                analyze_file(os.path.join(target, filename))
    else:
        analyze_file(target)