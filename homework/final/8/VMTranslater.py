import sys
import os
from Parser import Parser, C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL
from CodeWriter import CodeWriter

def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <input path>")
        return

    input_path = sys.argv[1]
    vm_files = []
    output_file = ""

    # 判斷輸入是檔案還是目錄
    if os.path.isdir(input_path):
        # 如果是目錄，找出所有 .vm 檔
        input_path = input_path.rstrip("/")
        dir_name = os.path.basename(input_path)
        output_file = os.path.join(input_path, dir_name + ".asm")
        
        for file in os.listdir(input_path):
            if file.endswith(".vm"):
                vm_files.append(os.path.join(input_path, file))
    else:
        # 如果是單一檔案
        output_file = input_path.replace(".vm", ".asm")
        vm_files.append(input_path)

    code_writer = CodeWriter(output_file)
    
    # 【關鍵】如果是目錄處理，通常需要加入 Bootstrap code
    # 如果你正在測試 SimpleFunction (不需要 bootstrap)，可以先把這行註解掉
    # if os.path.isdir(input_path):
    #     code_writer.writeInit()

    for vm_file in vm_files:
        parser = Parser(vm_file)
        # 通知 CodeWriter 現在正在處理哪個檔 (為了 Static 變數命名)
        file_name_only = os.path.basename(vm_file).replace(".vm", "")
        code_writer.setFileName(file_name_only)

        while parser.hasMoreLines():
            parser.advance()
            ctype = parser.commandType()
            
            if ctype == C_ARITHMETIC:
                code_writer.writeArithmetic(parser.arg1())
            elif ctype in [C_PUSH, C_POP]:
                code_writer.writePushPop(ctype, parser.arg1(), parser.arg2())
            elif ctype == C_LABEL:
                code_writer.writeLabel(parser.arg1())
            elif ctype == C_GOTO:
                code_writer.writeGoto(parser.arg1())
            elif ctype == C_IF:
                code_writer.writeIf(parser.arg1())
            elif ctype == C_FUNCTION:
                code_writer.writeFunction(parser.arg1(), parser.arg2())
            elif ctype == C_RETURN:
                code_writer.writeReturn()
            elif ctype == C_CALL:
                code_writer.writeCall(parser.arg1(), parser.arg2())

    code_writer.close()
    print(f"Successfully generated: {output_file}")

if __name__ == "__main__":
    main()