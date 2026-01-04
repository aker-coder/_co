# Nand2Tetris Project 3: 時序邏輯與記憶體

> ⚠️ **本文件由 AI 生成並進行內容理解與整合**

---

## 📖 專案概述

**目標**：從組合邏輯進入**時序邏輯 (Sequential Logic)**，設計能夠「記住」狀態的電路元件。

這是計算機歷史上的關鍵進步：從無記憶的邏輯門，到具有記憶功能的電路。

---

## 🚀 核心概念

### 組合 vs 時序

| 特性 | 組合邏輯 | 時序邏輯 |
| :--- | :--- | :--- |
| **輸出依賴** | 僅取決於當前輸入 | 取決於當前輸入 + 過去狀態 |
| **記憶能力** | 無 | 有 |
| **應用** | 加法器、多工器 | 計數器、暫存器、內存 |
| **時間性** | 無關時間 | 與時鐘同步 |

### 時鐘信號
- **時鐘 (Clock)**：週期性的 0/1 信號，同步所有時序元件
- **上升邊沿 (Rising Edge)**：0 → 1 的轉換，觸發狀態更新
- **時鐘週期**：決定了電路的最高執行速度

---

## 🛠️ 實作內容

### 第 1 級：基礎時序元件

#### 1. SR Latch (Set-Reset閂鎖)
最基本的記憶單元，無時鐘控制。

| S | R | Q | !Q | 狀態 |
| :--- | :--- | :--- | :--- | :--- |
| 0 | 0 | Hold | Hold | 保持 |
| 1 | 0 | 1 | 0 | Set |
| 0 | 1 | 0 | 1 | Reset |
| 1 | 1 | ? | ? | 禁止 |

#### 2. D Flip-Flop (D 觸發器) ⭐ *最重要*
**功能**：在時鐘上升邊沿捕捉輸入並輸出。

```
   D (Data)
    ↓
  [D Flip-Flop]
    ↓
   Q (Output)
   
行為：在每個時鐘脈衝時，Q ← D
```

**時序圖**：
```
CLK:   ___|‾‾‾|___|‾‾‾|___|‾‾‾|
D:     ___1___0___1___
Q:     _______1___0___1   (延遲一個時鐘週期)
       ↑上升邊沿捕捉
```

---

### 第 2 級：暫存器 (Registers)

#### 1-bit Register
```
D Flip-Flop + Mux (反饋迴路)
用於選擇：新輸入 或 保持舊值
```

#### 16-bit Register
```
16 個 1-bit Register 並聯
允許並行讀寫 16 位數據
```

**應用**：CPU 中的暫存器（R0-R15）。

#### Bit Register 與 Load 信號
```
load=1: 接受新輸入
load=0: 保持舊值
```

---

### 第 3 級：計數器 (Counters)

#### 程式計數器 (Program Counter, PC)

**三種工作模式**（由控制位決定）：

| reset | load | inc | 行為 |
| :--- | :--- | :--- | :--- |
| 1 | x | x | PC ← 0 |
| 0 | 1 | x | PC ← input |
| 0 | 0 | 1 | PC ← PC + 1 |
| 0 | 0 | 0 | PC ← PC (保持) |

**應用**：追蹤程式執行位置。

**邏輯流**：
```
         ┌────────┐
         ↓        │
    [Inc16]       │
         ↓        │
    [Mux16] ← load
         ↓        │
    [Register] ← reset/load
         ↓
        PC
```

---

### 第 4 級：記憶體 (Memory)

#### RAM (Random Access Memory)

**特性**：
- **隨機存取**：可直接存取任意位址（vs. 順序存取磁帶）
- **易失性**：掉電後資料消失
- **讀寫**：支援 `Read` 和 `Write`

#### 結構：位址解碼與多工
```
      address[k]
         ↓
    [地址解碼器]  → 選擇第 i 個字
         ↓
    RAM[0]  ← 選中讀寫
    RAM[1]
    ...
    RAM[n]
```

#### 16 位 RAM 的層級結構

| 大小 | 組成 | 實作方法 |
| :--- | :--- | :--- |
| **RAM8** | 8 個 16 位暫存器 | 3 位地址，DMux8Way 選擇 |
| **RAM64** | 8 個 RAM8 | 3+3=6 位地址，兩層解碼 |
| **RAM512** | 8 個 RAM64 | 3+3+3=9 位地址，三層解碼 |
| **RAM4K** | 8 個 RAM512 | 3+3+3+3=12 位地址，四層解碼 |
| **RAM16K** | 4 個 RAM4K | 2+12=14 位地址 |

