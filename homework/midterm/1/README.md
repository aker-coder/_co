# Nand2Tetris Project 1: 基礎邏輯閘

> ✨ **本文件為原創內容**

---

## 📖 專案概述

**目標**：使用 NAND 閘（唯一的基本元件）構建所有基礎邏輯閘與多位元元件。

這是 Nand2Tetris 課程的第一步，強調的是：**所有複雜的數位電路都可由最簡單的基礎邏輯門組合而成**。

---

## 🚀 核心概念

### 布林函數 (Boolean Functions)
| 運算 | 邏輯 | 真值表 |
| :--- | :--- | :--- |
| **AND** | 兩者都真 | 1 AND 1 = 1 |
| **OR** | 至少一個真 | 0 OR 1 = 1 |
| **NOT** | 反轉 | NOT 1 = 0 |
| **XOR** | 互斥或 | 1 XOR 1 = 0 |
| **NAND** | NOT AND | NAND(1,1) = 0 |

### 萬能元件：NAND 閘
**特性**：NAND 是一個「**萬能閘**」，可組合出任何其他邏輯閘。

**證明**：
```
NOT x        = NAND(x, x)
AND(x, y)    = NOT(NAND(x, y))
OR(x, y)     = NAND(NOT x, NOT y)  [De Morgan 定律]
```

---

## 🛠️ 實作內容

### 第 1 級：基礎邏輯閘（一位元）

| 元件 | 輸入 | 輸出 | 實作方法 |
| :--- | :--- | :--- | :--- |
| **Not** | 1 位 | 1 位 | `NAND(a, a)` |
| **And** | 2 位 | 1 位 | `NOT(NAND(a, b))` |
| **Or** | 2 位 | 1 位 | `NAND(NOT a, NOT b)` |
| **Xor** | 2 位 | 1 位 | 組合 AND, OR, NOT |
| **Mux** | 2 數據 + 1 選擇 | 1 位 | 多工器（選擇器） |
| **DMux** | 1 數據 + 1 選擇 | 2 位 | 解多工器（分配器） |

### 第 2 級：多位元擴展（16 位元）

| 元件 | 說明 | 應用 |
| :--- | :--- | :--- |
| **Not16** | 16 個 NOT 閘並聯 | 位元反轉 |
| **And16** | 16 個 AND 閘並聯 | 位元與 |
| **Or16** | 16 個 OR 閘並聯 | 位元或 |
| **Mux16** | 根據選擇信號選擇兩個 16 位數 | 數據選擇 |
| **Or8Way** | 8 輸入的 OR 級聯 | 檢查任何位為 1 |

### 第 3 級：多選多工器（複合邏輯）

| 元件 | 功能 | 實作邏輯 |
| :--- | :--- | :--- |
| **Mux4Way16** | 從 4 個 16 位數據中選 1 個 | 2 位選擇信號 |
| **Mux8Way16** | 從 8 個 16 位數據中選 1 個 | 3 位選擇信號 |
| **DMux4Way** | 將 1 位送到 4 個輸出之一 | 2 位選擇信號 |
| **DMux8Way** | 將 1 位送到 8 個輸出之一 | 3 位選擇信號 |

---

## 💡 實作亮點

### 1. 遞迴性與階層化
- 每級元件都建立在上一級之上
- `Mux8Way16` = `Mux4Way16` + `Mux4Way16` + `Mux16`
- 展現了**分而治之 (Divide & Conquer)** 的設計哲學

### 2. 多工與解多工的對稱性
```
Mux：  多個輸入 → [選擇信號] → 單一輸出
DMux： 單一輸入 → [選擇信號] → 多個輸出
```
這對互補操作在數位設計中廣泛應用。

### 3. 位寬的統一性
- 所有 16 位元元件遵循同一邏輯
- 可輕鬆擴展到 32、64 位（只需增加級數）

---

## 🔧 HDL 設計模式

### 模式 1：直接組合
```hdl
CHIP Not {
    IN a;
    OUT out;
    
    PARTS:
    Nand(a=a, b=a, out=out);
}
```

