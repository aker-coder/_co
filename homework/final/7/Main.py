import sys
# 假設你的檔案分別命名為 Parser.py 和 CodeWriter.py
from Parser import Parser, C_ARITHMETIC, C_PUSH, C_POP
from CodeWriter import CodeWriter

def main():
    if len(sys.argv) != 2:
        print("Usage: python Main.py <file.vm>")
        return

    input_file = sys.argv[1]
    # 產生的輸出檔名：把 .vm 換成 .asm
    output_file = input_file.replace(".vm", ".asm")

    # 1. 初始化
    parser = Parser(input_file)
    writer = CodeWriter(output_file)
    
    # 設定 CodeWriter 的檔名 (處理 static 變數用)
    # 這裡簡單處理，只取檔名部分 (去除路徑和副檔名)
    file_name_only = input_file.split('/')[-1].split('\\')[-1].replace(".vm", "")
    writer.set_file_name(file_name_only)

    print(f"Translating {input_file} -> {output_file} ...")

    # 2. 迴圈處理每一行指令
    while parser.has_more_commands():
        parser.advance()
        ctype = parser.command_type()

        if ctype == C_ARITHMETIC:
            # 處理算術指令 (add, sub, eq...)
            # arg1() 會回傳指令本身，如 "add"
            writer.write_arithmetic(parser.arg1())

        elif ctype == C_PUSH or ctype == C_POP:
            # 處理 push/pop
            command = "push" if ctype == C_PUSH else "pop"
            segment = parser.arg1()
            index = parser.arg2()
            writer.write_push_pop(command, segment, index)

        # 第 8 章的指令先留空，等第 7 章測試通過再來加
        # elif ctype == C_LABEL: ...
        
    # 3. 關閉檔案
    writer.close()
    print("Done!")

if __name__ == "__main__":
    main()