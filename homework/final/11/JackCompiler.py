import sys
import os
# 假設你的模組分別存成這些檔案
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def compile_file(input_filename):
    """編譯單一 .jack 檔案"""
    output_filename = input_filename.replace('.jack', '.vm')
    
    print(f"Compiling: {input_filename} -> {output_filename}")
    
    # 1. 建立 Tokenizer (讀取輸入)
    tokenizer = JackTokenizer(input_filename)
    
    # 2. 準備輸出檔案 (寫入 .vm)
    with open(output_filename, 'w') as output_file:
        # 3. 建立 CompilationEngine (核心邏輯)
        # 注意：你需要修改 CompilationEngine 讓它接受 output_file 或直接接受 VMWriter
        engine = CompilationEngine(tokenizer, output_file)
        
        # 4. 開始編譯 Class (這是入口點)
        engine.compileClass()

def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py <file.jack or directory>")
        return

    path = sys.argv[1]

    # 情況 A: 使用者輸入的是資料夾 (例如: python JackCompiler.py ./Seven)
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".jack"):
                full_path = os.path.join(path, filename)
                compile_file(full_path)
                
    # 情況 B: 使用者輸入的是單一檔案 (例如: python JackCompiler.py Main.jack)
    elif os.path.isfile(path) and path.endswith(".jack"):
        compile_file(path)
        
    else:
        print("Invalid file or directory.")

if __name__ == "__main__":
    main()