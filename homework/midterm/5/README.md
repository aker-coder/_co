# Nand2Tetris Project 5: 計算機架構

> ⚠️ **本文件由 AI 生成並進行內容理解與整合**

---

## 📖 專案概述

**目標**：將前面設計的所有硬體元件整合成一台完整的電腦（Hack 電腦）。

這是課程硬體部分的**最終整合**。我們要把：
- 邏輯門 (Project 1)
- ALU (Project 2)
- 記憶體 (Project 3)
- 機器語言 (Project 4)

組合成一台能執行程式的**完整電腦系統**。

---

## 🚀 核心概念

### 計算機的三大部件

```
         ROM[PC]
            ↓
      [指令解碼]
            ↓
    ┌───────┴───────┐
    ↓               ↓
[控制信號]    [計算信號]
    ↓               ↓
[CPU] ←──────→ [ALU]
 ↓  ↑              ↓
 ↓  └──────────────┘
 ↓
[Memory] (RAM)
```

### 馮紐曼架構 (Von Neumann Architecture)

```
CPU
├─ PC (程式計數器)
├─ Registers (暫存器)
├─ ALU (算術邏輯單元)
└─ Control Unit (控制單元)
       ↓
   Memory (內存)
       ↓
   ROM (程式存儲)
       ↓
   I/O (鍵盤、螢幕)
```

---

## 🛠️ 實作內容

### 第 1 級：CPU (中央處理器)

#### CPU 的功能

```
輸入：
- instruction[16]：當前指令
- inM[16]：從 RAM[A] 讀取的值
- reset：重設信號

輸出：
- outM[16]：要寫入 RAM[A] 的值
- writeM：是否寫入 RAM
- addressM[15]：RAM 位址
- pc[15]：下一條指令位址
```

#### CPU 的內部結構

```
instruction[16]
       ↓
   ┌──┴──┐
   ↓     ↓
[是 A?] [是 C?]
   ↓     ↓
[A暫存] [控制邏輯]
   ↓     ↓
   ├→[A 值]
   │     ↓
   │   [ALU輸入選擇]
   │     ↓
   │   [ALU]
   │     ↓
   │   [D 暫存]
   │     ↓
   │   [輸出]
   │
   └→[PC邏輯]
```

#### A 指令處理 (instruction[15] = 0)
```
A指令：0vvvvvvvvvvvvvvv
       ↓
   A ← vvvvvvvvvvvvvv
   
用途：
- 設定 A 暫存器的值
- 用於後續的 M（RAM[A]） 存取
```

#### C 指令處理 (instruction[15] = 1)
```
C指令：111accccccdddjjj
       ↓
   ┌─────┬──────┬──────┐
   ↓     ↓      ↓      ↓
 comp  dest   jump  output
   ↓     ↓      ↓
 [ALU][目的地][跳轉]
        ↓      ↓
    [A/D/M] [PC更新]
```

| 控制信號 | 功能 |
| :--- | :--- |
| **zx** | 若為 1，將 x 輸入設為 0 |
| **nx** | 若為 1，反轉 x 輸入 (NOT x) |
| **zy** | 若為 1，將 y 輸入設為 0 |
| **ny** | 若為 1，反轉 y 輸入 (NOT y) |
| **f** | 若為 1，執行加法；否則執行與 |
| **no** | 若為 1，反轉輸出 (NOT output) |
| **d1** | 若為 1，將結果寫入 A 暫存 |
| **d2** | 若為 1，將結果寫入 D 暫存 |
| **d3** | 若為 1，將結果寫入 M = RAM[A] |
| **j1** | 若結果 < 0 且此位為 1，則跳轉 |
| **j2** | 若結果 = 0 且此位為 1，則跳轉 |
| **j3** | 若結果 > 0 且此位為 1，則跳轉 |

#### PC (程式計數器) 邏輯

```
Jump信號 = (結果 < 0 AND j1) OR
           (結果 = 0 AND j2) OR
           (結果 > 0 AND j3)

若 Jump = 1：
    PC ← A         (跳轉到 A 地址)
否則：
    PC ← PC + 1    (下一指令)

若 reset = 1：
    PC ← 0         (重設)
```

---

### 第 2 級：記憶體系統 (Memory)

#### 記憶體映射

```
0x0000 (0)
  ↓
[RAM 0-15383]  (數據記憶體)
  ↓
0x4000 (16384)
  ↓
[Screen]       (16384-24575，8KB)
  ├─ 512×256 像素
  ├─ 16 bits/word
  └─ 高位 = 上方像素，低位 = 下方像素
  ↓
0x6000 (24576)
  ↓
[Keyboard]     (24576，唯讀)
  └─ 最後按下的鍵的 ASCII 碼
  ↓
0x6001+
```

#### Memory 元件
```
輸入：
- in[16]：數據輸入
- load：寫入信號
- address[15]：位址

輸出：
- out[16]：讀取的值

邏輯：
address[14..13]:
  00 → RAM
  01 → RAM
  10 → Screen
  11 → Keyboard
```

---

### 第 3 級：完整計算機 (Computer)

#### Computer 的組成

```
Computer
├─ ROM
│  └─ 32K 指令存儲（初始化時載入程式）
├─ CPU
│  ├─ ALU
│  ├─ A 暫存
│  ├─ D 暫存
│  └─ PC
├─ Memory
│  ├─ RAM (16K)
│  ├─ Screen (8K)
│  └─ Keyboard (1)
└─ CLK (時鐘)
```

#### 數據流

```
主迴圈：
1. 指令取得：instr ← ROM[PC]
2. 指令解碼：控制信號 ← decode(instr)
3. 數據計算：result ← ALU(inputs, controls)
4. 數據存儲：RAM[A], D, A ← result (根據 dest)
5. 下一指令：PC ← (jump) ? A : PC+1

重複...
```

