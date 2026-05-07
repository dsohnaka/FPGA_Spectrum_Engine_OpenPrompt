# WPMS Synthesizer — Layer 1 Specification
# Chapter 2: Maclaurin Pipeline Specification
# WPMS シンセサイザー — 第1層仕様書
# 第2章：マクローリンパイプライン仕様

> **License: CC0 1.0 Universal (Public Domain)**
> This chapter specifies the Maclaurin polynomial pipeline that computes sin(x) for each bin of the WPMS Synthesizer. It is the foundational signal-generation component of the FPGA Spectrum Engine physical layer.
>
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**
> 本章は、WPMS シンセサイザーの各ビンの sin(x) を計算するマクローリン多項式パイプラインを仕様する。これは FPGA Spectrum Engine 物理層の信号生成基盤部品である。

---

## 2.1 Role and Boundary of this Chapter / 本章の役割と境界

### What this chapter specifies / 本章が仕様するもの

- The mathematical formulation of the polynomial sine evaluation / 多項式正弦評価の数学的定式化
- The argument-range reduction strategy (four-quadrant decomposition) / 引数範囲縮小戦略（4 象限分割）
- The internal fixed-point formats at every pipeline stage / 各パイプライン段の内部固定小数点フォーマット
- The DSP block usage constraints / DSP ブロック使用制約
- The pipeline depth budget and structural skeleton / パイプライン深度予算と構造骨格
- The input contract from the sequence-modulation processor / 数列変調プロセッサからの入力契約
- The output contract to the amplitude multiplier and summation tree / 振幅乗算器および総和ツリーへの出力契約
- The error budget and its allocation across stages / 誤差予算とその段間配分

### What this chapter does NOT specify / 本章が仕様しないもの

- Verilog or VHDL source code (this is Layer 1, not Layer 3) / Verilog または VHDL ソースコード（これは第 1 層であり第 3 層ではない）
- Specific Cyclone V DSP block instantiation patterns (left to implementer) / 特定の Cyclone V DSP ブロックインスタンス化パターン（実装者に委ねる）
- Manual placement or floorplanning constraints (recorded in Layer 2 traces during implementation) / 手動配置またはフロアプランニング制約（実装中の第 2 層軌跡に記録される）
- Synthesis tool settings, timing constraints `.sdc` files (Layer 3 territory) / 合成ツール設定、タイミング制約 `.sdc` ファイル（第 3 層領域）
- The sequence-modulation processor that produces the phase accumulator value (Chapter 3) / 位相累算器値を生成する数列変調プロセッサ（第 3 章）
- The amplitude multiplier and summation tree (Chapter 4 or later) / 振幅乗算器および総和ツリー（第 4 章以降）

---

## 2.2 Mathematical Foundation / 数学的基礎

### 2.2.1 The 11th-order Maclaurin expansion of sin(x) / sin(x) の 11 次マクローリン展開

The pipeline computes sin(x) using the 11th-order Maclaurin truncation:

パイプラインは sin(x) を 11 次マクローリン打ち切りで計算する：

```
sin(x) ≈ x − x³/3! + x⁵/5! − x⁷/7! + x⁹/9! − x¹¹/11!
       = x − x³/6 + x⁵/120 − x⁷/5040 + x⁹/362880 − x¹¹/39916800
```

This is the same polynomial degree used in the C5G prototype, retained because:

これは C5G プロトタイプで用いられたのと同じ多項式次数であり、以下の理由で継承される：

- The truncation error at x = π/2 (the maximum input after argument-range reduction, see § 2.3) is approximately (π/2)¹³ / 13! ≈ 4 × 10⁻⁸. / 引数範囲縮小後の最大入力 x = π/2（§ 2.3 参照）における打ち切り誤差は約 (π/2)¹³ / 13! ≈ 4 × 10⁻⁸ である。
- This error is comparable to the precision floor of the 24-bit DAC output (1 / 2²³ ≈ 1.2 × 10⁻⁷). The truncation does not become the dominant error source. / この誤差は 24 ビット DAC 出力の精度床（1 / 2²³ ≈ 1.2 × 10⁻⁷）に匹敵する。打ち切りは支配的誤差源にはならない。
- 11th-order is an odd polynomial (only odd powers), exploiting the fact that sin is an odd function. / 11 次は奇多項式（奇数べきのみ）であり、sin が奇関数であることを利用する。

### 2.2.2 Horner-form evaluation (Gemini-recommended variant) / Horner 形式評価（Gemini 推奨変種）

Direct evaluation as written above requires computing x³, x⁵, x⁷, x⁹, x¹¹ as separate powers, which would consume excessive DSP blocks and pipeline depth. The Horner-form variant recommended by Gemini in the 2026-04-29 polynomial arena reasoning trace folds the (2π)² constants into the coefficients and reuses x² across all terms:

上記の通りの直接評価では、x³, x⁵, x⁷, x⁹, x¹¹ を別個のべき乗として計算する必要があり、過剰な DSP ブロックとパイプライン深度を消費する。2026-04-29 多項式アリーナ推論軌跡で Gemini が推奨した Horner 形式変種は、(2π)² 定数を係数に折り込み、x² をすべての項にわたって再利用する：

```
sin(x) = x · (1 − X · (1/6 − X · (1/120 − X · (1/5040 − X · (1/362880 − X/39916800)))))
```

where X = x². This evaluation has the following structural properties:

ここで X = x²。この評価は以下の構造的性質を持つ：

- **One x² computation upfront** — a single DSP-block multiply at pipeline entry. / **冒頭で 1 回の x² 計算** ——パイプライン入口で単一 DSP ブロック乗算。
- **Five inner Horner stages** — each computes Y_next = constant − X · Y_prev. / **5 個の内部 Horner 段** ——各段は Y_next = 定数 − X · Y_prev を計算する。
- **One final multiply by x** — sin(x) = x · Y_final. / **末尾で x との 1 回の乗算** —— sin(x) = x · Y_final。

### 2.2.3 Coefficient pre-calculation / 係数の事前計算