#### 地址空間映射 (Memory Map)

```
0x0000 (0)
  ↓
[Data Memory]  (0-16383)
  ↓
0x4000 (16384)
  ↓
[Screen Memory] (16384-24575)
  ↓
0x6000 (24576)
  ↓
[Keyboard Register] (24576, 唯讀)
  ↓
0x6001+
```

---

## 💡 實作亮點

### 1. 反饋迴路 (Feedback Loop)
時序元件的核心：
```
當前輸出 → 邏輯組合 → 下一狀態 → D Flip-Flop → 當前輸出
```
這形成了一個**自洽迴圈**。

### 2. 層級化記憶體設計
```
RAM16K = 4× RAM4K
       = 4×8× RAM512
       = 4×8×8× RAM64
       = 4×8×8×8× RAM8
       = 4×8×8×8×8 Register
```
每層使用 DMux 進行選擇，避免地址線爆炸。

### 3. 讀寫分離
```
in[16]   → [寫入邏輯]  → 更新 RAM[addr]
address[15]
→ [讀取邏輯]  → out[16]
```

---

## 🔧 HDL 設計模式

### D Flip-Flop（已給定）
```hdl
CHIP DFF {
    IN in;
    CLK;
    OUT out;
    // 內部實現（由底層提供）
}
```

### 1-bit Register
```hdl
CHIP Bit {
    IN in, load;
    OUT out;
    
    PARTS:
    Mux(a=out, b=in, sel=load, out=mux_out);
    DFF(in=mux_out, out=out);
}
```

### RAM8 層級
```hdl
CHIP RAM8 {
    IN in[16], load, address[3];
    OUT out[16];
    
    PARTS:
    DMux8Way(in=load, sel=address, 
             out=load0, out1, ..., out7);
    Register(in=in, load=load0, out=ram0);
    Register(in=in, load=load1, out=ram1);
    // ...
    Mux8Way16(a=ram0, b=ram1, ..., h=ram7,
              sel=address, out=out);
}
```

### RAM16K（多層）
```hdl
CHIP RAM16K {
    IN in[16], load, address[14];
    OUT out[16];
    
    PARTS:
    DMux4Way(in=load, sel=address[12..13],
             out=load0, out1, out2, out3);
    RAM4K(in=in, load=load0, address=address[0..11], out=ram0);
    RAM4K(in=in, load=load1, address=address[0..11], out=ram1);
    // ...
    Mux4Way16(a=ram0, b=ram1, c=ram2, d=ram3,
              sel=address[12..13], out=out);
}
```

---

## 📊 時序圖示例

### Register 的時序行為
```
CLK: __|‾‾|__|‾‾|__|‾‾|__|‾‾|__
load: ___1____________1_________
in:   ___X____Y____Z____W_______
out:  ___[X後延]________[Y后延]__
      ↑t0 ↑t1  ↑t2 ↑t3
```

### 記憶體讀寫
```
讀取：address → [地址解碼] → RAM → out (組合邏輯，無延遲)
寫入：address, in, load → RAM 更新（在下一個時鐘邊沿）
```

---

## 🎓 關鍵理解

### 1. 時鐘同步
所有時序元件共用一個全局時鐘，確保系統的一致性與可預測性。

### 2. 狀態轉移
每個時鐘週期，系統從一個穩定狀態轉遷到下一個狀態。

### 3. 記憶的本質
記憶本質上是通過**反饋迴路**實現的自洽：當前狀態維持自己的存在。

### 4. 記憶體層級
```
暫存器 → RAM → 快取 → 硬碟
速度：快 ─────────────→ 慢
容量：小 ─────────────→ 大
成本：高 ─────────────→ 低
```

---

## 📁 檔案清單

```
Project 3: Sequential Logic
├── Bit.hdl / .tst / .cmp
├── Register.hdl / .tst / .cmp
├── RAM8.hdl / .tst / .cmp
├── RAM64.hdl / .tst / .cmp
├── RAM512.hdl / .tst / .cmp
├── RAM4K.hdl / .tst / .cmp
├── RAM16K.hdl / .tst / .cmp
└── PC.hdl / .tst / .cmp
```

---

## ✅ 學習成果

完成此章節後，你將理解：
- ✅ 時序邏輯與組合邏輯的根本區別
- ✅ D Flip-Flop 作為記憶單元的角色
- ✅ 暫存器與計數器的設計原理
- ✅ 多層級記憶體的層級結構
- ✅ 時鐘同步的重要性

---

> 🎯 **記憶使電腦能夠進行複雜的計算。掌握時序邏輯，你就掌握了計算機的大腦。**
