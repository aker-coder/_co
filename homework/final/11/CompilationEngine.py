from SymbolTable import SymbolTable
from VMWriter import VMWriter 
# 假設你的 Tokenizer 方法是 camelCase (tokenType, keyWord...)

class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        # VMWriter 直接使用傳入的檔案物件
        self.vm_writer = VMWriter(output_file)
        self.symbol_table = SymbolTable()
        
        # 紀錄 Class Name (用於產生 function 名稱: ClassName.methodName)
        self.class_name = "" 
        
        self.label_count = 0

        # 初始化：先讀取第一個 Token
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    # --- 移除所有 _write_tag, _process, _write_end_tag 函式 ---
    # 第11章不需要輸出 XML，保留它們只會導致 outfile error

    # --- 編譯邏輯 ---

    def compileClass(self):
        # 1. 'class'
        self.tokenizer.advance() 
        
        # 2. className
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        # 3. '{'
        self.tokenizer.advance()

        # 4. ClassVarDec
        while self.tokenizer.tokenType() == 'KEYWORD' and \
              self.tokenizer.keyWord() in ['STATIC', 'FIELD']:
            self.compileClassVarDec()

        # 5. Subroutine
        while self.tokenizer.tokenType() == 'KEYWORD' and \
              self.tokenizer.keyWord() in ['CONSTRUCTOR', 'FUNCTION', 'METHOD']:
            self.compileSubroutine()

        # 6. '}'
        self.tokenizer.advance()

    def compileClassVarDec(self):
        # 結構: static/field type name, name;
        kind = self.tokenizer.keyWord() # static / field
        self.tokenizer.advance()
        
        type = self._getCurrentType() # 取得 int, boolean 或 class name
        self.tokenizer.advance()
        
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, kind.upper()) # 加入符號表
        self.tokenizer.advance()
        
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self.tokenizer.advance() # ,
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, kind.upper())
            self.tokenizer.advance()
            
        self.tokenizer.advance() # ;

    def compileSubroutine(self):
        # 1. 重置 Subroutine 符號表
        self.symbol_table.start_subroutine()
        
        func_type = self.tokenizer.keyWord() # constructor, function, method
        self.tokenizer.advance()
        
        self.tokenizer.advance() # void or return type
        
        func_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        self.tokenizer.advance() # (
        self.compileParameterList()
        self.tokenizer.advance() # )
        
        # --- Subroutine Body ---
        self.tokenizer.advance() # {
        
        # 先編譯變數宣告 (VarDec)
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord() == 'VAR':
            self.compileVarDec()
            
        # 計算 local 變數數量
        n_locals = self.symbol_table.var_count('VAR')
        
        # 寫入 VM function 指令
        full_func_name = f"{self.class_name}.{func_name}"
        self.vm_writer.write_function(full_func_name, n_locals)
        
        # === 處理 Method 和 Constructor 的特殊記憶體操作 ===
        if func_type == 'METHOD':
            # Method 的第一個參數是 this，需要對齊
            self.vm_writer.write_push('ARG', 0)
            self.vm_writer.write_pop('POINTER', 0) # this = argument 0
            
        elif func_type == 'CONSTRUCTOR':
            # Constructor 需要分配記憶體
            n_fields = self.symbol_table.var_count('FIELD')
            self.vm_writer.write_push('CONST', n_fields)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('POINTER', 0) # this = Memory.alloc(size)

        self.compileStatements()
        
        self.tokenizer.advance() # }

    def compileParameterList(self):
        # 參數列表不需產生 VM code，只需加入 Symbol Table
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')':
            return

        type = self._getCurrentType()
        self.tokenizer.advance()
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, 'ARG')
        self.tokenizer.advance()
        
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self.tokenizer.advance()
            type = self._getCurrentType()
            self.tokenizer.advance()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, 'ARG')
            self.tokenizer.advance()

    def compileVarDec(self):
        self.tokenizer.advance() # var
        type = self._getCurrentType()
        self.tokenizer.advance()
        
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, 'VAR')
        self.tokenizer.advance()
        
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self.tokenizer.advance()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, 'VAR')
            self.tokenizer.advance()
            
        self.tokenizer.advance() # ;

    def compileStatements(self):
        while self.tokenizer.tokenType() == 'KEYWORD':
            kw = self.tokenizer.keyWord()
            if kw == 'LET': self.compileLet()
            elif kw == 'IF': self.compileIf()
            elif kw == 'WHILE': self.compileWhile()
            elif kw == 'DO': self.compileDo()
            elif kw == 'RETURN': self.compileReturn()
            else: break

    def compileLet(self):
        # 結構: let varName ([ expression ])? = expression ;
        
        self.tokenizer.advance() # let
        var_name = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        isArray = False
        
        # 判斷是否為陣列賦值
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '[':
            isArray = True
            
            # 1. Push 陣列基底
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            segment = self._kind_to_segment(kind)
            self.vm_writer.write_push(segment, index)
            
            # 2. 計算索引
            self.tokenizer.advance() # [
            self.compileExpression()
            self.tokenizer.advance() # ]
            
            # 3. 相加得到目標位址 (現在 Stack 頂端是 Address)
            self.vm_writer.write_arithmetic('ADD')
            
        self.tokenizer.advance() # =
        
        # 4. 計算右邊的值 (結果會在 Stack 頂端)
        self.compileExpression()
        
        self.tokenizer.advance() # ;
        
        if isArray:
            # --- 陣列賦值邏輯 ---
            # Stack 狀態: [..., Address, Value] (Value 在頂端)
            
            self.vm_writer.write_pop('TEMP', 0)     # 暫存 Value -> Stack: [..., Address]
            self.vm_writer.write_pop('POINTER', 1)  # 設定 THAT -> Stack: [...]
            self.vm_writer.write_push('TEMP', 0)    # 取回 Value -> Stack: [..., Value]
            self.vm_writer.write_pop('THAT', 0)     # 寫入 arr[i]
            
        else:
            # --- 普通變數賦值 ---
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            segment = self._kind_to_segment(kind)
            if segment:
                self.vm_writer.write_pop(segment, index)

    def compileExpression(self):
        # 結構: term (op term)*
        self.compileTerm()
        
        ops = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() in ops:
            op = self.tokenizer.symbol() # 記住運算子
            self.tokenizer.advance()
            
            self.compileTerm() # 編譯右邊的 term
            
            # Postfix: 左右都 push 完後，才輸出運算指令
            self._write_op(op)

    def compileTerm(self):
        type = self.tokenizer.tokenType()
        
        if type == 'INT_CONST':
            self.vm_writer.write_push('CONST', self.tokenizer.intVal())
            self.tokenizer.advance()
            
        elif type == 'STRING_CONST':
            # --- [新增] 字串處理 ---
            s = self.tokenizer.stringVal()
            self.vm_writer.write_push('CONST', len(s))
            self.vm_writer.write_call('String.new', 1)
            for char in s:
                self.vm_writer.write_push('CONST', ord(char))
                self.vm_writer.write_call('String.appendChar', 2)
            self.tokenizer.advance()
            
        elif type == 'KEYWORD':
            kw = self.tokenizer.keyWord()
            if kw == 'TRUE':
                self.vm_writer.write_push('CONST', 0)
                self.vm_writer.write_arithmetic('NOT')
            elif kw == 'FALSE' or kw == 'NULL':
                self.vm_writer.write_push('CONST', 0)
            elif kw == 'THIS':
                self.vm_writer.write_push('POINTER', 0)
            self.tokenizer.advance()

        elif type == 'IDENTIFIER':
            name = self.tokenizer.identifier()
            self.tokenizer.advance()
            
            # --- [修改] 判斷是 陣列存取 / 函式呼叫 / 普通變數 ---
            
            if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '[':
                # 情況 A: 陣列存取 arr[i]
                
                # 1. Push 陣列基底位址
                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index)
                
                # 2. 計算索引 expression
                self.tokenizer.advance() # [
                self.compileExpression() # 計算索引 i
                self.tokenizer.advance() # ]
                
                # 3. 基底 + 索引 = 目標位址
                self.vm_writer.write_arithmetic('ADD')
                
                # 4. 設定 THAT 指標指向目標位址
                self.vm_writer.write_pop('POINTER', 1) # pointer 1 = that
                
                # 5. 取出值
                self.vm_writer.write_push('THAT', 0)
                
            elif self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() in ['(', '.']:
                # 情況 B: 函式呼叫 foo() 或 obj.method()
                self._compileSubroutineCall(name)
            else:
                # 情況 C: 普通變數
                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index)
                
        elif type == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.tokenizer.advance()
            self.compileExpression()
            self.tokenizer.advance()
            
        elif type == 'SYMBOL' and self.tokenizer.symbol() in ['-', '~']:
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compileTerm()
            if op == '-': self.vm_writer.write_arithmetic('NEG')
            if op == '~': self.vm_writer.write_arithmetic('NOT')

    def compileDo(self):
        self.tokenizer.advance() # do
        name = self.tokenizer.identifier()
        self.tokenizer.advance()
        self._compileSubroutineCall(name)
        self.tokenizer.advance() # ;
        # Do 語句不回傳值，但 VM stack 會有回傳值(0)，必須 pop 掉
        self.vm_writer.write_pop('TEMP', 0)

    def compileReturn(self):
        self.tokenizer.advance() # return
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.vm_writer.write_push('CONST', 0) # Void returns 0
        else:
            self.compileExpression()
        self.tokenizer.advance() # ;
        self.vm_writer.write_return()

    # --- Helpers ---
    def _new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def _compileSubroutineCall(self, first_name):
        # 處理 functionName() 或 ClassName.func() 或 var.method()
        n_args = 0
        
        if self.tokenizer.symbol() == '.':
            self.tokenizer.advance() # .
            method_name = self.tokenizer.identifier()
            self.tokenizer.advance() # method name
            
            # 檢查 first_name 是類別名還是變數名
            kind = self.symbol_table.kind_of(first_name)
            if kind: # 它是變數 (例如 ball.move()) -> 這是 Method
                index = self.symbol_table.index_of(first_name)
                segment = self._kind_to_segment(kind)
                self.vm_writer.write_push(segment, index) # push 物件 reference
                func_name = f"{self.symbol_table.type_of(first_name)}.{method_name}"
                n_args = 1 # 物件本身算一個參數
            else: # 它是類別 (例如 Output.printInt()) -> 這是 Function
                func_name = f"{first_name}.{method_name}"
                
        elif self.tokenizer.symbol() == '(': # method() -> 隱含 this.method()
            func_name = f"{self.class_name}.{first_name}"
            self.vm_writer.write_push('POINTER', 0) # push this
            n_args = 1

        self.tokenizer.advance() # (
        n_args += self.compileExpressionList()
        self.tokenizer.advance() # )
        
        self.vm_writer.write_call(func_name, n_args)

    def compileExpressionList(self):
        count = 0
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')':
            return 0
            
        self.compileExpression()
        count += 1
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self.tokenizer.advance()
            self.compileExpression()
            count += 1
        return count

    def compileIf(self):
        # 這裡需要 Labelling 邏輯，你需要自己實作 unique label generator
        pass 
    
    def compileWhile(self):
        # 同上
        pass

    def _kind_to_segment(self, kind):
        if kind == 'FIELD': return 'THIS'
        if kind == 'STATIC': return 'STATIC'
        if kind == 'VAR': return 'LOCAL'
        if kind == 'ARG': return 'ARG'
        return None
        
    def _getCurrentType(self):
        # 輔助：回傳目前的型別字串，不管是 int, char 還是 class name
        if self.tokenizer.tokenType() == 'KEYWORD':
            return self.tokenizer.keyWord().lower() # int, boolean...
        return self.tokenizer.identifier()
        
    def _write_op(self, op):
        if op == '+': self.vm_writer.write_arithmetic('ADD')
        elif op == '-': self.vm_writer.write_arithmetic('SUB')
        elif op == '*': self.vm_writer.write_call('Math.multiply', 2)
        elif op == '/': self.vm_writer.write_call('Math.divide', 2)
        elif op == '&': self.vm_writer.write_arithmetic('AND')
        elif op == '|': self.vm_writer.write_arithmetic('OR')
        elif op == '<': self.vm_writer.write_arithmetic('LT')
        elif op == '>': self.vm_writer.write_arithmetic('GT')
        elif op == '=': self.vm_writer.write_arithmetic('EQ')

    def compileIf(self):
        # 結構: if (expression) { statements } (else { statements })?
        
        self.tokenizer.advance() # 吃掉 'if'
        self.tokenizer.advance() # 吃掉 '('
        
        self.compileExpression() # 計算條件，結果 push 到堆疊頂端
        
        self.tokenizer.advance() # 吃掉 ')'
        self.tokenizer.advance() # 吃掉 '{'
        
        L1 = self._new_label() # 用來標記 Else 開始 (或 If 結束)
        L2 = self._new_label() # 用來標記整個 If 語句結束
        
        # VM 邏輯：條件取反 -> 如果不成立，跳去 L1
        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(L1)
        
        # 編譯 If 內部的語句
        self.compileStatements()
        
        self.tokenizer.advance() # 吃掉 '}'
        
        # If 執行完後，無條件跳到 L2 (避開 Else)
        self.vm_writer.write_goto(L2)
        
        # 標記 L1 (Else 的進入點)
        self.vm_writer.write_label(L1)
        
        # 檢查有沒有 Else
        if self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord() == 'ELSE':
            self.tokenizer.advance() # 吃掉 'else'
            self.tokenizer.advance() # 吃掉 '{'
            self.compileStatements()
            self.tokenizer.advance() # 吃掉 '}'
            
        # 標記 L2 (結束點)
        self.vm_writer.write_label(L2)
    
    def compileWhile(self):
        # 結構: while (expression) { statements }
        
        L1 = self._new_label() # 迴圈頂端 (Top)
        L2 = self._new_label() # 迴圈出口 (End)
        
        # 1. 標記迴圈開始
        self.vm_writer.write_label(L1)
        
        self.tokenizer.advance() # 吃掉 'while'
        self.tokenizer.advance() # 吃掉 '('
        
        # 2. 計算條件
        self.compileExpression()
        
        self.tokenizer.advance() # 吃掉 ')'
        self.tokenizer.advance() # 吃掉 '{'
        
        # 3. 條件判斷：如果不成立 (NOT True)，跳出迴圈 (去 L2)
        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(L2)
        
        # 4. 執行迴圈內容
        self.compileStatements()
        
        self.tokenizer.advance() # 吃掉 '}'
        
        # 5. 跳回開頭 (Loop)
        self.vm_writer.write_goto(L1)
        
        # 6. 標記迴圈結束
        self.vm_writer.write_label(L2)