### 模式 2：並聯 (Array)
```hdl
CHIP Not16 {
    IN in[16];
    OUT out[16];
    
    PARTS:
    Not(in=in[0], out=out[0]);
    Not(in=in[1], out=out[1]);
    // ... 依此類推到 15
}
```

### 模式 3：選擇邏輯 (Mux)
```hdl
CHIP Mux {
    IN a, b, sel;
    OUT out;
    
    PARTS:
    // sel=0 時輸出 a，sel=1 時輸出 b
    Not(in=sel, out=notsel);
    And(a=a, b=notsel, out=ax);
    And(a=b, b=sel, out=bx);
    Or(a=ax, b=bx, out=out);
}
```

### 模式 4：遞迴組合 (Mux4Way)
```hdl
CHIP Mux4Way16 {
    IN in[4][16], sel[2];
    OUT out[16];
    
    PARTS:
    Mux16(a=in[0], b=in[1], sel=sel[0], out=out0);
    Mux16(a=in[2], b=in[3], sel=sel[0], out=out1);
    Mux16(a=out0, b=out1, sel=sel[1], out=out);
}
```

---

## 🧪 測試方法

### HDL 與測試文件
每個元件均配有：
- **`.hdl` 檔**：硬體描述
- **`.tst` 檔**：測試腳本
- **`.cmp` 檔**：預期輸出（比較基準）

### 執行步驟
1. 在 Hardware Simulator 中打開 `.hdl` 檔
2. 加載對應的 `.tst` 檔
3. 執行測試並與 `.cmp` 文件比較
4. 如輸出相符，則設計正確 ✅

---

## 📊 設計複雜度

| 元件 | 輸入端 | 邏輯層級 | NAND 數量 |
| :--- | :--- | :--- | :--- |
| Not | 1 | 1 | 1 |
| And | 2 | 2 | 3 |
| Or | 2 | 3 | 6 |
| Xor | 2 | 4 | 12 |
| Mux | 3 | 4 | 12 |
| Mux8Way16 | 27 | 10+ | 100+ |

**觀察**：隨著功能複雜度增加，所需的基本 NAND 閘呈指數成長。

---

## 🎓 關鍵理解

### 1. 全域可組合性 (Universality)
- NAND 是完全的（任何布林函數都可用 NAND 實現）
- 啟發了 **計算通用性** 的概念

### 2. 抽象的力量
- 上層設計者無須知道下層如何實現
- 只需了解介面（輸入/輸出）即可

### 3. 模組化與階層化
- 複雜系統 = 簡單元件的遞迴組合
- 這是所有現代數位設計的基礎

---

## 📁 檔案清單

```
Project 1: Elementary Logic Gates
├── Not.hdl / Not.tst / Not.cmp
├── And.hdl / And.tst / And.cmp
├── Or.hdl / Or.tst / Or.cmp
├── Xor.hdl / Xor.tst / Xor.cmp
├── Mux.hdl / Mux.tst / Mux.cmp
├── DMux.hdl / DMux.tst / DMux.cmp
├── Not16.hdl / Not16.tst / Not16.cmp
├── And16.hdl / And16.tst / And16.cmp
├── Or16.hdl / Or16.tst / Or16.cmp
├── Mux16.hdl / Mux16.tst / Mux16.cmp
├── Or8Way.hdl / Or8Way.tst / Or8Way.cmp
├── Mux4Way16.hdl / Mux4Way16.tst / Mux4Way16.cmp
├── Mux8Way16.hdl / Mux8Way16.tst / Mux8Way16.cmp
├── DMux4Way.hdl / DMux4Way.tst / DMux4Way.cmp
└── DMux8Way.hdl / DMux8Way.tst / DMux8Way.cmp
```

---

## ✅ 學習成果

完成此章節後，你將理解：
- ✅ 布林邏輯與組合電路的基礎
- ✅ 如何用簡單元件構建複雜系統
- ✅ HDL (Hardware Description Language) 的基本語法
- ✅ 數位設計的模組化思想

---

> 🎯 **第 1 章是基礎之基礎。掌握這些邏輯門，就掌握了整個數位電路的靈魂。**