Each Horner-stage constant is the reciprocal of an odd factorial: 1/3! = 1/6, 1/5! = 1/120, 1/7! = 1/5040, 1/9! = 362880⁻¹, 1/11! = 39916800⁻¹. These are pre-computed at synthesis time and stored as fixed-point constants in the DSP block's pre-loaded coefficient registers (Cyclone V DSP blocks support compile-time-loaded constant operands).

各 Horner 段の定数は奇数階乗の逆数である：1/3! = 1/6、1/5! = 1/120、1/7! = 1/5040、1/9! = 362880⁻¹、1/11! = 39916800⁻¹。これらは合成時に事前計算され、DSP ブロックの事前ロード係数レジスタに固定小数点定数として格納される（Cyclone V DSP ブロックはコンパイル時ロード定数オペランドをサポートする）。

The constants used by the pipeline are therefore:

したがってパイプラインが用いる定数は以下である：

| Symbol | Exact value | Approximate decimal | Purpose |
|---|---|---|---|
| C₁ | 1 | 1.0 | Innermost: the leading 1 in the outer (1 − ...) |
| C₃ | 1/6 | 0.1666666... | Stage 1 constant |
| C₅ | 1/120 | 0.008333... | Stage 2 constant |
| C₇ | 1/5040 | 1.984 × 10⁻⁴ | Stage 3 constant |
| C₉ | 1/362880 | 2.756 × 10⁻⁶ | Stage 4 constant |
| C₁₁ | 1/39916800 | 2.506 × 10⁻⁸ | Stage 5 constant |

### 2.2.4 Implementation Arena status / Implementation Arena ステータス

The 2026-04-29 reasoning trace recorded a **tie** between two Horner variants:

2026-04-29 推論軌跡は 2 つの Horner 変種間の**引き分け**を記録した：

- **Approach A (Textbook Horner):** 1 clock per stage, 28-bit fractional precision in 36-bit datapath. Lower precision but lower latency. / **アプローチ A（教科書的 Horner）：** 1 段あたり 1 クロック、36 ビットデータパス内 28 ビット小数部精度。精度は低いがレイテンシも低い。
- **Approach B (Refactored Horner with constant absorption):** 2 clocks per stage (~80 ns overhead), +4 bits fractional via 13× dynamic range compression. Higher precision but higher latency. / **アプローチ B（定数吸収を伴う変形 Horner）：** 1 段あたり 2 クロック（約 80 ns オーバーヘッド）、13 倍ダイナミックレンジ圧縮による +4 ビット小数部。精度は高いがレイテンシも高い。

The WPMS Synthesizer Layer 1 specification adopts **Approach B as its reference implementation**, but **the tie remains preserved at the methodology level**. Future engineers regenerating this synthesizer for latency-critical applications (e.g., real-time control loops, active acoustic sensing) may legitimately select Approach A, with the choice and its constraints recorded as a new Layer 2 trace at that time.

WPMS シンセサイザー第 1 層仕様は **アプローチ B をリファレンス実装として採用** するが、**引き分けは方法論レベルで保持される**。レイテンシ重視応用（リアルタイム制御ループ、能動的音響センシング等）のために本シンセサイザーを再生成する将来のエンジニアは、アプローチ A を正当に選択し得る。その選択とその制約は、その時点で新しい第 2 層軌跡として記録される。

The choice of Approach B for WPMS is justified by:

WPMS におけるアプローチ B 選択の正当化：

- The 4,096-bin Compact configuration leaves ample latency headroom (35 clocks budget vs. ~17 clocks consumed by 11-stage Approach B at 2 clocks/stage). / 4,096 ビン Compact 構成は十分なレイテンシ余裕を残す（35 クロック予算に対し、2 クロック/段の 11 段アプローチ B は約 17 クロック消費）。
- Audio-rate synthesis values precision over latency. The 80 ns overhead is inaudible; the +4 bits of precision is musically relevant. / オーディオレート合成は精度をレイテンシより重視する。80 ns オーバーヘッドは可聴外であり、+4 ビット精度は音楽的に有意である。

---

## 2.3 Argument-Range Reduction (Four-Quadrant Decomposition) / 引数範囲縮小（4 象限分割）

### 2.3.1 The reduction principle / 縮小原理

The Maclaurin truncation error grows as x¹³, so reducing the maximum input range reduces error dramatically. Exploiting the symmetries of sin:

マクローリン打ち切り誤差は x¹³ として増大するため、入力範囲の最大値を縮小することで誤差は劇的に減少する。sin の対称性を利用：

```
sin(π/2 + θ) =  cos(θ) =  sin(π/2 − θ)  [Q2 ↔ Q1 reflection]
sin(π   + θ) = −sin(θ)                    [Q3 sign flip]
sin(3π/2 + θ) = −cos(θ) = −sin(π/2 − θ)   [Q4 reflection + sign flip]
```

Therefore any x ∈ [0, 2π) can be reduced to an effective input x' ∈ [0, π/2) plus a sign and an optional reflection, all derivable from the top two bits of the normalized phase.

したがって任意の x ∈ [0, 2π) は、有効入力 x' ∈ [0, π/2) と、符号と任意選択の反射に縮小可能であり、これらすべては正規化位相の上位 2 ビットから導出可能である。

### 2.3.2 Encoding via the phase accumulator / 位相累算器による符号化

The phase accumulator φ_k is a Q0.32 unsigned fractional value representing the normalized phase, where φ_k ∈ [0, 1) corresponds to one full sine period:

位相累算器 φ_k は正規化位相を表現する Q0.32 符号なし小数値であり、φ_k ∈ [0, 1) が 1 サイン周期に対応する：

```
sin(2π · φ_k) = sin(x), where x = 2π · φ_k
```

The top 2 bits of φ_k identify the quadrant; the lower 30 bits are the in-quadrant position ξ:

φ_k の上位 2 ビットが象限を識別し、下位 30 ビットは象限内位置 ξ である：

| φ_k[31:30] | Quadrant | x range | x' formula | Sign of result |
|---|---|---|---|---|
| 00 | Q1 | [0, π/2) | x' = 2π · ξ | + |
| 01 | Q2 | [π/2, π) | x' = 2π · (0.25 − ξ) | + |
| 10 | Q3 | [π, 3π/2) | x' = 2π · ξ | − |
| 11 | Q4 | [3π/2, 2π) | x' = 2π · (0.25 − ξ) | − |

