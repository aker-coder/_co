# Jack Compiler (Nand2Tetris Ch 10 & 11) 專案說明文件
1. 專案概述這是一個將 Jack 高階語言（類似 Java）編譯為 Hack VM 中介碼（堆疊機指令）的編譯器。這是 Nand2Tetris 課程中軟體層次最核心、也最複雜的部分。

**核心目標**：將人類可讀的 .jack 檔案，轉換為虛擬機可執行的 .vm 檔案。
2. **系統架構圖**
編譯器由五個核心模組組成，數據流向如下：

```bash 程式碼片段
graph LR
    Input[.jack File] --> A[JackTokenizer]
    A --> B[CompilationEngine]
    C[SymbolTable] <--> B
    D[VMWriter] <-- B
    D --> Output[.vm File]
```

1. **JackTokenizer**: 負責「斷詞」，把原始碼切成一個個有意義的單字（Token）。

2. **CompilationEngine**: 負責「語法分析」與「邏輯控制」，是編譯器的大腦。

3. **SymbolTable**: 負責「記憶」，記錄變數名稱、型別、種類（Scope）與記憶體位址。

4. **VMWriter**: 負責「輸出」，將邏輯轉換為標準的 VM 指令字串。

5. **JackCompiler**: 主程式，負責檔案讀寫與流程串接。

## 3. 階段演進與程式碼比較 (重要！)

這是你最需要理解的部分：我們如何從第 10 章進化到第 11 章？

**階段一**：語法分析 (Syntax Analysis - Ch 10)

* **目標**：驗證程式碼語法是否正確，並產出 XML 語法樹。

* **輸出**：`<class>`, `<keyword> class </keyword>`, `<symbol> { </symbol>`

* **邏輯**：看到什麼就吐出什麼標籤。

**階段二：代碼生成 (Code Generation - Ch 11)**

* **目標**：產出可執行的 VM 指令。

* **輸出**：push local 0, add, pop static 1

* **重大改變說明**：
**比較 1：核心驅動邏輯**
|特徵|第 10 章 (XML)|第 11 章 (VM)|
|:---|:---|:---|
|輸出工具|直接 `outfile.write('<tag>...')`|透過 `vm_writer.writePush(...)`|
|變數處理|視為純文字 `<identifier> x </identifier>`|需查表 symbol_table.indexOf('x') 取得索引|
|運算式輸|出中序 (Infix) XML|轉換為 後序 (Postfix) 指令 (`push a`, `push b`, `add`)|

**比較 2：程式碼實作差異 (以 `compileTerm` 為例)**
**第 10 章版本 (舊)**：
```Python
# 只是單純記錄結構
def compileTerm(self):
    if self.tokenizer.tokenType() == 'INT_CONST':
        # 輸出 XML 標籤
        self._write_tag("integerConstant", self.tokenizer.intVal()) 
```
**第 11 章版本 (新)**：
```Python
# 具有實際執行意義
def compileTerm(self):
    if self.tokenizer.tokenType() == 'INT_CONST':
        # 產生 VM 指令：將數字推入堆疊
        self.vm_writer.write_push('CONST', self.tokenizer.intVal())
```
**為什麼這樣改？**因為電腦看不懂 XML 標籤。VM 是一個**堆疊機器 (Stack Machine)**，它需要的是動作（Push/Pop/Add）。我們必須把「看到數字」這個語法事件，轉化為「把數字推入堆疊」這個執行動作。

## 4. 模組詳細解析
**A. SymbolTable.py (符號表)**
**功能**： 這是編譯器的記憶體。當我們寫 `let x = 1` 時，編譯器必須知道 `x` 到底是第幾個變數。

* **資料結構**：使用兩個 Hash Map (Python Dictionary)。
    * `class_table`: 存 `static` (全域共享), `field` (物件屬性)。
    
    * `subroutine_table`: 存 `arg` (參數), `var` (區域變數)。

* **關鍵邏輯**：
    * 進入新函式 (`startSubroutine`) 時，清空 `subroutine_table`。
    
    * 查表順序：先查區域變數，再查類別變數。
    
**B. VMWriter.py (VM 寫入器)**

**功能**： 封裝 VM 指令格式，避免手寫字串出錯。

* **設計模式**：Facade Pattern (外觀模式)。隱藏了 VM 語法的細節。

* **為什麼需要它？** 為了讓 `CompilationEngine` 的程式碼更乾淨。寫 `vm.writeArithmetic('ADD')` 比寫 `outfile.write('add\n')` 更具可讀性且不易出錯。

**C. CompilationEngine.py (核心引擎)**

這是最複雜的檔案，使用了 **遞迴下降分析法 (Recursive Descent Parsing)**。

**關鍵實作細節**：

1. **運算式 (Expressions)**:

    * 利用遞迴處理優先權。

    * **轉換邏輯**：Jack 是 `1 + 2`，VM 必須是 `push 1`, `push 2`, `add`。所以我們在編譯完左邊和右邊的 Term 後，才寫入 Op 指令。

2. **流程控制 (Flow Control)**:
    * **If**: 產生 `L1`, `L2` 標籤。利用 `not` + `if-goto` 實作「如果**不成立**就跳去 Else」。
    * **While**: 產生 `L1` (開頭), `L2` (結尾)。每次迴圈結束都 `goto L1`。

3. **陣列存取 (Arrays)**:

* **難點**：VM 沒有 `push array i`。

* **解法**：
    * 計算位址：`push arr` + `push i` + `add`。

    * 指標重導：`pop pointer 1` (這會讓 `that` 區段指向剛計算出的位址)。

    * 存取值：`push that 0`。
    
4. **物件導向 (Method Call)**:

* **難點**：呼叫 Method 時，需要隱式傳遞 `this`。

* **解法**：在 `compileSubroutine` 中，如果判斷是 Method 呼叫，編譯器會自動先 `push` 物件的 Reference 作為第 0 個參數。

## 5. 如何向他人解釋這份程式碼？
如果你需要報告或解釋這份作業，請使用以下三個亮點：
1. *圖靈完備 (Turing Complete)**：「這個編譯器支援了變數、迴圈 (While)、分支 (If) 和函式呼叫，這意味著它理論上可以計算任何可計算的問題。」

2. **堆疊機思維 (Stack Machine Thinking)**：「我在實作表達式編譯時，採用了後序遍歷。例如處理 `a + b`，我先生成推入 `a` 的指令，再生成推入 `b` 的指令，最後才生成 `add`，這完全符合 VM 的堆疊運作原理。」

3. **記憶體管理 (Memory Management)**：「在處理陣列 (`arr[i]`) 時，我利用了 Hack VM 的 `pointer 1` (That 指標) 來動態存取記憶體堆疊 (Heap)，這是第 11 章最困難也最精彩的實作細節。」

## 6. 檔案清單
* `JackCompiler.py`: 程式入口點。

* `JackTokenizer.py`: 正規表達式處理 Token。

* `CompilationEngine.py`: 核心編譯邏輯。

* `SymbolTable.py`: 變數管理。

* `VMWriter.py`: VM 指令輸出工具。

## 參考資料
[Gemini對話](https://gemini.google.com/share/d93da0f23a46)