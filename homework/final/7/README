# Nand2Tetris Project 7: VM Translator (Stack Arithmetic)

## 📖 專案概述
本專案是 Nand2Tetris 課程從硬體轉向軟體的關鍵一步。目標是構建一個 **VM Translator (虛擬機轉譯器)**，能夠將中階的虛擬機語言 (VM Code) 轉譯為底層的 Hack 組合語言 (Hack Assembly)。

本章節 (Project 7) 專注於實作 **堆疊算術運算 (Stack Arithmetic)** 以及 **記憶體區段存取 (Memory Access)**，目的是建立對「堆疊機」思維模式的理解，並處理虛擬記憶體區段到實體 RAM 的映射。

## 🛠 技術與環境
* **語言**：Python 3
* **輸入**：Hack VM Code (`.vm`)
* **輸出**：Hack Assembly (`.asm`)
* **驗證**：CPUEmulator

---

## 🧠 實作細節與技術筆記 (Implementation Details)

### 1. 堆疊運算 (Arithmetic/Logical Commands)
所有的運算皆發生在堆疊頂端。轉譯器需將 VM 的堆疊操作轉換為操作 RAM 與 D 暫存器的 Assembly 指令。

#### A. 二元運算 (`add`, `sub`, `and`, `or`)
* **邏輯流程**：`pop y` $\rightarrow$ `pop x` $\rightarrow$ `x op y` $\rightarrow$ `push result`
* **Hack Assembly 技巧**：
    為了效率，不需要真的將兩個數都 pop 到暫存變數。
    1. `SP--`：將 SP 減 1，指向 `y`。
    2. `D = *SP`：讀取 `y` 到 D 暫存器。
    3. `SP--`：再將 SP 減 1，指向 `x`。
    4. `M = M op D`：直接用 `x` (M) 與 `y` (D) 運算，並將結果覆寫回 `x` 的位置。
    5. `SP++`：SP 加 1 (指向結果之後的空位)。

#### B. 一元運算 (`neg`, `not`)
* **邏輯流程**：直接修改堆疊頂端的數值，**SP 不變**。
* **實作**：`SP--` 指向頂端數值，執行 `M = -M` 或 `M = !M`，SP 保持原位 (因為此時 SP 原本就指向下一個空位，邏輯上運算完還是在同一個位置)。

#### C. 比較運算 (`eq`, `gt`, `lt`) ⚠️ *最易出錯*
* **邏輯流程**：執行減法 `x - y`，根據結果觸發跳轉 (Jump)。
* **關鍵陷阱**：在 Hack 語言規範中，**True 是 `-1` (0xFFFF)**，而 **False 是 `0`**。
* **實作難點 (Unique Labels)**：
    由於 Assembly 是線性執行的，實作 `if (x == y)` 需要跳轉指令。
    必須為每一個比較指令生成**唯一的 Label** (例如 `EQ_TRUE_1`, `EQ_END_1`)，利用計數器 (Counter) 來避免多個 `eq` 指令導致的標籤衝突。

---

### 2. 記憶體區段映射 (Memory Segments)
VM Translator 必須將虛擬的記憶體區段 (Segments) 轉換為 Hack RAM 的實體位址操作。

| VM Segment | 對應 Hack 機制 | 實作公式 (Address Calculation) | 備註 |
| :--- | :--- | :--- | :--- |
| **constant** | 純數值 | 無 | 直接 `D=i`, `push D` |
| **local** | 基底位址在 RAM[1] (LCL) | `addr = RAM[LCL] + index` | 間接定址 |
| **argument** | 基底位址在 RAM[2] (ARG) | `addr = RAM[ARG] + index` | 間接定址 |
| **this** | 基底位址在 RAM[3] (THIS) | `addr = RAM[THIS] + index` | 間接定址 |
| **that** | 基底位址在 RAM[4] (THAT) | `addr = RAM[THAT] + index` | 間接定址 |
| **temp** | 固定映射 | `addr = 5 + index` | 映射到 RAM[5] - RAM[12] |
| **pointer** | 0/1 切換 | `addr = 3 + index` | 0 對應 `THIS`，1 對應 `THAT` |
| **static** | 靜態變數 | `@FileName.index` | 例如 `@Xxx.0`，由 Assembler 分配 |

> **實作提示 (Pop)**：實作 `pop segment i` 時，需先計算目標位址並存入臨時暫存器 (如 `R13`)，再將堆疊數值 Pop 到 D，最後寫入 `*R13`。

---

## 📂 專案結構
* `Parser.py`: 解析 VM 指令，去除空白與註解，拆解指令結構。
* `CodeWriter.py`: 核心轉譯邏輯，負責輸出 Assembly 代碼與處理 Label 命名。
* `Main.py`: 程式入口，串接 Parser 與 CodeWriter。

## 🚀 如何執行
在終端機輸入以下指令：

```bash
python Main.py YourFile.vm
```

或者:
```bash
python Main.py YourDirectory/
```

## 參考資料
[Gemini對話](https://gemini.google.com/share/43b803d804a2)