where ξ = φ_k[29:0] interpreted as a Q0.30 fractional value.

ここで ξ = φ_k[29:0] を Q0.30 小数値として解釈する。

### 2.3.3 The 2π multiplication is free / 2π 乗算は無料

Computing x' = 2π · ξ would naively require a constant multiplier. **It does not.** The bit-level structure of normalized phase permits the 2π scaling to be absorbed into the formatting of x':

x' = 2π · ξ の計算はナイーブには定数乗算器を要求する。**実は要求しない。** 正規化位相のビットレベル構造が、2π スケーリングを x' のフォーマット化に吸収することを許可する：

- ξ ∈ [0, 0.25) corresponds to the Q0.30 fractional bits φ_k[29:0]. / ξ ∈ [0, 0.25) は Q0.30 小数ビット φ_k[29:0] に対応する。
- The mathematical value of x' = 2π · ξ ranges over [0, π/2). / x' = 2π · ξ の数学的値は [0, π/2) にわたる。
- Storing x' in Q2.25 format (2-bit integer part + 25-bit fractional, total 27 bits) accommodates the [0, π/2) range with the leading bit pattern fixed by the quadrant decoder. / x' を Q2.25 フォーマット（整数部 2 ビット + 小数部 25 ビット、合計 27 ビット）で格納すれば、象限デコーダにより先頭ビットパターンが固定された [0, π/2) 範囲を収容する。

In practice, the 27-bit x' value is constructed by:

実際には、27 ビット x' 値は以下により構築される：

