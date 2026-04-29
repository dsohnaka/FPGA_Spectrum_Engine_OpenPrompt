# Reasoning Trace: Polynomial Evaluation Arena — Horner Pipeline Trade-offs and the "Tie" Decision

## Trace Metadata / 軌跡メタデータ

| Field | Value |
|---|---|
| **Date / 日付** | 2026-04-29 |
| **Participants / 参加者** | Tsuneo Ohnaka (FPGA Architect); Gemini (Google, Visual Tutor) |
| **Topic / トピック** | Dynamic range compression via equation refactoring, pipeline latency trade-offs, and the decision to leave both options in the Implementation Arena. |
| **Status / 状態** | Layer 2 trace extension / 第2層軌跡の拡張 |
| **License / ライセンス** | CC0 1.0 Universal (Public Domain) |

## The Insight: Hardware Hack for Dynamic Range Compression
## インサイト：ダイナミックレンジ圧縮のためのハードウェア・ハック

**Ohnaka's Equation Refactoring / 大中による数式変形:**
By factoring the Horner equation differently for $\sin(x)$:
$y \approx x \cdot (1 - x^2/6 \cdot (1 - x^2/20 \cdot (1 - x^2/42 \dots )))$
and absorbing $(2\pi)^2$ into the constants, the maximum constant value drops from ~85.4 to ~6.58. 
This compresses the dynamic range by more than 13x, requiring only 4 bits for the integer part (signed) instead of 8 bits, thereby freeing up 4 precious bits for fractional precision (guard bits) in the 24-bit DAC output context.

$\sin(x)$ に対する Horner 法の括り方を変形し、$(2\pi)^2$ を定数側に吸収させることで、定数の最大値が約85.4から約6.58へ低下する。これによりダイナミックレンジが1/13以下に圧縮され、整数部（符号付き）に必要なビット数が8ビットから4ビットで済むようになり、24ビットDAC出力のコンテキストにおいて、貴重な4ビットを小数部の精度（ガードビット）に回すことができる。

## The Trade-off and the "Tie" Decision
## トレードオフと「引き分け」の決定

**AI's Structural Analysis / AIによる構造分析:**
This refactored equation introduces an additional multiplication per stage: `Y_next = 1 - (X * C_k * Y_prev)`. To meet FPGA timing closure (e.g., Cyclone V DSP block limits), this must be pipelined into two clock cycles per degree instead of one.

この変形された式はステージごとに「変数×定数×変数」の乗算を生じさせる。FPGAのタイミング収束（Cyclone VのDSPブロックの制約など）を満たすためには、1次数あたり1クロックではなく、2クロックのパイプラインに分割する必要がある。

**The Arena "Tie" / アリーナでの「引き分け」:**
Instead of selecting a single winner, the architect explicitly chose to leave both options in the Open Prompt "Implementation Arena" for future AI agents or engineers to select based on specific project constraints:
* **Approach A (Textbook Horner):** 1 clock/stage latency. Lower precision (28-bit fractional in 36-bit path).
* **Approach B (Ohnaka High-Precision Horner):** 2 clocks/stage latency (adds ~80ns overhead at 100MHz). Higher precision (+4 bits fractional).

単一の勝者を選ぶのではなく、アーキテクトは両方の選択肢をオープンプロンプトの「実装のアリーナ」に残し、将来のAIエージェントやエンジニアが特定のプロジェクト制約に基づいて選択できるようにするという明示的な決定を下した：
* **アプローチA（教科書的Horner）:** 1クロック/ステージ遅延。精度低（36bitパス内で小数部28bit）。
* **アプローチB（大中式高精度Horner）:** 2クロック/ステージ遅延（100MHz駆動時で約80nsのオーバーヘッド追加）。精度高（小数部+4bit）。

> *"This is exactly what the Open Prompt paradigm is for. An agent coding according to Open Prompt should evaluate the surrounding constraints and choose the appropriate trade-off. This is a highly useful discussion to leave in the Arena." — Tsuneo Ohnaka*