---

## 💡 實作亮點

### 1. 指令集完全性 (ISA Completeness)
Hack ISA 包含：
- ✅ 算術運算（加、減、AND、OR）
- ✅ 記憶體存取（RAM 讀寫）
- ✅ 分支控制（條件跳轉、無條件跳轉）
- ✅ I/O 操作（鍵盤、螢幕）
→ **圖靈完備** (能計算任何可計算的問題)

### 2. 記憶體映射 I/O
```
優點：
- 統一的編程模型（記憶體和 I/O 無區別）
- 簡化的硬體設計
- 易於擴展新設備

缺點：
- I/O 等待時間（鍵盤輸入阻塞）
```

### 3. 時鐘同步
所有時序元件（PC、暫存器、RAM）共用時鐘：
```
上升邊沿 → 所有狀態同時更新 → 下降邊沿 → 穩定期
         ↓
      計算新狀態
```

---

## 🔧 HDL 設計

### CPU 的主要邏輯

```hdl
CHIP CPU {
    IN inM[16], instruction[16], reset;
    OUT outM[16], writeM, addressM[15], pc[15];
    
    PARTS:
    // 分類指令（A vs C）
    Not(in=instruction[15], out=isAinst);
    
    // A 暫存（A 指令直接寫入，C 指令需檢查 d1）
    Mux16(a=aluout, b=instruction, sel=isAinst, out=toA);
    ARegister(in=toA, load=d1flag, out=aval, out[0..14]=addressM);
    
    // 選擇 ALU 輸入（y 可來自 A 或 M）
    Mux16(a=aval, b=inM, sel=instruction[12], out=yval);
    
    // ALU 與控制信號
    ALU(x=dval, y=yval,
        zx=instruction[11], nx=instruction[10],
        zy=instruction[9], ny=instruction[8],
        f=instruction[7], no=instruction[6],
        out=aluout, out=outM,
        zr=zrflag, ng=ngflag);
    
    // D 暫存
    DRegister(in=aluout, load=d2flag, out=dval);
    
    // PC 邏輯
    PC(in=aval, inc=true, load=jumpsignal, reset=reset, out[0..14]=pc);
}
```

### Memory 的選址邏輯

```hdl
CHIP Memory {
    IN in[16], load, address[15];
    OUT out[16];
    
    PARTS:
    DMux(in=load, sel=address[14], out=loadram, out=loadio);
    
    RAM16K(in=in, load=loadram, address=address[0..13], out=ramout);
    
    // address[13] 選擇 Screen 或 Keyboard
    Mux16(a=screenout, b=kbdout, sel=address[13],
          out=ioout);
    Screen(in=in, load=loadscreen, address=address[0..12], out=screenout);
    Keyboard(out=kbdout);
    
    Mux16(a=ramout, b=ioout, sel=address[14], out=out);
}
```

---

## 📊 時序圖範例

### 執行 `D=D+A` 的時序

```
時刻 t0：
  ROM[PC] → 1110000010010000 (D=D+A)
  解碼 → ALU 執行 D+A
  結果 → Dval

時刻 t1 (上升邊沿)：
  D 暫存 ← 新值
  PC ← PC+1

時刻 t2：
  新 PC 值 → ROM[PC+1]
  新指令被取得
```

---

## 🎓 關鍵理解

### 1. 取指執行迴圈 (Fetch-Execute Cycle)
```
Fetch → Decode → Execute → Write-Back → Next PC
```
這是所有馮紐曼架構電腦的核心。

### 2. 指令的三部分
```
A 指令：直接設定位址
C 指令：執行計算（comp）
        決定存儲位置（dest）
        決定是否跳轉（jump）
```

### 3. 記憶體階層
```
速度快：暫存器 (CPU 內)
  ↓
記憶體快：RAM (數百個時鐘週期)
  ↓
速度慢：磁碟 (百萬時鐘週期)
```

### 4. I/O 映射的優雅性
```
統一模型 → 簡化編程
RAM[16384] = 像素
RAM[24576] = 按鍵

無需特殊 I/O 指令！
```

---

## 📁 檔案清單

```
Project 5: Computer Architecture
├── Memory.hdl       (記憶體單元)
├── CPU.hdl          (處理器核心)
├── Computer.hdl     (完整計算機)
└── 測試檔案
```

---

## ✅ 學習成果

完成此章節後，你將理解：
- ✅ CPU 的內部結構與指令執行
- ✅ 取指執行迴圈的工作原理
- ✅ A 和 C 指令的處理流程
- ✅ 記憶體映射與 I/O 整合
- ✅ 時鐘同步的關鍵作用
- ✅ 馮紐曼架構的實現

---

## 🚀 運行程式

完成 CPU 和 Memory 後，你可以：

1. **編譯程式**（第 6 章組譯器）
2. **加載到 ROM**
3. **在 CPU 模擬器中運行**
4. **觀察執行狀態**：
   - 暫存器值
   - 記憶體變化
   - PC 進度
   - 螢幕輸出

---

## 進階思考

### 性能優化
```
現在：1 指令 = 1 時鐘週期

改進：
- 流水線 (Pipelining) → 多指令並行
- 快取 (Caching) → 減少記憶體延遲
- 並行 (Parallelism) → 多核處理
```

### 指令集擴展
```
現有：算術、邏輯、跳轉

新增：
- 浮點運算
- SIMD (單指令多數據)
- 虛擬記憶體
```

---

> 🎯 **從邏輯門到完整電腦，你見證了計算機從無到有的創造過程。這就是 Nand2Tetris 課程的精髓：理解電腦的每一層。**
