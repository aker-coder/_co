class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.outfile = open(output_file, 'w')
        self.indent_level = 0
        
        # 初始化：先讀取第一個 Token
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def close(self):
        self.outfile.close()

    # --- 輔助函式 ---
    
    def _write_tag(self, tag, value, is_terminal=True):
        # 處理 XML 特殊字元
        if value in self.tokenizer.XML_ENTITY:
            value = self.tokenizer.XML_ENTITY[value]
            
        indent = "  " * self.indent_level
        if is_terminal:
            self.outfile.write(f"{indent}<{tag}> {value} </{tag}>\n")
        else:
            # 用於非終端符號 (如 <class>, <term>) 的開頭
            self.outfile.write(f"{indent}<{tag}>\n")

    def _write_end_tag(self, tag):
        indent = "  " * self.indent_level
        self.outfile.write(f"{indent}</{tag}>\n")

    def _process(self, expected_value=None):
        """
        核心輔助函式：
        1. 驗證當前 Token 是否符合預期 (若有指定)
        2. 將當前 Token 寫入 XML
        3. 推進到下一個 Token
        """
        curr_type = self.tokenizer.tokenType()
        curr_val = self.tokenizer.current_token[1]
        
        # Mapping token types to XML tags
        type_to_tag = {
            'KEYWORD': 'keyword',
            'SYMBOL': 'symbol',
            'IDENTIFIER': 'identifier',
            'INT_CONST': 'integerConstant',
            'STRING_CONST': 'stringConstant'
        }
        
        # 這裡可以加入 Error Handling
        if expected_value and curr_val != expected_value:
             print(f"Syntax Error: Expected {expected_value}, got {curr_val}")
             # raise Exception("Syntax Error")

        self._write_tag(type_to_tag[curr_type], curr_val)
        self.tokenizer.advance()

    # --- 編譯邏輯 (Recursive Descent) ---

    def compileClass(self):
        self._write_tag("class", "", is_terminal=False)
        self.indent_level += 1

        self._process("class")      # 'class'
        self._process()             # className
        self._process("{")          # '{'

        # 處理 ClassVarDec (static/field)
        while self.tokenizer.tokenType() == 'KEYWORD' and \
              self.tokenizer.keyword() in ['static', 'field']:
            self.compileClassVarDec()

        # 處理 Subroutine (constructor/function/method)
        while self.tokenizer.tokenType() == 'KEYWORD' and \
              self.tokenizer.keyword() in ['constructor', 'function', 'method']:
            self.compileSubroutine()

        self._process("}")          # '}'

        self.indent_level -= 1
        self._write_end_tag("class")

    def compileClassVarDec(self):
        self._write_tag("classVarDec", "", is_terminal=False)
        self.indent_level += 1
        
        self._process() # static | field
        self._process() # type
        self._process() # varName
        
        # 處理多個變數: , var2, var3...
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self._process(",")
            self._process() # varName
            
        self._process(";")
        
        self.indent_level -= 1
        self._write_end_tag("classVarDec")

    def compileSubroutine(self):
        self._write_tag("subroutineDec", "", is_terminal=False)
        self.indent_level += 1

        self._process() # constructor | function | method
        self._process() # void | type
        self._process() # subroutineName
        self._process("(")
        self.compileParameterList()
        self._process(")")
        
        # Subroutine Body
        self._write_tag("subroutineBody", "", is_terminal=False)
        self.indent_level += 1
        self._process("{")
        
        # varDec*
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() == 'var':
            self.compileVarDec()
            
        self.compileStatements()
        
        self._process("}")
        self.indent_level -= 1
        self._write_end_tag("subroutineBody")

        self.indent_level -= 1
        self._write_end_tag("subroutineDec")

    def compileParameterList(self):
        self._write_tag("parameterList", "", is_terminal=False)
        self.indent_level += 1
        
        # 檢查參數列表是否為空 (若下一個符號是 ')' 則為空)
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self._process() # type
            self._process() # varName
            
            while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self._process(",")
                self._process()
                self._process()
        
        self.indent_level -= 1
        self._write_end_tag("parameterList")

    def compileVarDec(self):
        self._write_tag("varDec", "", is_terminal=False)
        self.indent_level += 1
        
        self._process("var")
        self._process() # type
        self._process() # varName
        
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self._process(",")
            self._process()
            
        self._process(";")
        
        self.indent_level -= 1
        self._write_end_tag("varDec")

    def compileStatements(self):
        self._write_tag("statements", "", is_terminal=False)
        self.indent_level += 1
        
        while self.tokenizer.tokenType() == 'KEYWORD':
            kw = self.tokenizer.keyword()
            if kw == 'let': self.compileLet()
            elif kw == 'if': self.compileIf()
            elif kw == 'while': self.compileWhile()
            elif kw == 'do': self.compileDo()
            elif kw == 'return': self.compileReturn()
            else: break # 遇到不是 statement 的關鍵字 (如 '}')
        
        self.indent_level -= 1
        self._write_end_tag("statements")

    # --- 待實作區域 (請參考 compileClass 模式完成) ---
    # 將這段程式碼放入 CompilationEngine 類別中，替換原本的 placeholder

    def compileLet(self):
        # 結構: let varName ([expression])? = expression ;
        self._write_tag("letStatement", "", is_terminal=False)
        self.indent_level += 1
        
        self._process("let")
        self._process() # varName (變數名稱)
        
        # 處理陣列賦值: let a[i] = ...
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '[':
            self._process("[")
            self.compileExpression()
            self._process("]")

        self._process("=")
        self.compileExpression()
        self._process(";")
        
        self.indent_level -= 1
        self._write_end_tag("letStatement")

    def compileDo(self):
        # 結構: do subroutineCall ;
        self._write_tag("doStatement", "", is_terminal=False)
        self.indent_level += 1
        
        self._process("do")
        # 這裡直接呼叫 helper 來處理 subroutineCall (因為它跟 compileTerm 裡的邏輯長得一樣)
        self._compileSubroutineCall() 
        self._process(";")
        
        self.indent_level -= 1
        self._write_end_tag("doStatement")

    def compileIf(self):
        # 結構: if (expression) { statements } (else { statements })?
        self._write_tag("ifStatement", "", is_terminal=False)
        self.indent_level += 1
        
        self._process("if")
        self._process("(")
        self.compileExpression()
        self._process(")")
        
        self._process("{")
        self.compileStatements()
        self._process("}")
        
        # 檢查有沒有 else
        if self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() == 'else':
            self._process("else")
            self._process("{")
            self.compileStatements()
            self._process("}")
            
        self.indent_level -= 1
        self._write_end_tag("ifStatement")

    def compileWhile(self):
        # 結構: while (expression) { statements }
        self._write_tag("whileStatement", "", is_terminal=False)
        self.indent_level += 1
        
        self._process("while")
        self._process("(")
        self.compileExpression()
        self._process(")")
        self._process("{")
        self.compileStatements()
        self._process("}")
        
        self.indent_level -= 1
        self._write_end_tag("whileStatement")

    # 請替換掉原本簡陋的 compileExpression 和 compileTerm

    def compileExpression(self):
        self._write_tag("expression", "", is_terminal=False)
        self.indent_level += 1
        
        # 至少會有一個 term
        self.compileTerm()
        
        # 接著可能是 (op term)*
        # op: +, -, *, /, &, |, <, >, =
        ops = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() in ops:
            self._process() # op (運算子)
            self.compileTerm() # 下一個 term
            
        self.indent_level -= 1
        self._write_end_tag("expression")

    def compileTerm(self):
        self._write_tag("term", "", is_terminal=False)
        self.indent_level += 1
        
        tt = self.tokenizer.tokenType()
        
        if tt == 'INT_CONST':
            self._process()
        elif tt == 'STRING_CONST':
            self._process()
        elif tt == 'KEYWORD':
            # keywordConstant: true, false, null, this
            if self.tokenizer.keyword() in ['true', 'false', 'null', 'this']:
                self._process()
            else:
                # 理論上不該發生，除非語法錯誤
                pass 
                
        elif tt == 'IDENTIFIER':
            # 這是最複雜的地方：
            # 1. varName
            # 2. varName[expression]
            # 3. subroutineName(expressionList)
            # 4. className.subroutineName(expressionList)
            # 5. varName.subroutineName(expressionList)
            
            # 我們需要偷看下一個符號 (LL(2))
            next_token = self.tokenizer.peek()
            
            if next_token and next_token[1] == '[': 
                # Case 2: 陣列存取
                self._process() # varName
                self._process("[")
                self.compileExpression()
                self._process("]")
                
            elif next_token and next_token[1] in ('(', '.'):
                # Case 3, 4, 5: 函式呼叫
                # 為了邏輯統一，我們把這段拉出去處理，但因為 XML 結構要求 term 包裹它，
                # 我們不直接呼叫 compileDo 用的 helper，而是手寫這段邏輯以確保層級正確
                
                # 這裡不能呼叫 _compileSubroutineCall，因為它不會包在 <term> 裡面
                # 但邏輯是一樣的：
                self._process() # identifier (name)
                
                if self.tokenizer.symbol() == '.':
                    self._process(".")
                    self._process() # subroutineName
                
                self._process("(")
                self.compileExpressionList()
                self._process(")")
                
            else:
                # Case 1: 單純變數
                self._process()
                
        elif tt == 'SYMBOL':
            symbol = self.tokenizer.symbol()
            if symbol == '(': 
                # (expression)
                self._process("(")
                self.compileExpression()
                self._process(")")
            elif symbol in ('-', '~'): 
                # unaryOp term (負號或 NOT)
                self._process() # unaryOp
                self.compileTerm() # 遞迴呼叫 term
                
        self.indent_level -= 1
        self._write_end_tag("term")

    # [Helper] 用於 compileDo，處理函式呼叫語法
    # 因為 do 語句不需要 <term> 標籤，所以獨立出來比較乾淨
    def _compileSubroutineCall(self):
        self._process() # identifier (funcName or className/varName)
        
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '.':
            self._process(".")
            self._process() # subroutineName
            
        self._process("(")
        self.compileExpressionList()
        self._process(")")

    def compileExpressionList(self):
        self._write_tag("expressionList", "", is_terminal=False)
        self.indent_level += 1
        
        # 判斷列表是否為空：如果是 ')' 就代表結束
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self.compileExpression()
            while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self._process(",")
                self.compileExpression()
                
        self.indent_level -= 1
        self._write_end_tag("expressionList")

    def compileReturn(self):
        self._write_tag("returnStatement", "", is_terminal=False)
        self.indent_level += 1
        self._process("return")
        
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.compileExpression()
            
        self._process(";")
        self.indent_level -= 1
        self._write_end_tag("returnStatement")