## 🐛 錯誤與修正紀錄 (Bug Fixes & Troubleshooting)

### 1. `KeyError: 'pointer'` 錯誤
**狀況描述**：
執行轉譯時，程式崩潰並顯示 `KeyError: 'pointer'`。

**錯誤原因**：
在 `CodeWriter.py` 中，試圖使用 `seg_map` 字典來查找 `pointer`、`temp` 或 `static` 的基底位址。但這些記憶體區段沒有單一的基底指標 (如 LCL/ARG)，因此字典中不存在對應的 Key。

**✅ 修正後 (解決方案)**：
在 `writePushPop` 加入條件判斷，針對特殊區段分流處理。

```python
if segment == "pointer":
    label = "THIS" if index == 0 else "THAT"
    # 生成 pointer 專屬組合語言
elif segment == "temp":
    # 生成 temp (RAM[5]+i) 專屬組合語言
elif segment == "static":
    # 生成 static (FileName.i) 專屬組合語言
else:
    # 其他標準區段才使用通用函式
    self._write_pop_to_segment(segment, index)
```
### 2. 組合語言變直式 (Vertical Formatting)

```Plaintext

@
S
P
...
```
**錯誤原因**： CodeWriter 使用 Python 的 f-string (多行字串) 傳遞指令，但 _write_asm 函式使用 for cmd in commands 迴圈遍歷。Python 會將字串視為字元陣列逐一讀取。

**✅ 修正後 (解決方案)**： 修改 _write_asm 輔助函式，增加型別檢查。
```python
def _write_asm(self, commands):
    # 如果傳入的是單一字串，先依換行切割成列表
    if isinstance(commands, str):
        commands = commands.strip().split('\n')
    
    for cmd in commands:
        if cmd.strip():
            self.output_file.write(cmd.strip() + '\n')
```

### 3. 指令消失 (Missing Instructions)
**狀況描述**： 輸出的 .asm 檔只有註解（例如 // 1 argument 1），但下方沒有對應的組合語言指令。

**錯誤原因**： Parser 傳入的 command 是整數代號 (1 代表 push)，但 CodeWriter 內部是用字串 (if command == "push") 進行判斷，導致邏輯跳過。
**✅ 修正後 (解決方案)**： 在 writePushPop 開頭統一指令格式。
```python
cmd_str = ""
# 兼容整數代號與字串
if command == 1 or command == "push":
    cmd_str = "push"
elif command == 2 or command == "pop":
    cmd_str = "pop"

# 後續邏輯使用 cmd_str
if cmd_str == "push":
    # ... 執行 push 邏輯
```
### 4. Bootstrap Code 導致測試失敗
**狀況描述**： 在執行 FibonacciSeries 或 BasicLoop 測試時，程式進入無窮迴圈或計算錯誤。

**錯誤原因**： 這些單元測試腳本 (.tst) 會手動設定記憶體環境 (如 ARG 指標)。若轉譯器強制寫入 Sys.init 的啟動程式碼 (@256, D=A... call Sys.init)，會覆蓋掉測試腳本的設定，導致環境錯亂。

**✅ 修正後 (解決方案)**： 在 VMTranslator.py 設置開關，針對不同測試情境決定是否寫入啟動碼。

```python
# 針對 SimpleFunction, BasicLoop, FibonacciSeries -> 關閉 (註解掉)
# code_writer.writeInit()

# 針對 NestedCall, FibonacciElement, StaticsTest -> 開啟
code_writer.writeInit()
```

