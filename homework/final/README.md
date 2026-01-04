# Nand2Tetris 完整課程專案統整

> ✨ **本文件1~2章為原創內容**
> ⚠️ **本文件3~5章由 AI 生成並進行內容理解與整合**

---

## 📚 目錄
1. [第 6 章：Hack 組譯器 (Assembler)](#第-6-章hack-組譯器)
2. [第 7 章：虛擬機轉譯器 - 堆疊運算](#第-7-章虛擬機轉譯器---堆疊運算)
3. [第 8 章：虛擬機轉譯器 - 流程控制與函式呼叫](#第-8-章虛擬機轉譯器---流程控制與函式呼叫)
4. [第 9 章：高階語言與遊戲開發](#第-9-章高階語言與遊戲開發)
5. [第 10 章：編譯器 - 語法分析](#第-10-章編譯器---語法分析)
6. [第 11 章：編譯器 - 代碼生成](#第-11-章編譯器---代碼生成)
7. [第 12 章：作業系統](#第-12-章作業系統)

---

## 第 6 章：Hack 組譯器

### 📖 概述
**目標**：將 Hack 組合語言 (`.asm`) 翻譯成 Hack 電腦硬體可執行的二進位機器碼 (`.hack`)。

### 🚀 核心功能
- **完整指令支援**：A 指令 (`@value`) 與 C 指令 (`dest=comp;jump`)
- **符號解析**：
  - 預定義符號（`SCREEN`, `KBD`, `R0`~`R15`）
  - 標籤（`LOOP`, `END`）用於跳轉
  - 變數自動分配記憶體位址（從 RAM[16] 開始）
- **兩遍掃描演算法**：解決向前參考 (Forward Reference) 問題

### 🛠️ 專案結構
```
Assembler.py
├── Parser：讀取與解析 .asm 檔案
├── Code：將助記符轉換為二進位碼
└── SymbolTable：管理符號與記憶體位址對應
```

### 💡 理解重點
- 組合語言是硬體與軟體的橋樑
- 符號表動態管理提高代碼可讀性
- 兩遍掃描確保所有標籤能被正確解析

---

## 第 7 章：虛擬機轉譯器 - 堆疊運算

### 📖 概述
**目標**：將中階虛擬機語言 (`.vm`) 轉譯為底層 Hack 組合語言 (`.asm`)。
本章重點是理解**堆疊機**思維與虛擬記憶體區段的映射。

### 🚀 核心功能

#### 堆疊算術運算
| 指令類型 | 範例 | 邏輯 |
| :--- | :--- | :--- |
| **二元運算** | `add`, `sub`, `and`, `or` | Pop y → Pop x → Push(x op y) |
| **一元運算** | `neg`, `not` | 直接修改堆疊頂端（SP 不變） |
| **比較運算** | `eq`, `gt`, `lt` | 減法 + 條件跳轉（True = -1, False = 0） |

#### 記憶體區段映射
| VM Segment | Hack 機制 | 實作公式 |
| :--- | :--- | :--- |
| constant | 純數值 | 直接 `D=i` |
| local | 基底位址在 RAM[1] (LCL) | `addr = RAM[LCL] + index` |
| argument | 基底位址在 RAM[2] (ARG) | `addr = RAM[ARG] + index` |
| this | 基底位址在 RAM[3] | `addr = RAM[THIS] + index` |
| that | 基底位址在 RAM[4] | `addr = RAM[THAT] + index` |
| temp | 固定映射 | `addr = 5 + index` |
| pointer | 0/1 切換 | `addr = 3 + index` |
| static | 靜態變數 | `@FileName.index` |

### 💡 理解重點
- **堆疊機是一種抽象模型**：簡化了複雜的暫存器管理
- **唯一標籤生成**：比較運算需要為每個指令生成唯一標籤以避免衝突
- **位址計算優化**：使用暫存器 `R13` 存儲目標位址，提高轉譯效率

---

## 第 8 章：虛擬機轉譯器 - 流程控制與函式呼叫

### 📖 概述
**目標**：擴充第 7 章的功能，支援程式流程控制與函式呼叫機制。

### 🚀 核心功能

#### 1. 流程控制
- `label labelName`：定義跳轉標籤
- `goto labelName`：無條件跳轉
- `if-goto labelName`：條件跳轉（堆疊頂端非零則跳轉）

#### 2. 函式呼叫
| 指令 | 功能 | 核心邏輯 |
| :--- | :--- | :--- |
| `function funcName nVars` | 定義函式 | 初始化 nVars 個區域變數為 0 |
| `call funcName nArgs` | 呼叫函式 | 保存 Caller 狀態、配置新 Stack Frame |
| `return` | 函式返回 | 恢復 Caller 狀態、回傳值 |

#### 3. Stack Frame 結構
```
[Return Address]  ← 返回位址
[LCL]             ← 保存的 Caller 局部變數指標
[ARG]             ← 保存的 Caller 參數指標
[THIS]            ← 保存的 Caller this
[THAT]            ← 保存的 Caller that
[local 0..n]      ← 被調函式的局部變數
[arg 0..m]        ← 被調函式的參數
```

#### 4. Bootstrap 代碼
自動寫入初始化代碼，將 `SP` 設為 256，並呼叫 `Sys.init` 啟動程式。

### 🧪 推薦測試順序
| 階段 | 測試項目 | 重點 | Bootstrap |
| :--- | :--- | :--- | :--- |
| 1 | SimpleFunction | function / return 基礎 | 關閉 |
| 2 | NestedCall | 嵌套呼叫 | 開啟 |
| 3 | FibonacciElement | 遞迴演算法 | 開啟 |
| 4 | StaticsTest | 靜態變數命名空間 | 開啟 |

### 💡 理解重點
- **Stack Frame 是函式呼叫的核心**：透過統一的結構保存與恢復狀態
- **遞迴的可能性**：正確的 Stack Frame 管理使遞迴得以實現
- **多檔案支援**：靜態變數需要帶前綴 (`ClassName.variableName`) 確保命名空間隔離

---

## 第 9 章：高階語言與遊戲開發

### 📖 概述
**專案名稱**：Sky Defender（射擊遊戲）  
**目標**：使用 Jack 高階語言（類似 Java）開發遊戲應用，運行於 VMEmulator。

### 🎮 Jack 語言基本語法

#### 語言特性
| 特性 | 說明 |
| :--- | :--- |
| 類別結構 | 每檔案一個 class，無繼承 |
| 變數宣告 | 必須置於所有邏輯語句之前 |
| 函式類型 | `function`, `method`, `constructor` |
| 特殊關鍵字 | `do`（void 函式呼叫）, `let`（賦值）, `Array.new()` |

#### 變數作用域
| 類型 | 作用範圍 | 說明 |
| :--- | :--- | :--- |
| field | 物件屬性 | 所有方法可存取 |
| static | 全域共享 | 類別中所有方法共享 |
| var | 區域變數 | 僅函式內可用 |
| arg | 參數 | 函式簽名定義 |

### 🎯 遊戲架構

#### 檔案結構
| 檔案 | 職責 |
| :--- | :--- |
| Main.jack | 進入點，初始化並啟動遊戲 |
| Game.jack | 核心控制邏輯，管理玩家/敵人/子彈 |
| Player.jack | 玩家飛機的屬性與繪製 |
| Enemy.jack | 敵人的移動與重置 |
| Bullet.jack | 子彈的飛行邏輯 |

#### 遊戲迴圈
```
1. Input：檢測鍵盤（Keyboard.keyPressed）
2. Update：計算新座標
3. Collision：碰撞檢測（AABB）
4. Draw：擦除舊位置 + 繪製新位置
5. Wait：控制 FPS（Sys.wait(30)）
```

#### 碰撞檢測
採用 **AABB (Axis-Aligned Bounding Box)**：檢查兩矩形是否在四個方向都有重疊。

### 🧠 設計亮點
- **記憶體管理**：手動 `dispose()` 避免內存洩漏
- **Debounce 處理**：按鍵狀態鎖定防止連發
- **堆積 Heap 存取**：使用 `pointer 1` (THAT) 動態存取陣列

### ⚠️ 常見問題
**Q：按空白鍵沒有發射子彈？**  
**A：切換到英文輸入法。中文輸入法會攔截空白鍵訊號。**

---

## 第 10 章：編譯器 - 語法分析

### 📖 概述
**目標**：驗證 Jack 程式碼語法是否正確，產出 XML 語法樹。

### 🚀 核心模組

#### JackTokenizer（斷詞）
- **功能**：將原始碼切分為有意義的單字 (Token)
- **輸出格式**：
  ```xml
  <tokens>
    <keyword> class </keyword>
    <identifier> Main </identifier>
    <symbol> { </symbol>
  </tokens>
  ```
- **實作技巧**：使用正規表達式 (Regex) 進行模式匹配

#### CompilationEngine（語法分析）
- **方法**：遞迴下降分析 (Recursive Descent Parsing)
- **輸出**：完整 XML 語法樹
- **邏輯**：看到什麼就吐出什麼 XML 標籤

### 💡 理解重點
- **正規表達式的威力**：一行 Regex 可解決複雜的模式識別
- **遞迴下降分析**：自然地對應語法規則的遞迴結構
- **XML 作為中間表示**：便於除錯與視覺化檢驗

---

## 第 11 章：編譯器 - 代碼生成

### 📖 概述
**目標**：從 Jack 高階語言產生可執行的 VM 中介碼 (`.vm`)。

### 🚀 與第 10 章的演進

| 特徵 | 第 10 章 (XML) | 第 11 章 (VM) |
| :--- | :--- | :--- |
| **輸出工具** | 直接寫檔案 | 透過 VMWriter 封裝 |
| **變數處理** | 純文字標籤 | 查表取得記憶體索引 |
| **運算式輸出** | 中序 (Infix) XML | 後序 (Postfix) 指令 |

### 🎯 核心實作

#### SymbolTable（符號表）
**資料結構**：兩個 Hash Map
- `class_table`：存 `static` 與 `field`
- `subroutine_table`：存 `arg` 與 `var`

**操作**：
```python
startSubroutine()      # 進入新函式，清空 subroutine_table
define(name, type, kind)  # 添加新變數
indexOf(name)          # 查詢變數索引
```

#### VMWriter（VM 寫入器）
**設計模式**：Facade Pattern（外觀模式）
```python
writePush(segment, index)      # 生成 push 指令
writePop(segment, index)       # 生成 pop 指令
writeArithmetic(command)       # 生成算術指令
writeLabel(label)              # 生成標籤
```

#### CompilationEngine（核心引擎）

**1. 運算式編譯**
- 後序遍歷轉換：`a + b` → `push a`, `push b`, `add`
- 優先權透過遞迴層級處理

**2. 流程控制**
```
If：   生成 L1, L2 標籤，利用 not + if-goto 實作 Else
While：生成 L1 (開頭), L2 (結尾)，結束時 goto L1
```

**3. 陣列存取** ⚠️ *最難的部分*
```
arr[i] 的存取步驟：
1. push arr        # 推入陣列基底位址
2. push i          # 推入索引
3. add             # 計算真實位址
4. pop pointer 1   # 讓 THAT 指向該位址
5. push that 0     # 讀取值
```

**4. 物件導向**
- Method 呼叫自動在第一個參數推入 `this`
- Constructor 呼叫 `Memory.alloc` 分配記憶體

### 💡 理解重點
- **堆疊機思維**：後序運算式完全符合 VM 的堆疊運作
- **指標重導**：`pointer 1` (THAT) 是動態存取記憶體的核心
- **圖靈完備**：支援變數、迴圈、分支、函式呼叫 → 理論上可計算任何問題

---

## 第 12 章：作業系統

### 📖 概述
**目標**：在 Hack 硬體架構之上，透過 Jack OS 補足硬體功能缺失。

### ⚠️ 學習方式
根據課程規定，本章重點在於**理解設計原理**而非從零實作。
建議研讀現有實作，深入理解各模組的演算法。

### 🏗️ OS 模組架構

#### 1. **Math.jack**（數學運算）
| 函式 | 實作方法 |
| :--- | :--- |
| `multiply(x, y)` | Bit-shift + 加法（模擬長乘法） |
| `divide(x, y)` | 遞迴長除法 |
| `sqrt(x)` | 牛頓法或二分搜尋 |

**設計亮點**：預先計算 $2^i$ 陣列 (`twoToThe`) 提升效能

#### 2. **Memory.jack**（記憶體管理）
- **機制**：Free List（空閒列表）演算法
- **操作**：
  - `alloc(size)`：First-fit 或 Best-fit 尋找空閒區塊
  - `deAlloc(obj)`：歸還記憶體
  - `peek(addr)`, `poke(addr, value)`：直接存取

#### 3. **Screen.jack**（螢幕繪圖）
- **記憶體映射**：RAM[16384] ~ RAM[24575]（512×256 像素）
- **操作**：
  - `drawPixel(x, y, color)`：畫點
  - `drawLine(x1, y1, x2, y2, color)`：Bresenham 演算法
  - 優化：橫向直線一次寫 16 bits

#### 4. **Output.jack**（文字輸出）
- **字型庫**：ASCII → 11×8 像素矩陣
- **功能**：`printChar()`, `printString()`, `printInt()`
- **特性**：游標移動、換行、Backspace 處理

#### 5. **Keyboard.jack**（鍵盤輸入）
- **記憶體映射**：RAM[24576]（鍵盤暫存器）
- **功能**：`readLine()`, `readInt()`，含輸入緩衝與回顯

#### 6. **String.jack**（字串處理）
- **表示**：字元陣列
- **操作**：長度、附加字元、整數轉換

#### 7. **Array.jack**（陣列支援）
- **輕量級封裝**：直接呼叫 `Memory.alloc()` / `Memory.deAlloc()`

#### 8. **Sys.jack**（系統核心）
| 函式 | 功能 |
| :--- | :--- |
| `init()` | 初始化所有 OS 模組，呼叫 `Main.main` |
| `wait(ms)` | 延遲（空迴圈） |
| `halt()` | 停止系統（無窮迴圈） |

### 💡 理解重點
- **軟體補硬體**：無乘法器 → 用軟體實作乘法
- **記憶體與 I/O 映射**：統一的記憶體模型簡化硬體設計
- **OS 的分層架構**：高層函式建立在低層服務之上

---

## 🎓 學習總結

### 三大核心概念

1. **從硬體到軟體的進階**
   - 第 6 章：組合語言（最接近硬體）
   - 第 7-8 章：虛擬機中介層（抽象化）
   - 第 9-11 章：高階語言與編譯器（最接近人類思維）

2. **堆疊機思維**
   - 簡化的計算模型
   - 後序運算式自然對應堆疊操作
   - 虛擬記憶體區段隔離邏輯與實體記憶體

3. **編譯器設計**
   - Tokenization → Parsing → Code Generation
   - 符號表管理變數生命週期
   - 兩遍掃描解決前向參考

### 技術亮點

| 技術 | 應用章節 | 價值 |
| :--- | :--- | :--- |
| **正規表達式** | 第 10 章 | 簡潔高效的模式識別 |
| **遞迴下降分析** | 第 10-11 章 | 自然對應語法規則結構 |
| **Stack Frame** | 第 8 章 | 函式呼叫與遞迴的基礎 |
| **指標重導** | 第 11 章 | 動態記憶體存取的核心 |
| **Free List** | 第 12 章 | 堆積記憶體管理演算法 |

---

## 📁 專案文件結構
```
final/
├── 6/  → Hack 組譯器
├── 7/  → VM 轉譯器（堆疊運算）
├── 8/  → VM 轉譯器（流程控制與函式）
├── 9/  → Jack 高階語言遊戲
├── 10/ → 編譯器（語法分析）
├── 11/ → 編譯器（代碼生成）
├── 12/ → 作業系統
└── README.md  ← 本檔案
```

---

## 📚 參考資源
- **官方課程**：[Nand2Tetris](https://www.nand2tetris.org/)
- **教科書**：*The Elements of Computing Systems* by Noam Nisan & Shimon Schocken
- **GitHub 參考實作**：[CPU2OS](https://github.com/ccc114a/cpu2os)

---

> ✅ **本文件涵蓋 Nand2Tetris 課程第 6-12 章的完整內容統整。**  
> 每個章節均包含功能概述、核心實作細節與理解重點，適合作為複習與參考資料。