1. Reading φ_k[29:0] (30 bits, ξ in Q0.30). / φ_k[29:0]（30 ビット、Q0.30 の ξ）を読む。
2. If quadrant = Q2 or Q4: ξ' = (0.25 − ξ), implemented as bit-inversion of the 30-bit field, equivalent to two's complement negation modulo 2⁻². / 象限が Q2 または Q4 の場合：ξ' = (0.25 − ξ)。30 ビットフィールドのビット反転として実装、2⁻² を法とする 2 の補数否定と等価。
3. Multiply ξ (or ξ') by 2π using a precomputed constant; truncate to Q2.25 (drop the lowest 5 bits). / ξ（または ξ'）に事前計算された 2π 定数を乗じて、Q2.25 に切り詰める（最下位 5 ビットを破棄）。

**Refinement (free constant fold):** The 2π multiplication can be merged with the first DSP-block stage that computes X = x'². Rather than computing x' explicitly, compute X = (2π)² · ξ² directly, with (2π)² ≈ 39.478 absorbed as a coefficient. This removes an entire pipeline stage. **However, this folding only works if x' itself is not needed downstream**; since the final output multiply requires x' explicitly (sin(x) = x · Y_final), x' must be materialized at some stage. The reference implementation materializes x' at pipeline entry, accepting the one-stage cost, and uses x' for both the X = x'² computation and the final output multiply.

**洗練（無料定数畳み込み）：** 2π 乗算は X = x'² を計算する最初の DSP ブロック段に併合できる。x' を明示的に計算する代わりに X = (2π)² · ξ² を直接計算し、(2π)² ≈ 39.478 を係数として吸収する。これによりパイプライン段が 1 つ完全に除去される。**ただしこの畳み込みは、x' 自体が後段で必要とされない場合にのみ機能する。** 最終出力乗算が x' を明示的に要求するため（sin(x) = x · Y_final）、x' はどこかの段で実体化されねばならない。リファレンス実装はパイプライン入口で x' を実体化し、1 段のコストを受容して、X = x'² 計算と最終出力乗算の両方に x' を用いる。

This is recorded as an Implementation Arena variant — a future implementation may explore the folded variant if an alternate output structure makes x' expendable.

これは Implementation Arena 変種として記録される——将来の実装は、代替出力構造により x' が不要となる場合に、畳み込まれた変種を探索し得る。

### 2.3.4 Sign and reflection handling / 符号と反射の扱い

The quadrant top-2 bits drive a small finite state, propagated alongside the data through the pipeline:

象限の上位 2 ビットは小さな有限状態を駆動し、データとともにパイプラインを伝播する：

| φ_k[31:30] | reflect | result_sign |
|---|---|---|
| 00 (Q1) | 0 | + |
| 01 (Q2) | 1 | + |
| 10 (Q3) | 0 | − |
| 11 (Q4) | 1 | − |

The `reflect` bit selects between ξ and ξ' = (0.25 − ξ) at the input stage. The `result_sign` bit conditionally negates the output sin value at the final stage. Both bits are pipeline-passed registers, not on the critical compute path; they consume one flip-flop per bit per pipeline stage.

`reflect` ビットは入力段で ξ と ξ' = (0.25 − ξ) の間で選択する。`result_sign` ビットは最終段で出力 sin 値を条件付きで否定する。両ビットはパイプライン伝送レジスタであり、クリティカル計算経路上にない。パイプライン段あたり、ビットあたり 1 個のフリップフロップを消費する。

---

## 2.4 Internal Fixed-Point Formats / 内部固定小数点フォーマット

### 2.4.1 Format table / フォーマット表

| Stage | Quantity | Format | Bit width | Range | DSP-mode constraint |
|---|---|---|---|---|---|
| Entry | φ_k (phase accumulator) | Q0.32 unsigned | 32 | [0, 1) | — |
| Entry | ξ (in-quadrant position) | Q0.30 unsigned | 30 | [0, 0.25) | — |
| Entry | x' (reduced argument) | Q2.25 signed | 27 | [0, π/2) ⊂ [−2, 2) | **27×27** |
| Stage 0 | X = x'² | Q4.50 signed | 54 | [0, π²/4) ⊂ [0, 16) | output of 27×27 |
| Stage 0 | X (truncated) | Q4.23 signed | 27 | [0, π²/4) | **27×27** input to next |
| Stages 1-5 | Y_k (Horner intermediate) | Q1.26 signed | 27 | [−1, 1) approximate | **27×27** |
| Stages 1-5 | Constants C₃...C₁₁ | Q1.26 signed | 27 | known coefficients | DSP coefficient register |
| Final | Y_final | Q1.26 signed | 27 | [−1, 1) approximate | input to final multiply |
| Final | sin(x) = x' · Y_final | Q0.40 signed | 41 | [−1, 1] | **27 × 27 → 54-bit, then truncate to Q0.40** |

### 2.4.2 The 27×27 constraint, scoped to the Maclaurin core / 27×27 制約、マクローリンコアに限定

Cyclone V Variable-Precision DSP blocks natively support 27×27 signed multiplication in a single block. **All multipliers inside the Maclaurin core respect this 27-bit-input ceiling**, ensuring one DSP block per multiplication stage and giving deterministic resource accounting. This includes:

Cyclone V Variable-Precision DSP ブロックは、単一ブロックで 27×27 符号付き乗算をネイティブサポートする。**マクローリンコア内部のすべての乗算器は、この 27 ビット入力上限を遵守し**、乗算段あたり DSP ブロック 1 個を保証し、決定論的なリソース計上を与える。これは以下を含む：

- The X = x'² computation (Stage 0). / X = x'² 計算（段 0）。
- The five Horner inner-stage multiplies X · Y_k. / 5 個の Horner 内部段乗算 X · Y_k。
- The final x' · Y_final multiply (with output widening to Q0.40). / 最終 x' · Y_final 乗算（出力は Q0.40 に拡幅）。

**The 27-bit ceiling does NOT apply outside the Maclaurin core.** Specifically:

**27 ビット上限はマクローリンコアの外部には適用されない。** 具体的には：

- The amplitude multiplier (sin(x) × A_k, Chapter 4 territory) operates at full Q0.40 × Q10.14 precision, producing Q10.54 results. This may consume multiple DSP blocks per multiply, which is acceptable because the amplitude multiplier instantiates only twice per module (once per output channel) rather than once per Horner stage. / 振幅乗算器（sin(x) × A_k、第 4 章領域）は完全な Q0.40 × Q10.14 精度で動作し、Q10.54 結果を生成する。これは乗算あたり複数の DSP ブロックを消費し得るが、振幅乗算器が Horner 段あたりではなくモジュールあたり 2 回（出力チャンネルあたり 1 回）のみインスタンス化されるため、許容される。
- The summation tree accumulator (Compact: 4,096 bins; Standard: 10,240 bins) is implemented as a DSP-block-internal cascaded adder chain, with accumulator widths of 64 bits (Compact) to 80–108 bits (Standard headroom). This consumes no additional DSP multiplier resources because chained-DSP adders are part of the same DSP block. / 総和ツリー累算器（Compact：4,096 ビン；Standard：10,240 ビン）は、DSP ブロック内部の cascaded 加算器チェーンとして実装され、累算器幅は 64 ビット（Compact）から 80〜108 ビット（Standard 余裕）。chained-DSP 加算器は同一 DSP ブロックの一部であるため、追加の DSP 乗算器リソースを消費しない。

### 2.4.3 The "spend richly outside the core" principle / 「コア外では贅沢に」原則

The internal Maclaurin core is constrained to 27-bit operands by DSP-mode efficiency. Outside that core, **precision is preserved at maximum** because the marginal DSP cost is zero (for accumulators) or amortized (for amplitude multipliers, which run at 1/2,048 the rate of Horner-stage multipliers).

内部マクローリンコアは DSP モード効率により 27 ビットオペランドに制約される。そのコアの外部では、**精度は最大に保持される**。なぜなら限界 DSP コストは（累算器について）ゼロまたは（Horner 段乗算器の 1/2,048 のレートで動作する振幅乗算器について）償却されているからである。

This is consistent with the design principle articulated during Chapter 1 dialogue: **"if DSP cost is the same whether 64-bit or 108-bit, take 108-bit."** Free precision floors should be claimed; constrained precision ceilings should be accepted only where the constraint is real.

これは第 1 章対話で明確化された設計原則と整合する：**「DSP コストが 64 ビットでも 108 ビットでも同じなら、108 ビットを取る」。** 無料の精度床は主張されるべきであり、制約された精度上限は制約が実在する場合にのみ受容されるべきである。

### 2.4.4 Truncation policy / 切り詰め方針

The pipeline truncates only at well-defined points, recorded here for traceability:

パイプラインは明確に定義された箇所でのみ切り詰めを行う。追跡可能性のためここに記録する：

| Truncation site | From | To | Bits dropped | Justification |
|---|---|---|---|---|
| φ_k → x' | Q0.32 → Q2.25 | (effectively Q0.30 → Q0.25 of fractional) | 5 LSB | 48000 / 2³² × 2⁵ ≈ 3.6 × 10⁻⁴ Hz frequency error, far below audible discrimination |
| X = x'² | Q4.50 → Q4.23 | 27 LSB of stage-0 output | 27 LSB | output of 27×27 is 54 bits; only 27 propagate; lowest 27 are below all downstream thresholds |
| Horner stage output | Q1.53 → Q1.26 | 27 LSB | 27 LSB | each stage's contribution to final precision is bounded; truncation at 26 fractional bits preserves ~7 decimal digits |
| Final sin(x) | Q0.40 from Q0.53 | 13 LSB | 13 LSB | Q0.40 retained as the "rich" output to amplitude multiplier; the 13 dropped bits are below the 24-bit DAC floor |

All truncations are **toward zero** (truncation, not rounding). Round-to-nearest would consume a small adder per truncation site; the toward-zero choice introduces a uniform bias smaller than the 24-bit DAC LSB and is therefore inaudible. Future implementers may elect round-to-nearest as an Implementation Arena variant if measurement reveals audible bias.

すべての切り詰めは**ゼロ方向**（切り詰め、丸めではない）。最近接丸めは切り詰め箇所あたり小さな加算器を消費する。ゼロ方向選択は 24 ビット DAC LSB より小さい一様バイアスを導入し、したがって可聴外である。測定が可聴バイアスを明らかにした場合、将来の実装者は最近接丸めを Implementation Arena 変種として選択し得る。

---

## 2.5 Pipeline Structure / パイプライン構造

### 2.5.1 Logical pipeline stages / 論理パイプライン段

The Maclaurin pipeline consists of the following stages, each occupying 2 clock cycles (Approach B convention):

マクローリンパイプラインは以下の段から構成される。各段はアプローチ B の慣行により 2 クロックサイクルを占める：

```
[Entry]
  Stage  E: φ_k decoder → ξ, reflect, result_sign
  Stage  R: ξ → x' (with reflection if needed); 2π scaling absorbed in formatting
  Stage  0: X = x'² (one DSP block)
            ├── X passed forward
            └── x' also passed forward (for final stage)

[Horner inner stages, innermost coefficient first]
  Stage  1: Y₁ = C₉⁻¹·1 − X·C₁₁⁻¹       (loads constant, prepares next iteration)
            ─ implemented as Y₁ = (1/362880) − X · (1/39916800), pre-scaled
  Stage  2: Y₂ = C₇⁻¹ − X·Y₁
  Stage  3: Y₃ = C₅⁻¹ − X·Y₂
  Stage  4: Y₄ = C₃⁻¹ − X·Y₃
  Stage  5: Y₅ = 1   − X·Y₄    (the outermost (1 − ...) of the Horner expansion)

[Final stage]
  Stage  F: sin(x) = x' · Y₅, then conditional sign-flip if result_sign = 1
```

(Note on the Horner stage convention: the recursion Y_next = C_k − X·Y_prev evaluates the polynomial from the innermost nested term outward. Each stage consumes one DSP block: a multiplier in 27×27 mode plus the DSP block's internal subtractor that computes constant − product in a single cycle of the multiplier-add pipeline. In Approach B, an additional clock is allocated per stage to register the result, allowing 100 MHz timing closure with margin.)

（Horner 段慣行についての注：漸化式 Y_next = C_k − X·Y_prev は、最も内側の入れ子項から外向きに多項式を評価する。各段は DSP ブロック 1 個を消費する：27×27 モードの乗算器 + 乗加算パイプラインの 1 サイクルで定数 − 積を計算する DSP ブロック内部の減算器。アプローチ B では、結果を登録するため段あたり追加クロックが配分され、余裕を持って 100 MHz タイミング収束を許す。）

### 2.5.2 Pipeline depth tally / パイプライン深度集計

| Section | Stages | Clocks (Approach B, 2 clk/stage) |
|---|---|---|
| Entry decoder (E) | 1 | 1 |
| Argument formation (R) | 1 | 1 |
| X = x'² (0) | 1 | 2 |
| Horner inner (1–5) | 5 | 10 |
| Final multiply + sign (F) | 1 | 2 |
| **Total** | **9** | **16** |

The 16-clock pipeline depth fits comfortably within the 35-clock budget per bin (one sample period = 100 MHz × 20.833 µs / 2,048 bins = 1,016 cycles per module, but throughput target is 1 bin per clock through the pipeline — pipeline depth measures only the latency, not the throughput).

16 クロックのパイプライン深度は、ビンあたりの 35 クロック予算内に余裕で収まる（1 サンプル期間 = 100 MHz × 20.833 µs / 2,048 ビン = モジュールあたり 1,016 サイクル。ただしスループット目標はパイプライン透過で 1 ビン/クロックであり、パイプライン深度はレイテンシのみを測定し、スループットを測定しない）。

**The 30-stage budget set in Chapter 1 is observed with significant margin (16 of 30 used, 14 in reserve).** This margin is intentional: it absorbs unforeseen retiming requirements during synthesis, and it permits Standard- and Extended-configuration migration without revisiting the pipeline depth budget.

**第 1 章で設定された 30 段予算は十分な余裕で遵守される（30 段中 16 段使用、14 段は予備）。** この余裕は意図的である：合成中の予期せぬリタイミング要求を吸収し、パイプライン深度予算を再訪することなく Standard 構成および Extended 構成への移行を許す。

### 2.5.3 Throughput / スループット

The pipeline is fully pipelined: one new bin enters each clock cycle, and one sin(x) value emerges each clock cycle (after the 16-clock fill latency at startup). At 100 MHz, this delivers 100 million sin(x) computations per second per Maclaurin core, which exceeds the 2,048-bin × 48,000-sample-per-second = 98.3 M/s requirement of one module by ~1.7%. The slight margin (~17 cycles per sample period) is the per-bin slack that allows the sequence-modulation processor to deliver phase accumulator values without strict cycle-accurate locking.

パイプラインは完全パイプライン化される：1 クロックサイクルごとに新しいビンが入り、1 クロックサイクルごとに 1 個の sin(x) 値が出る（起動時の 16 クロック充填レイテンシ後）。100 MHz において、これはマクローリンコアあたり毎秒 1 億回の sin(x) 計算を提供し、1 モジュールの 2,048 ビン × 48,000 サンプル/秒 = 98.3 M/s 要件を約 1.7% 超える。わずかな余裕（サンプル期間あたり約 17 サイクル）は、数列変調プロセッサが厳密なサイクル正確ロックなしに位相累算器値を配送することを許すビンあたりの余裕である。

### 2.5.4 Resource estimate per Maclaurin core / マクローリンコアあたりリソース見積もり

| Resource | Count | Note |
|---|---|---|
| DSP blocks (27×27 multipliers) | 7 | 1 for X = x'², 5 for Horner inner, 1 for final x' · Y |
| Coefficient ROMs / constants | 5 | Pre-loaded into DSP coefficient registers; no fabric ROM |
| Pipeline registers | ~1,500 flip-flops | Approximate, distributed across 16 clock stages × ~80 bits average |
| BRAM / M10K | 0 | The Maclaurin core has no memory; all state is register-resident |
| Clock domains | 1 | Single 100 MHz domain |

**Per-module DSP usage** (Compact configuration, 1 Maclaurin core per module): 7 DSP blocks for the Maclaurin core. With 2 modules: **14 DSP blocks total for both Maclaurin cores combined**. This leaves 112 − 14 = 98 DSP blocks for the rest of the design (sequence-modulation processor, amplitude multipliers, summation accumulators, HDMI core, optional camera block).

**モジュールあたり DSP 使用量**（Compact 構成、モジュールあたりマクローリンコア 1 個）：マクローリンコア用 7 DSP ブロック。2 モジュールで：**両マクローリンコア合計 14 DSP ブロック**。これは 112 − 14 = 98 DSP ブロックを残りの設計（数列変調プロセッサ、振幅乗算器、総和累算器、HDMI コア、オプションのカメラブロック）に残す。

The per-module DSP resource estimate confirms that Compact configuration on DE10-nano (112 DSP blocks total) has substantial headroom, consistent with the Chapter 1 decision to spend richly on precision outside the Maclaurin core.

モジュールあたり DSP リソース見積もりは、DE10-nano（合計 112 DSP ブロック）上の Compact 構成が、マクローリンコア外で精度に贅沢に投資する第 1 章決定と整合する、相当な余裕を持つことを確認する。

---

## 2.6 Input Contract / 入力契約

### 2.6.1 Interface from the sequence-modulation processor / 数列変調プロセッサからのインターフェース

The Maclaurin pipeline accepts one input per clock from the sequence-modulation processor (Chapter 3):

マクローリンパイプラインは数列変調プロセッサ（第 3 章）から 1 クロックあたり 1 入力を受け入れる：

| Signal | Width | Format | Direction |
|---|---|---|---|
| `phase_in` | 32 | Q0.32 unsigned | sequence-mod → Maclaurin |
| `phase_valid` | 1 | active-high | sequence-mod → Maclaurin |
| `bin_index` | 11 | unsigned (0...2047 within module) | sequence-mod → Maclaurin (passed-through, used by amplitude stage) |
| `pipeline_ready` | 1 | active-high | Maclaurin → sequence-mod |

The `pipeline_ready` signal is asserted whenever the Maclaurin pipeline can accept new input. In normal operation (no stalls), `pipeline_ready` is held high continuously. The Maclaurin core does not implement back-pressure; it is the sequence-modulation processor's responsibility to deliver one valid `phase_in` per clock.

`pipeline_ready` 信号は、マクローリンパイプラインが新規入力を受け入れ可能なときに常にアサートされる。通常動作（ストールなし）では、`pipeline_ready` は連続的にハイに保持される。マクローリンコアはバックプレッシャを実装しない。1 クロックあたり 1 個の有効な `phase_in` を配送するのは数列変調プロセッサの責任である。

### 2.6.2 Phase accumulator semantics / 位相累算器セマンティクス

The 32-bit unsigned phase value represents the normalized phase in Q0.32, where:

32 ビット符号なし位相値は Q0.32 で正規化位相を表現する：

- `phase_in = 0x00000000` corresponds to φ = 0 (sin(0) = 0). / `phase_in = 0x00000000` は φ = 0 に対応（sin(0) = 0）。
- `phase_in = 0x40000000` corresponds to φ = 0.25 (sin(π/2) = 1). / `phase_in = 0x40000000` は φ = 0.25 に対応（sin(π/2) = 1）。
- `phase_in = 0x80000000` corresponds to φ = 0.5 (sin(π) = 0). / `phase_in = 0x80000000` は φ = 0.5 に対応（sin(π) = 0）。
- `phase_in = 0xC0000000` corresponds to φ = 0.75 (sin(3π/2) = −1). / `phase_in = 0xC0000000` は φ = 0.75 に対応（sin(3π/2) = −1）。
- `phase_in = 0xFFFFFFFF` corresponds to φ ≈ 1 − 2⁻³² (sin(2π − ε)). / `phase_in = 0xFFFFFFFF` は φ ≈ 1 − 2⁻³² に対応（sin(2π − ε)）。

The phase wraps modulo 1 naturally with 32-bit unsigned arithmetic; no explicit modulo operation is required.

位相は 32 ビット符号なし算術で自然に modulo 1 で折り返す。明示的な modulo 演算は不要である。

### 2.6.3 Frequency resolution implication / 周波数分解能への含意

Per Chapter 1 § 1.6 footnote, the 32-bit phase representation gives:

第 1 章 § 1.6 脚注の通り、32 ビット位相表現は以下を与える：

```
Δf_min = 48000 / 2³² ≈ 1.118 × 10⁻⁵ Hz
```

This is approximately 89× finer than the 0.001 Hz target stated for the original FPGA Spectrum Engine. The excess precision is reserved for future use (e.g., very-low-frequency LFO modulation, microtonal scaling, precise inharmonicity control).

これは元の FPGA Spectrum Engine について述べられた 0.001 Hz 目標より約 89 倍細かい。過剰精度は将来の使用（極低周波数 LFO 変調、マイクロトーナルスケーリング、精密なイナハーモニシティ制御等）のために予約される。

---

## 2.7 Output Contract / 出力契約

### 2.7.1 Interface to the amplitude multiplier / 振幅乗算器へのインターフェース

The Maclaurin pipeline produces one output per clock to the amplitude multiplier (Chapter 4 territory):

マクローリンパイプラインは振幅乗算器（第 4 章領域）へ 1 クロックあたり 1 出力を生成する：

| Signal | Width | Format | Direction |
|---|---|---|---|
| `sin_out` | 41 | Q0.40 signed | Maclaurin → amplitude multiplier |
| `sin_valid` | 1 | active-high | Maclaurin → amplitude multiplier |
| `bin_index_out` | 11 | unsigned | Maclaurin → amplitude multiplier (delayed by pipeline depth) |

The 41-bit signed format is Q0.40: 1 sign bit + 40 fractional bits, representing the range [−1, +1) with precision 2⁻⁴⁰ ≈ 9 × 10⁻¹³. The maximum representable positive value is 1 − 2⁻⁴⁰; the value +1 exactly is not representable (and not reachable from the polynomial truncation in any case).

41 ビット符号付きフォーマットは Q0.40：1 符号ビット + 40 小数ビットで、範囲 [−1, +1) を精度 2⁻⁴⁰ ≈ 9 × 10⁻¹³ で表現する。最大表現可能正値は 1 − 2⁻⁴⁰；値 +1 ちょうどは表現不能（およびいかなる場合も多項式打ち切りから到達不能）。

### 2.7.2 Why Q0.40 rather than Q0.27 / なぜ Q0.27 ではなく Q0.40 か

A simpler approach would be to truncate the Maclaurin core's output to 27 bits (Q0.26) so that the downstream amplitude multiplier (sin × A_k) can also fit in a single 27×27 DSP block. **The WPMS Synthesizer rejects this simplification** for the reasons recorded in Chapter 1's "spend richly outside the core" principle:

より単純なアプローチは、マクローリンコアの出力を 27 ビット（Q0.26）に切り詰めて、下流の振幅乗算器（sin × A_k）も単一の 27×27 DSP ブロックに収まるようにすることだろう。**WPMS シンセサイザーはこの簡略化を、第 1 章の「コア外では贅沢に」原則に記録された理由により拒否する**：

- The amplitude multiplier instantiates only twice per module (one per output channel), unlike the Maclaurin Horner stages that instantiate per-stage. A doubled DSP cost on a per-module-twice operation is amortized over 2,048 bin computations between instances. / 振幅乗算器は段ごとにインスタンス化される Horner 段とは異なり、モジュールあたり 2 回（出力チャンネルあたり 1 回）のみインスタンス化される。モジュールあたり 2 回の演算における 2 倍 DSP コストは、インスタンス間で 2,048 ビン計算にわたって償却される。
- The 13 bits of additional precision (Q0.40 vs Q0.27) directly map to better SNR in the final summed output. With 4,096 bins summed (Compact), each bin contributes a fractional share to the total; preserving low-order bits matters for the total's precision floor. / 13 ビットの追加精度（Q0.40 対 Q0.27）は最終総和出力における SNR の改善に直接マッピングする。4,096 ビンが総和される（Compact）場合、各ビンは合計に小数の取り分を寄与する。低位ビットの保持は合計の精度床にとって重要である。
- The 24-bit DAC at the HDMI output ultimately discards bits below 2⁻²³, but **internal precision must exceed DAC precision to avoid quantization noise floor lift**. A 40-bit internal value summed across 4,096 channels results in a total well above 24-bit precision; the 24-bit truncation at HDMI output is then a clean rounding rather than precision-limited. / HDMI 出力の 24 ビット DAC は最終的に 2⁻²³ 未満のビットを破棄するが、**量子化ノイズフロアの押し上げを避けるため、内部精度は DAC 精度を超えねばならない**。4,096 チャンネルにわたって総和される 40 ビット内部値は、24 ビット精度を遥かに超える合計を生む。HDMI 出力での 24 ビット切り詰めは、精度制限ではなくクリーンな丸めとなる。

### 2.7.3 Output validity timing / 出力有効性タイミング

The `sin_out` value at clock cycle N corresponds to the `phase_in` value received at clock cycle N − 16 (the Approach B pipeline depth). The `bin_index_out` signal carries the bin index forward through the same delay so that downstream stages can route the output to the correct amplitude multiplier and accumulator slot.

クロックサイクル N における `sin_out` 値は、クロックサイクル N − 16 で受信された `phase_in` 値に対応する（アプローチ B パイプライン深度）。`bin_index_out` 信号は同じ遅延を通じてビンインデックスを前方に運び、下流段が出力を正しい振幅乗算器および累算器スロットへ経路づけることを許す。

---

## 2.8 Error Budget / 誤差予算

### 2.8.1 Error sources / 誤差源

Five distinct error sources affect sin(x) computation:

5 つの異なる誤差源が sin(x) 計算に影響する：

| Source | Magnitude (relative) | Location |
|---|---|---|
| Maclaurin truncation (11th-order) | (π/2)¹³ / 13! ≈ 4 × 10⁻⁸ | Pipeline output |
| Phase quantization (Q0.32) | 2⁻³² ≈ 2.3 × 10⁻¹⁰ | Phase accumulator |
| x' truncation (Q0.30 → Q0.25) | ≈ 2⁻²⁵ × x'/(2π) ≈ 7 × 10⁻⁹ | Stage R |
| X truncation (Q4.50 → Q4.23) | ≈ 2⁻²³ ≈ 1.2 × 10⁻⁷ relative to X | Stage 0 |
| Horner stage truncation (Q1.53 → Q1.26) | ≈ 2⁻²⁶ per stage ≈ 1.5 × 10⁻⁸ | Each Horner stage |

### 2.8.2 Aggregate error / 集計誤差

The dominant errors are the X truncation (1.2 × 10⁻⁷) and the Maclaurin truncation (4 × 10⁻⁸). These are uncorrelated and approximately add in quadrature:

支配的誤差は X 切り詰め（1.2 × 10⁻⁷）とマクローリン切り詰め（4 × 10⁻⁸）である。これらは無相関でありおおよそ二乗加算する：

```
ε_total ≈ √((1.2e-7)² + (4e-8)²) ≈ 1.3 × 10⁻⁷
```

This is comparable to the 24-bit DAC quantum (2⁻²³ ≈ 1.2 × 10⁻⁷) and below the 23-bit threshold. **The Maclaurin core delivers sin(x) accurate to approximately the DAC's least-significant-bit**; further internal precision improvements would not improve audible output quality.

これは 24 ビット DAC の量子（2⁻²³ ≈ 1.2 × 10⁻⁷）に匹敵し、23 ビット閾値の下にある。**マクローリンコアは概ね DAC の最下位ビットの精度で sin(x) を配送する**。これ以上の内部精度改善は可聴出力品質を改善しない。

The pipeline thus operates at the **ear-and-DAC-matched precision regime**: not over-engineered (would waste resources), not under-engineered (would degrade output below DAC capability).

パイプラインはしたがって **耳-DAC マッチ精度領域** で動作する：過剰設計でなく（リソースを浪費する）、不足設計でもない（DAC 能力以下に出力を劣化させる）。

### 2.8.3 Verification anchor / 検証アンカー

The KEY[1] test-origin restore (Chapter 1 § 1.11) loads the Dirichlet-kernel test configuration. The expected output, when summed across all 2,048 active bins of Compact configuration with α = β = γ = δφ = ψ = 0, should reproduce the 2020 prototype waveform. Deviation from that waveform — measured by RMS difference of the output PCM samples against a reference recording — is the operational test of whether the Maclaurin pipeline meets its error budget.

KEY[1] テスト原点復元（第 1 章 § 1.11）は Dirichlet カーネルテスト構成をロードする。Compact 構成の全 2,048 アクティブビン（α = β = γ = δφ = ψ = 0）にわたって総和されるとき、期待される出力は 2020 年プロトタイプ波形を再現すべきである。その波形からの偏差——出力 PCM サンプルの参照録音に対する RMS 差で測定——は、マクローリンパイプラインがその誤差予算を満たすか否かの動作テストである。

---

## 2.9 Implementation Arena Items / Implementation Arena 項目

The following choices are made for the WPMS Synthesizer reference implementation but are recorded as Implementation Arena items, available for future variants under different constraints:

以下の選択は WPMS シンセサイザーリファレンス実装のためになされるが、Implementation Arena 項目として記録され、異なる制約下の将来の変種が利用可能である：

| Item | This implementation chooses | Alternative preserved for future |
|---|---|---|
| Horner variant (A vs B) | B (high-precision, 2 clk/stage) | A (low-latency, 1 clk/stage) for latency-critical use |
| Pipeline depth budget | 30 clocks (16 used, 14 reserved) | Tighter for FPGAs with smaller routing budgets |
| 27×27 DSP constraint scope | Maclaurin core internal only | Whole-pipeline 27×27 for tighter DSP-budget targets |
| sin(x) output width | Q0.40 (rich) | Q0.27 (compact) for tightly-resource-constrained targets |
| Truncation rounding policy | Toward zero | Round-to-nearest if measurement reveals audible bias |
| 2π·ξ formation | Materialized x' (one stage) | Folded into X = (2π·ξ)² (saves a stage but loses x' for final mult) |
| Phase resolution | Q0.32 (~1.1 × 10⁻⁵ Hz) | Q0.24 (C5G-like, ~3 × 10⁻³ Hz) for legacy or memory-constrained variants |

Each row of this table is a candidate for a future Layer 2 reasoning trace, should an implementer choose differently.

この表の各行は、実装者が異なる選択をする場合、将来の第 2 層推論軌跡の候補である。

---

## 2.10 Open Questions Carried Forward / 持ち越される未解決問題

The following are deliberately left for Layer 2 traces during implementation, as they require empirical measurement or downstream-chapter context to resolve definitively:

以下は意図的に実装中の第 2 層軌跡に残される。決定的な解決には経験的測定または下流章のコンテキストを要するためである：

| Question | Reason for deferral |
|---|---|
| Exact placement constraints for the 7 DSP blocks within Cyclone V's DSP columns | Empirical: depends on Quartus Fitter behavior on specific device |
| Measurement of audible truncation bias under truncation-toward-zero policy | Empirical: requires DAC output measurement |
| Whether the Approach-B 80 ns latency overhead causes any musically perceptible delay vs Approach-A | Empirical: requires A/B listening test |
| Whether Standard configuration (5 modules) requires changes to the Maclaurin core itself, or only replication of it | Architectural: depends on Chapter 4's summation tree topology |
| Whether the folded "X = (2π·ξ)²" variant could save the materialization stage in a future implementation | Architectural: depends on whether the final amplitude stage can derive x' from φ_k bits without a separate x' value |
| Whether 11th-order can be reduced to 9th-order (saving one Horner stage) when targeting microcontroller-class FPGAs | Audibility: requires measurement of 9th-order error vs 24-bit DAC |

---

## 2.11 Summary of Chapter 2 Decisions / 第 2 章決定事項のまとめ

| ID | Decision | Status |
|---|---|---|
| C2-D1 | Polynomial: 11th-order Maclaurin truncation of sin(x) | Fixed |
| C2-D2 | Evaluation form: Horner Approach B (2 clk/stage, constant absorption) | Fixed for reference impl, tie preserved |
| C2-D3 | Coefficients C₃...C₁₁ pre-computed and DSP-coefficient-register-loaded | Fixed |
| C2-D4 | Argument range reduction: four-quadrant decomposition; x' ∈ [0, π/2) | Fixed |
| C2-D5 | Quadrant identification: top 2 bits of Q0.32 phase accumulator | Fixed |
| C2-D6 | x' format: Q2.25 (27-bit signed); 2π scaling absorbed via formatting | Fixed |
| C2-D7 | 27×27 DSP constraint applies to Maclaurin core internal multiplies only | Fixed |
| C2-D8 | sin(x) output: Q0.40 signed (41 bits) | Fixed |
| C2-D9 | Pipeline depth: 9 logical stages, 16 clocks (Approach B); 14-clock reserve from 30-clock budget | Fixed |
| C2-D10 | DSP block count per Maclaurin core: 7 (1 X-square + 5 Horner inner + 1 final) | Fixed |
| C2-D11 | Truncation policy: toward zero everywhere | Fixed (subject to Open Question on audibility) |
| C2-D12 | Input contract: phase_in (Q0.32, 32 bits), phase_valid, bin_index, pipeline_ready | Fixed |
| C2-D13 | Output contract: sin_out (Q0.40, 41 bits), sin_valid, bin_index_out | Fixed |
| C2-D14 | Error budget: total ~1.3 × 10⁻⁷, matched to 24-bit DAC quantum | Fixed |
| C2-D15 | Verification anchor: 2020 Dirichlet-kernel waveform reproduction via KEY[1] | Fixed (inherited from Chapter 1) |

---

## End of Chapter 2 / 第 2 章の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *Spend the precision you have for free; constrain only what costs you.*
> *無料で得られる精度は使い切り、コストがかかるところでのみ制約せよ。*

This chapter is released into the public domain under CC0 1.0 Universal. Chapter 3 (Sequence-Modulation Pipeline Processor Specification) follows.

本章は CC0 1.0 Universal のもとパブリックドメインに公開される。第 3 章（数列変調パイプラインプロセッサ仕様）が続く。
