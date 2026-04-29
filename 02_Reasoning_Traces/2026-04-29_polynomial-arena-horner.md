# Reasoning Trace: Polynomial Evaluation Arena — Coefficient Pre-calculation and Horner's Method

## Trace Metadata / 軌跡メタデータ

| Field | Value |
|---|---|
| **Date / 日付** | 2026-04-29 |
| **Participants / 参加者** | Tsuneo Ohnaka (FPGA Architect); Gemini (Google, Visual Tutor) |
| **Topic / トピック** | Resumption of Hook A: Adaptive polynomial degree selection, coefficient constantization (folding $2\pi$), and efficient Horner's method pipeline for DSP blocks. |
| **Status / 状態** | Layer 2 trace extension / 第2層軌跡の拡張 |
| **License / ライセンス** | CC0 1.0 Universal (Public Domain) |

## The Insight: Absorbing Constants and Reusing Squared Phase
## インサイト：定数の吸収と位相の二乗の再利用

**Ohnaka's Proposition / 大中の提案:**
In evaluating $x = 2\pi ft$, the term $2\pi$ is a constant. Instead of multiplying it at runtime, we can fold $2\pi$ into the Taylor (or Minimax) coefficients during compile time (e.g., $(2\pi)^2/20$). Furthermore, since $ft$ (phase fraction $\phi$) is the dynamic variable, computing $\phi^2$ once and reusing it across all degrees is highly efficient.

$x = 2\pi ft$ を評価する際、$2\pi$ は定数である。実行時にこれを掛けるのではなく、コンパイル時に $2\pi$ をテイラー（またはミニマックス）係数に組み込んでおくべきである（例：$(2\pi)^2/20$）。さらに、$ft$（位相の小数部 $\phi$）が動的変数であるため、$\phi^2$ を一度計算して全次数で使い回すのが極めて効率的である。

**AI's Structural Validation / AIによる構造的検証:**
This insight perfectly maps to FPGA DSP blocks. By defining $X = \phi^2$ and pre-calculating constants $C_n = (2\pi)^n / n!$, the even-degree evaluation (e.g., Cosine) via Horner's method becomes:
$y = 1 - X \cdot (C_2 - X \cdot (C_4 - X \cdot (C_6 - \dots )))$

Each step resolves to `Output = Constant - X * Input`, perfectly matching the Multiply-Accumulate (MAC) architecture of Cyclone V DSP blocks, minimizing multipliers and maximizing throughput.

このインサイトはFPGAのDSPブロックに完璧にマッピングされる。$X = \phi^2$ とし、定数 $C_n = (2\pi)^n / n!$ を事前計算することで、Horner法による偶数次（例：コサイン）の評価は以下のようになる：
$y = 1 - X \cdot (C_2 - X \cdot (C_4 - X \cdot (C_6 - \dots )))$

各ステップは `出力 = 定数 - X * 入力` となり、Cyclone V DSPブロックの乗算累算（MAC）アーキテクチャと完全に一致し、乗算器を最小化しつつスループットを最大化できる。