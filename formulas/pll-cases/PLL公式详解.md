# PLL 公式详解

**PLL = Permutation of Last Layer = 最后一层换位**

这是CFOP的第4步，也是最后一步。OLL完成后，最后一层所有块的颜色都朝上了，但位置还不对。PLL就是把这些块移到正确的位置。

PLL共21个公式，按字母分类命名。

---

## 棱块轮换（角不动，最简单的PLL）

### U Permutation
**U = U型三轮换**

棱块呈U形循环移动，角块位置不动。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Ua** | U Permutation a | R U' R U R U R U' R' U' R2 |
| **Ub** | U Permutation b | R2 U R U R' U' R' U' R' U R' |

### Z Permutation
**Z = Z型对棱交换**

平行的两条对棱交换，呈Z字形。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Z** | Z Permutation | M2 U M2 U2 M2 U M2 |

### H Permutation
**H = H型对棱交换**

十字形的两条对棱交换。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **H** | H Permutation | M2 U M2 U M' U2 M2 U2 M' U2 |

---

## 角块交换（棱不动）

### E Permutation
**E = E型对角交换**

两个对角块交换，棱块不动。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **E** | E Permutation | x' R U R' D R U' R' D' R U R' D R U' R' D' |

---

## 角三棱三（最常用的PLL）

### A Permutation
**A = Adjacent corner swap = 相邻角交换**

两个相邻角交换，同时三个棱块轮换。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Aa** | A Permutation a | x R' U R' D2 R U' R' D2 R2 |
| **Ab** | A Permutation b | x R2 D2 R U R' D2 R U' R |

---

## G Permutation 四轮换
**G = G型四轮换**

角和棱都在动的大循环，共4个变体。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Ga** | G Permutation a | R2 U R U R' U' R' U' R' U R' |
| **Gb** | G Permutation b | R' U' R U' R U R U' R' U R U R2 |
| **Gc** | G Permutation c | R2 U' R' U' R U R U R U' R |
| **Gd** | G Permutation d | R U R' U R' U' R' U R U' R' U' R2 |

---

## 相邻角 + 相邻棱

### R Permutation
**R = R型交换**

相邻角 + 相邻棱交换，呈R形。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Ra** | R Permutation a | R U R' F' R U R' U' R' F R2 U' R' U' |
| **Rb** | R Permutation b | R' U2 R U2 R' F R U R' U' R' F' R2 U' |

### T Permutation
**T = T型交换**

呈T字形的交换模式。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **T** | T Permutation | R U R' U' R' F R2 U' R' U' R U R' F' |

---

## 相邻角 + 对棱

### J Permutation
**J = J型交换**

相邻角 + 对棱交换，呈J形。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Ja** | J Permutation a | R' U L' U2 R U' R' U2 R L |
| **Jb** | J Permutation b | R U R' F' R U R' U' R' F R2 U' R' |

### F Permutation
**F = F型交换**

呈F字形的交换模式。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **F** | F Permutation | R' U' R' F R F' U R' F R' F' R U R |

---

## 其他交换模式

### V Permutation
**V = V型交换**

呈V字形的交换模式。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **V** | V Permutation | R' U R' U' y R' F' R2 U' R' U R' F R F |

### Y Permutation
**Y = Y型交换**

呈Y字形的交换模式。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Y** | Y Permutation | F R U' R' U' R U R' F' R U R' U' R' F R F' |

### N Permutation
**N = N型大循环**

对角棱的大循环。

| 名称 | 全称含义 | 公式 |
|------|----------|------|
| **Na** | N Permutation a | R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R' |
| **Nb** | N Permutation b | R' U R U' R' F' U' F R U R' F R' F' R U' R |

---

## PLL 学习建议

### 推荐学习顺序（从易到难）

1. **Ua, Ub** - 角不动，只有棱动，最好记
2. **Z, H** - 也是棱动，公式短
3. **Aa, Ab** - 角三棱三，最常用
4. **T, J** - 常见情况
5. **R, F** - 进阶
6. **G系列 (4个)** - 稍长，最后学
7. **V, Y, N** - 不太常见，可以后学

### 记忆技巧

- 先看**角块**：角动不动？动几个？怎么动？
- 再看**棱块**：棱动不动？动几个？怎么动？
- 记住每个字母的典型模式
- 肌肉记忆比背公式更重要

---

**文件位置：** `formulas/pll-cases/PLL公式详解.md`
**关联：** `knowledge/魔方术语表.md` → 查看PLL命名规则