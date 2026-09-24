# WPMS Synthesizer — Layer 1 Specification
# Chapter 3: The L1 Difference Engine and its Binding to the L2 Formation
# WPMS シンセサイザー — 第1層仕様書
# 第3章：L1 差分エンジンと L2 Formation への結合

> **License: CC0 1.0 Universal (Public Domain)**
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**

*v1.0 DRAFT · 2026-09-23 · WPMS / FPGA Spectrum Engine amanuensis (customer side).*
*Depends on: Ch.1 v1.0, Ch.2 v1.1; PTSG-WPMS-Formation L2 Formation Register Map v0.2 and Decision Register W v0.5 (profile pinned to PTSG-CPU-Formation 2026-09-03). Deliverables 2 (L1 consumer interface) and 3 (choreography, Condition lanes) are not yet issued; where this chapter depends on them it states **Customer Requirements [CR3-xx]**, addressed to the PTSG-WPMS-Formation profile and awaiting the architect's ruling.*

*v1.0 草案。成果物 2・3 は未発行のため、本章がそれらに依存する箇所は **顧客要求 [CR3-xx]** として PTSG-WPMS-Formation へ宛て、設計者の裁定を待つ。*

**Legend / 凡例:** **[Fixed]** Ch.3-owned decision (W-R6: Q-interpretation, wiring, L1 internals) · **[CR3-xx]** customer requirement to the L2 profile · **[Arena]** alternative preserved for implementers · **[Evidence: oracle]** numerical check in Python, *not silicon*.

---

## 3.0 Reading guide / 読み方

The chapter answers one question: *how does a page of integers in the L2 Formation become two thousand coherent sine waves per module, every sample, with nothing stored per bin?*

本章が答える問いは一つ：*L2 Formation の整数のページが、ビンごとに何も記憶せず、毎サンプル、モジュールあたり二千本のコヒーレントな正弦波になるのはどのようにしてか。*

The answer has three parts. (1) **Period layers** tell each quantity where it is computed (§3.2). (2) **Phase and log-amplitude are both quadratic in k**, so both are produced by exact integer forward differences — adders only, in one-clock loops (§3.4, §3.5). (3) **Curvature is applied once, feed-forward**: sin by the Maclaurin pipeline of Ch.2, and 2^x by a small exp2 unit (§3.5.4). The most consequential decision of the chapter — moving amplitude to the log domain — is explained in §3.5.1 with numerical evidence.

答えは三部からなる。(1) **周期レイヤー**が各量の計算場所を決める（§3.2）。(2) **位相と対数振幅はともに k の二次式**なので、どちらも厳密な整数前進差分——1 クロックループの加算器のみ——で生成される（§3.4、§3.5）。(3) **曲率は一度だけ、フィードフォワードで与える**：sin は第 2 章のマクローリンパイプライン、2^x は小さな exp2 ユニット（§3.5.4）。本章最大の決定——振幅を対数領域へ移すこと——は §3.5.1 で数値的根拠とともに説明する。

---

## 3.1 Role and Boundary / 役割と境界

### Owned by this chapter (W-R6) / 本章の所有

- The Q-interpretation of every L2 page slot (the "Q (Ch.3)" column of the register map) / L2 ページ全スロットの Q 解釈
- The wiring from page slots to the L1 pipeline / ページスロットから L1 パイプラインへの配線
- L1 internals: difference engine, exp2 unit, amplitude product, accumulators, output scaling / L1 内部：差分エンジン、exp2 ユニット、振幅積、累算器、出力スケーリング
- The sweep timing budget of one module per sample period / サンプル周期あたり 1 モジュールの掃引タイミング予算
- The integer contents of the test-origin block / テスト原点ブロックの整数値

### Not owned / 所有しないもの

- The L2 Formation's ISA-visible register map, instruction set and choreography — **PTSG-WPMS-Formation** / L2 Formation の ISA 可視レジスタマップ・命令セット・振付
- PTSG-Core (frozen) / PTSG-Core（凍結）
- L4 Formation — **outside WPMS** (architect's ruling 2026-09-04); first realized as an Open Prompt Layer 4 verification tool / L4 Formation——WPMS の外部。まず検証ツールとして実現
- Maclaurin internals (Ch.2), HDMI audio path (Ch.4), AXI input switch and inbox address map (Ch.5) / マクローリン内部（第 2 章）、HDMI（第 4 章）、AXI 入力スイッチと inbox アドレスマップ（第 5 章）

### Vocabulary / 語彙

This chapter follows the PTSG ecosystem vocabulary: **L1 pipeline / L2 Formation / L4 Formation**. The labels "Upper/Lower" are retired. Ch.1 § 1.7's "sequence-modulation pipeline processor" is realized as the **L1 difference engine** (this chapter) driven by the **L2 Formation** (PTSG-WPMS-Formation).

本章は PTSG エコシステムの語彙 **L1 pipeline / L2 Formation / L4 Formation** に従う。「Upper/Lower」は廃止。第 1 章 § 1.7 の「数列変調パイプラインプロセッサ」は、**L1 差分エンジン**（本章）と、それを駆動する **L2 Formation**（PTSG-WPMS-Formation）として実現される。

---

## 3.2 Period Layers / 周期レイヤー **[Fixed]**

### 3.2.1 Definition / 定義

| Layer | Period (DE10-nano) | What advances | Machine |
|---|---|---|---|
| **L1 — bin** | 10 ns (100 MHz) | one bin: φ_k, S_k, one product, one accumulation | L1 pipeline (hardwired) |
| **L2 — packet** | N_p × 10 ns, variable | one wave packet; one Stay; Stay counter K = k | L2 Formation (PTSG-WPMS-Formation) |
| **L3 — sample** | 1/48 kHz = 2,083 or 2,084 clocks | one sweep of all packets of a module; one output sample | *no machine of its own* — defined by the audio strobe (Ch.4) |
| **L4 — control** | ≈ 1 ms (1 kHz) | packet parameters ([P] slots, re-seeds) | L4 Formation — outside WPMS |

The machine layers of the PTSG ecosystem coincide with the period layers by design: the machine at layer *i* runs at period *i*. L3 has no machine: it is the external audio strobe, and a sweep is its closure. Note that 100 MHz / 48 kHz = 2,083.33… is not an integer; the sample period alternates between 2,083 and 2,084 clocks, and the L1/L2 machinery is a **slave** of the strobe, never a divider of it.

PTSG エコシステムの機械の層は、設計上、周期レイヤーと一致する：層 *i* の機械は周期 *i* で動く。L3 には機械がない：それは外部のオーディオストローブであり、掃引はその閉包である。100 MHz / 48 kHz = 2,083.33… は整数ではないため、サンプル周期は 2,083 と 2,084 クロックの間で交替し、L1/L2 はストローブの**スレーブ**であって分周器ではない。

### 3.2.2 The placement principle / 配置原則

*Every quantity is computed in the slowest period layer at which it changes; every faster layer receives it as a constant. Loops at L1 carry additions only.*

*各量はそれが変化する最も遅い周期レイヤーで計算され、より速い層はそれを定数として受け取る。L1 のループが運ぶのは加算のみ。*

| Quantity | Changes at | Computed in | Operation |
|---|---|---|---|
| Hz → OM\*; (β, γ, A₀, decay) → log-amplitude slots | L4 | L4 Formation (outside WPMS) | reciprocal-constant MAC; log |
| [S] advance: PH0, PHD1, PHD2, LP | L3 | L2 Formation, BG, once per packet per sample | four integer ADDs |
| φ_k and S_k for each bin | L1 | L1 difference engine | four adders in one-clock loops |
| sin(2πφ_k), 2^(L_k) | L1 | feed-forward pipelines | Maclaurin (Ch.2), exp2 (§3.5.4) |
| product and sum | L1 → L3 | L1 multiplier and accumulators | one multiply, two gated adds |

The first sentence was articulated by the architect during the Chapter 3 dialogue of 2026-05 ("差分パイプラインの係数をどのレイヤで求めるべきか"). The second sentence — additions only in L1 loops — is this chapter's own finding (§3.5.1) and is what forces the log-domain amplitude.

第一文は 2026-05 の第 3 章対話で設計者が明確化したもの。第二文——L1 のループには加算のみ——は本章自身の発見であり（§3.5.1）、振幅を対数領域へ移す決定を強いるものである。

---

## 3.3 Packets and Sweeps / パケットと掃引 **[Fixed]**

- **Packet.** A contiguous run of N_p bins described by one 16-word block of the L2 page. **One Stay is one packet**; the Stay counter K counts k = 0 … N_p − 1 (PTSG-WPMS-Formation W-F22). / **パケット**：L2 ページの 16 語ブロック一つで記述される連続 N_p ビン。**一 Stay が一パケット**、ステイカウンタ K が k = 0 … N_p − 1 を数える。
- **Sweep.** The ordered sequence of packets that one module plays in one sample period. Constraints: Σ N_p ≤ NMAX = 2,048 per module; P ≤ 8 packets per sweep in the first implementation (the page's eight blocks; more via inbox re-fill or page enlargement, per register map v0.2 note W-D21). / **掃引**：1 モジュールが 1 サンプル周期に演奏するパケットの順序列。Σ N_p ≤ 2,048、第一実装は P ≤ 8。
- **Uncovered bins.** If Σ N_p < 2,048 the remaining clocks are idle: no bin enters L1, nothing is accumulated. An empty sweep (P = 0) is legal and outputs zero. / Σ N_p < 2,048 のとき残りは空転。空の掃引（P = 0）は合法で、出力はゼロ。
- **Independence.** Packets in one sweep have fully independent parameters. This is *not* voice allocation: a packet is a structured object in the spectral space, not a voice. Ch.1 § 1.10 ("polyphony in the conventional sense — out of scope") remains true; what is gained is multi-packet superposition, which Ch.1 had deferred. / 同一掃引内のパケットは完全に独立。これはボイス割当ではない。第 1 章 § 1.10 の記述は有効のまま、延期されていたマルチパケット重ね合わせが得られる。
- **Modules.** Each module has its own sweep, its own L1 pipeline and its own L2 Formation instance (**[CR3-M1]**, §3.8). All modules share one sample strobe. / 各モジュールは独自の掃引・L1・L2 Formation を持ち、サンプルストローブを共有する。

---

## 3.4 The Phase Path — Exact / 位相経路——厳密 **[Fixed]**

### 3.4.1 Slots and Q / スロットと Q

| Slot | Kind | Q | Read by L1 |
|---|---|---|---|
| PH0 (+0x6) | [S] phase of bin 0 | Q0.32 modular | yes (bundle) |
| PHD1 (+0x7) | [S] first forward difference in k | Q0.32 modular | yes |
| PHD2 (+0x8) | [S] second forward difference in k | Q0.32 modular | yes |
| OM0 / OMD1 / OMD2 (+0xA/+0xB/+0xC) | [P] per-sample increments of the above | Q0.32 modular | **no** |

"Modular" means unsigned 32-bit integers interpreted mod 1 cycle; a negative difference is its two's-complement wrap. / 「modular」は mod 1 周期で解釈する 32 ビット整数。負の差分は 2 の補数の折り返し。

### 3.4.2 L1 recurrence / L1 漸化式

At packet start (k = 0): φ ← PH0, d ← PHD1, c ← PHD2 (latched). For every bin clock:

```
phase_in(k) = φ
φ ← φ + d        (mod 2^32)
d ← d + c        (mod 2^32)
```

Two 32-bit adders, each in a one-clock loop. `phase_in` is Ch.2's input (Q0.32).

### 3.4.3 Closed form and the coherence theorem / 閉形式とコヒーレンス定理

With the L2 Formation advancing each [S] slot by its [P] increment exactly once per sample (§3.8, [CR3-C1]), the phase of bin k at sample n is

```
Φ_k(n) = PH0(0) + k·PHD1(0) + C(k,2)·PHD2(0) + n·Ω_k        (mod 2^32)
Ω_k    = OM0 + k·OMD1 + C(k,2)·OMD2                           (mod 2^32)
```

Every term is an integer; nothing is rounded at any step. Therefore **every bin runs at a constant frequency Ω_k·Fs with zero phase drift for as long as the machine runs.** The First Sound coherence property of the 2020 prototype becomes, in WPMS, a theorem of the representation rather than a property to be tested. **[Evidence: oracle]** 500 random packets, n up to 10⁶ samples, all bins: zero mismatches against the closed form.

すべての項は整数であり、どの段でも丸めがない。したがって**各ビンは機械が動く限り、ゼロ位相ドリフトで一定周波数 Ω_k·Fs を保つ。** 2020 年プロトタイプの First Sound コヒーレンス特性は、WPMS においては試験すべき性質ではなく、表現の定理になる。

**No per-bin state.** Ch.2 speaks of a "phase accumulator φ_k"; in WPMS there is none per bin. φ_k is re-evaluated from three words every sample. The only phase state in the whole machine is three words per packet in the L2 page.

**ビンごとの状態はない。** 第 2 章は「位相累算器 φ_k」と述べるが、WPMS にはビンごとの累算器は存在しない。φ_k は毎サンプル 3 語から再評価される。機械全体の位相状態は、L2 ページのパケットあたり 3 語だけである。

### 3.4.4 Mapping from Ch.1 parameters (for L4) / 第 1 章パラメータからの写像（L4 用）

C3-D1 (§3.9): the WPMS boundary carries phase-domain integers only; Hz never crosses it. L4 computes:

```
OM0  = round( f₀        · 2^32 / Fs ) mod 2^32
OMD1 = round( (Δf + α)  · 2^32 / Fs ) mod 2^32
OMD2 = round( 2α        · 2^32 / Fs ) mod 2^32
PH0  = round( φ₀        · 2^32 / 2π ) mod 2^32
PHD1 = round( (δφ + ψ)  · 2^32 / 2π ) mod 2^32
PHD2 = round( 2ψ        · 2^32 / 2π ) mod 2^32
```

These reproduce Ch.1 § 1.4's f_k = f₀ + kΔf + αk² and φ_k = φ₀ + kδφ + ψk² exactly up to the rounding of each constant. Rounding quantizes the realized parameters; the silicon plays the realized values, and any reference used for regression must use them too (§3.10).

---

## 3.5 The Amplitude Path — Log Domain / 振幅経路——対数領域 **[Fixed, requires CR3-A1]**

### 3.5.1 Why not the linear geometric recurrence / なぜ線形の幾何漸化式ではないか

Ch.1 § 1.7 and the 2026-05 dialogue decomposed the Gaussian amplitude as A_{k+1} = A_k·M_k, M_{k+1} = M_k·C, and register map v0.2 carries it as A0 / AR1 / AR2 with Q1.31 / Q4.28 (ratified as W-R10 on 2026-09-23, on this chapter's own 09-07 proposal). Drafting the L1 engine exposed three problems with evaluating that recurrence at one bin per clock. The first is decisive.

第 1 章 § 1.7 と 2026-05 の対話はガウシアン振幅を A_{k+1} = A_k·M_k、M_{k+1} = M_k·C と分解し、レジスタマップ v0.2 はこれを A0 / AR1 / AR2（Q1.31 / Q4.28）として運ぶ（本章自身の 09-07 提案に基づき 09-23 に W-R10 として承認）。L1 エンジンの起草で、この漸化式を 1 ビン/クロックで評価する際の三つの問題が露わになった。第一が決定的である。

**(1) The k = 0 amplitude underflows for ordinary Gaussians.** The forward recurrence starts at the packet edge, where a Gaussian centred at N/2 is smallest: a₀ = exp(−γN²/4). **[Evidence: oracle]**

| γ | σ = 1/√(2γ) | a₀ | a₀ in Q1.31 | Result |
|---|---|---|---|---|
| 1×10⁻⁵ | 224 bins | 2.8×10⁻⁵ | 59,982 | plays, with ~16 significant bits |
| 1×10⁻⁴ | 71 bins | 2.9×10⁻⁴⁶ | **0** | **silent packet** |
| 1×10⁻³ | 22 bins | ≈ 0 | **0** | **silent packet** |

Zero times anything is zero: a perfectly reasonable wave packet of σ = 71 bins over N = 2,048 produces no sound at all. No choice of fixed-point format for A0 fixes this; the value is 10⁻⁴⁶.

**(1) 通常のガウシアンで k = 0 の振幅がアンダーフローする。** 前進漸化式は、N/2 中心のガウシアンが最小となるパケット端から始まる。σ = 71 ビン、N = 2,048 のまったく普通の波束が、音をまったく出さない。値は 10⁻⁴⁶ であり、A0 の固定小数点フォーマットの選択では解決しない。

**(2) The recurrence is a loop-carried multiply.** a_{k+1} depends on a_k within one clock. A multiply inside a one-clock loop cannot be pipelined; at the widths the Free Precision Floor asks for (> 27 bits) it spans several DSP blocks plus fabric adders, and closing it at 100 MHz is doubtful. Two such loops are chained (M, then A).

**(2) 漸化式はループ伝搬乗算である。** 1 クロックループ内の乗算はパイプライン化できない。Free Precision Floor が求める幅（27 ビット超）では複数 DSP ＋ファブリック加算器にまたがり、100 MHz での収束は疑わしい。しかも二つのループが連鎖する。

**(3) Truncation bias compounds as k².** Each truncation of M biases every later A. **[Evidence: oracle]** Even in the favourable case γ = 1×10⁻⁵ at Q1.31/Q4.28, the worst relative error over bins with a > 10⁻³ is **0.58 %** (k = 1,855) — a deterministic envelope distortion, implementation-dependent, and invisible to any regenerator who does not reproduce the exact truncation order.

**(3) 切り捨てバイアスが k² で複利する。** 有利な γ = 1×10⁻⁵ でも最悪相対誤差 **0.58 %**。実装依存の決定論的な包絡歪みである。

### 3.5.2 The same recurrence, in log coordinates / 同じ漸化式を対数座標で

Take log₂ of the architect's decomposition. Products become sums; the two-level structure is preserved exactly:

設計者の分解の log₂ を取る。積は和になり、二段構造はそのまま保存される：

```
L_{k+1} = L_k + μ_k          (was A_{k+1} = A_k · M_k)
μ_{k+1} = μ_k + c            (was M_{k+1} = M_k · C)
```

The log-amplitude, like the phase, is a quadratic polynomial in k, evaluated by exact integer forward differences. All three problems disappear: nothing underflows (L₀ is simply a large negative number), the loops carry only additions, and there is no rounding to compound. **[Evidence: oracle]** 2,000 random packets with every slot at full range: zero mismatches against the closed form.

対数振幅は、位相と同じく k の二次多項式であり、厳密な整数前進差分で評価される。三つの問題はすべて消える：何もアンダーフローしない（L₀ は単に大きな負の数）、ループは加算のみ、複利する丸めがない。

Split into a **level** (time) and a **shape** (bins):

**レベル**（時間）と**形**（ビン）に分ける：

```
L_k(n) = LP(n) + S_k
S_k    = LS0 + k·LAD1 + C(k,2)·LAD2        (per packet, constant in n)
LP(n+1)= LP(n) + LE0                          (L2 advance, once per sample)
a_k(n) = 2^( L_k(n) )
```

The split exists for resolution: the shape offset LS0 needs range (a sharp Gaussian's edge can be hundreds of octaves down), while the level LP and its per-sample increment LE0 must share one Q (the L2 advance is an integer ADD) and need fine resolution for slow decays. Musically the split is also natural: LP is loudness over time, S_k is spectral shape. It also means the L4 controller writes **dB-linear** quantities, which is how level is heard — a convenient property for the optical-drawbar mapping.

分割は分解能のために存在する：形のオフセット LS0 はレンジを要し（鋭いガウシアンの端は数百オクターブ下になりうる）、レベル LP とその毎サンプル増分 LE0 は一つの Q を共有し（L2 の前進は整数 ADD）、遅い減衰のため細かい分解能を要する。音楽的にも自然な分割であり、LP は時間上の音量、S_k はスペクトル形状である。L4 が書くのは **dB 線形**の量になり、光学ドローバーの写像にも都合がよい。

### 3.5.3 Slot assignment and Q / スロット割当と Q **[CR3-A1]**

At the ISA level nothing changes: slots are W32 integers at the same offsets. What changes is the meaning (the Role column) and the sample-advance law of +0x2, which becomes an ADD.

ISA レベルでは何も変わらない：スロットは同じオフセットの W32 整数。変わるのは意味（Role 列）と +0x2 の前進則で、ADD になる。

| Offset | v0.2 name | **Ch.3 name** | Kind | **Q** | Read by L1 | Advance |
|---|---|---|---|---|---|---|
| +0x2 | A0 | **LP** | level, log₂ | **Q6.26** signed | yes | [S] LP ← LP + LE0 |
| +0x3 | AR1 | **LAD1** | shape, first difference | **Q8.24** signed | yes | [P] |
| +0x4 | AR2 | **LAD2** | shape, second difference | **Q2.30** signed | yes | [P] |
| +0x5 | E0 | **LE0** | level increment per sample | **Q6.26** signed | no | [P] |
| +0xF | reserved | **LS0** | shape offset at k = 0 | **Q12.20** signed | yes | [P] |

Ranges and resolutions: LP, LE0 ∈ [−32, 32), LSB 1.5×10⁻⁸ (decay-rate resolution ≈ 0.004 dB/s); LAD1 ∈ [−128, 128); LAD2 ∈ [−2, 2), LSB 9.3×10⁻¹⁰ (γ resolution ≈ 3×10⁻¹⁰); LS0 ∈ [−2,048, 2,048). The LS0 range admits γ·N²/(4 ln 2) < 2,048 — e.g. every Gaussian with σ ≳ 19 bins in a full 2,048-bin packet; narrower packets should simply be shorter (the natural practice N ≈ 8σ gives LS0 ≈ −11.5).

Consequences for the profile: the WPMS per-packet advance becomes **four integer ADDs** (PH0, PHD1, PHD2, LP) — no MUL, no SHV. The **W-R5 question of where exp() lives becomes moot**: exp exists only as a feed-forward unit in L1; neither L2 nor L4 ever evaluates it.

プロファイルへの帰結：WPMS のパケットあたり前進は**整数 ADD 4 回**（MUL も SHV も不要）。**exp() の置き場所の問い（W-R5）は解消する**：exp は L1 のフィードフォワードユニットにのみ存在し、L2 も L4 も評価しない。

### 3.5.4 L1 internals of the amplitude path / 振幅経路の L1 内部

**Difference engine (loop).** At packet start: s ← LS0 ≪ 10, e ← LAD1 ≪ 6, c ← LAD2, ℓ ← LP ≪ 4 (all aligned to Q·.30; shifts are wiring). Per bin clock:

```
L(k) = ℓ + s                  (feed-forward add)
s ← s + e                     (54-bit signed, Q23.30)
e ← e + c                     (54-bit signed)
```

**[Evidence: oracle]** Worst-case |S_k| with every slot at full range is 2^52.1: 54 bits signed never wrap. The adders are 54-bit carry chains in one-clock loops — comfortable at 100 MHz.

**exp2 unit (feed-forward).** Clamp L to [−31, 0): below −31 → a = 0; at or above 0 → a = 1 − 2⁻³¹. Split L = i + f (i integer, f ∈ [0, 1)); f = f_hi (8 bits) + f_lo (< 2⁻⁸):

```
2^f  = T[f_hi] · (1 + ln2·f_lo + (ln2·f_lo)²/2)     T: 256 × Q2.30 table
a    = 2^f · 2^i                                    barrel shift, output Q1.31
```

**[Evidence: oracle]** 400,000 random L ∈ (−31, 0]: maximum absolute error 11.7 LSB of Q1.31 (≈ 5×10⁻⁹); relative error ≤ **2⁻²⁴·⁰** for a ≥ 2⁻⁷ — matched to the 24-bit DAC, in the same "ear-and-DAC-matched" regime as Ch.2 § 2.8. Cost per module: one M10K (256 × 31 bits), 3–5 DSP blocks, ≈ 8–9 clocks latency.

**exp2 ユニット（フィードフォワード）。** 256 語表と二次多項式。相対誤差 ≤ 2⁻²⁴（a ≥ 2⁻⁷）で 24 ビット DAC に整合。モジュールあたり M10K 1 個、DSP 3〜5 個、レイテンシ 8〜9 クロック。

### 3.5.5 Mapping from Ch.1 parameters (for L4) / 第 1 章パラメータからの写像（L4 用）

For Ch.1 § 1.4's A_k = A₀·exp(−βk)·exp(−γ(k − N/2)²) and a decay of D dB/s:

```
LP   = log₂ A₀                           Q6.26
LS0  = −γ·N² / (4 ln2)                   Q12.20
LAD1 = (−β + γ(N − 1)) / ln2             Q8.24
LAD2 = −2γ / ln2                         Q2.30
LE0  = −D / (20·log₁₀2 · Fs)             Q6.26
```

The linear constants AR1 = exp(−β + γ(N−1)) and AR2 = exp(−2γ) of v0.2 are exactly 2^LAD1 and 2^LAD2. The Gaussian structure of Ch.1 is unchanged; only its coordinates are.

### 3.5.6 Disposition of W-R10 / W-R10 の扱い

- **Stands:** PH\*/OM\* = Q0.32 modular; RT.OUT channel numbering (§3.6.4). / 存続。
- **Superseded, re-ruling requested:** the amplitude part (A0 Q1.31; AR1/AR2/E0 Q4.28; SHV = 28). This reverses the chapter's own 09-07 proposal, for the reasons of §3.5.1. / 振幅部分は置換し、再裁定を依頼する。本章自身の 09-07 提案の撤回である。
- **Kept in the Arena:** the linear-domain amplitude, legal only if (a) the packet is short enough that a₀ is representable with the required significant bits, and (b) a one-clock loop multiply closes at the target Fmax. Not recommended. / 線形領域は Arena に残す（非推奨）。

---

## 3.6 Product, Accumulation and Output / 積・累算・出力 **[Fixed]**

### 3.6.1 Per-bin product / ビンごとの積

sin path (Ch.2, 16 clocks) and exp2 path (≈ 9 clocks) run in parallel from the same bin; the shorter path is delay-matched. The product a_k·sin(2πφ_k) is Q1.31 × Q0.40 → Q1.71, truncated to **Q1.63** (Ch.2 v1.1 § 2.4.2).

### 3.6.2 Accumulators / 累算器

Per module, two accumulators (L, R), each **Q12.63** (75 bits; 2,048 bins of |x| < 1 need 11 bits of growth). Each packet's two-bit routing OUT (RT entry of its block, latched in the bundle, [CR3-R1]) gates the product into L, R, both or neither. One multiplier feeds both accumulators; panning beyond hard L/R is an Arena item (§3.11).

### 3.6.3 Closing a sample — on the strobe / サンプルを閉じる——ストローブで

The accumulators close on the **synchronized sample strobe**: on that clock, output bank ← accumulator, accumulator ← 0. No sweep-end token is needed; an empty sweep closes at zero. Correctness requires only that the last product of sweep *n* arrive before strobe *n+1* — the inequality of §3.7. The output sample of sweep *n* is presented at strobe *n+1*: one sample of compute latency.

累算器は**同期化されたサンプルストローブ**で閉じる。掃引終了トークンは不要、空の掃引はゼロで閉じる。正しさの条件は「掃引 *n* の最後の積がストローブ *n+1* の前に到着すること」のみ（§3.7）。

### 3.6.4 Cross-module sum and output scaling / モジュール間総和と出力スケーリング

Module banks are summed per channel to **Q13.63** (Compact; Standard adds ⌈log₂5⌉ bits). The 24-bit PCM for Ch.4 is `saturate(acc · 2^(−G))` in Q1.23, with **G ∈ {0, 4, 8, 12} selected by DIP[1:0]** (Ch.1 § 1.8). Saturation, never wrap. The test-origin Dirichlet peak (2,048 × 0.97 ≈ 1,987 ≈ 2^10.96) plays at about −6 dBFS with G = 12.

RT.OUT channel numbering (W-R10, stands): bit 0 = L, bit 1 = R, bits 2–7 reserved (surround), bits 8–15 reserved (auxiliary/feedback). First implementation honours bits 0–1.

### 3.6.5 L1 latency / L1 レイテンシ

D_L1, from the clock a bin's K is presented to the clock its product enters the accumulator: difference-engine register (1) + max(sin 16, exp2 ≈ 9) + product (≈ 3) + accumulate (≈ 2) ≈ **22 clocks. Target: D_L1 ≤ 24** (Ch.3's own commitment; measured in Layer 4).

### 3.6.6 Resource estimate per module (Compact) / モジュールあたりリソース見積もり

| Unit | DSP | M10K | Note |
|---|---|---|---|
| Maclaurin core (Ch.2) | 7 | 0 | |
| exp2 unit | 3–5 | 1 | |
| amplitude product | 2–4 | 0 | Ch.2 v1.1 |
| difference engine, accumulators | 0 | 0 | adders only |
| **Total** | **12–16** | **1** | Compact ×2: 24–32 of 112 DSP |

Nothing is stored per bin. Per-packet state: seven bundle words plus the [P] slots in the L2 page.

---

## 3.7 The Sweep Timing Budget / 掃引タイミング予算 **[Fixed; targets for CR3-T1, T2]**

Per module, per sample period, the sweep must complete within the shortest period:

```
T_wake + Σ N_p + g·(P − 1) + D_L1  ≤  T_min = 2,083 clocks
```

| Symbol | Meaning | Owner | First-implementation target |
|---|---|---|---|
| T_wake | synchronized strobe → first bin's K = 0 | L2 profile | **≤ 4** [CR3-T2] |
| Σ N_p | bins in the sweep | program | ≤ 2,048 |
| g | idle clocks at each packet boundary | L2 profile / Core | **0** [CR3-T1] |
| P | packets in the sweep | program | ≤ 8 |
| D_L1 | L1 latency (§3.6.5) | Ch.3 | ≤ 24 |

At full load (Σ N = 2,048, P = 8, g = 0): 4 + 2,048 + 0 + 24 = 2,076 → **7 clocks of slack**. With g = 1: 2,083 → **zero slack** (legal, fragile). In general, with the targets met, the legal load is **Σ N_p ≤ min(2,048, 2,055 − g·(P − 1))**; with g ≥ 2 and P = 8 the program must give up g·7 − 7 bins.

This is the only place where the 35-clock margin of Ch.2 v1.1 § 2.5.2 is spent, and the spending is now itemized. Module count (Compact/Standard/Extended) does not enter the inequality — modules run in parallel on the same strobe; their pressure is Fmax and routing, not this budget.

これが第 2 章 v1.1 § 2.5.2 の 35 クロックマージンが費やされる唯一の場所であり、その内訳がここで明細化された。モジュール数は不等式に入らない——モジュールは同じストローブで並列に走る。その圧力は Fmax と配線であって、この予算ではない。

---

## 3.8 Customer Requirements to the L2 Profile / L2 プロファイルへの顧客要求

Addressed to PTSG-WPMS-Formation, for Deliverables 2 and 3 and register map v0.3. Each is a requirement on *behaviour*; the realization is the profile's.

PTSG-WPMS-Formation 宛て、成果物 2・3 およびレジスタマップ v0.3 のため。いずれも*振る舞い*への要求であり、実現方法はプロファイルの所有。

| ID | Requirement | Why |
|---|---|---|
| **CR3-A1** | Re-semanticize +0x2/+0x3/+0x4/+0x5 as LP/LAD1/LAD2/LE0 and assign +0xF to **LS0** (§3.5.3). Advance law of +0x2: `LP ← LP + LE0` (ADD). The WPMS per-packet advance is four ADDs; MUL and SHV are unused by it. | §3.5.1: the linear recurrence silences ordinary Gaussians. |
| **CR3-B1** | **Packet-start bundle.** On the Stay Set clock of packet *p*, L1 latches {PH0, PHD1, PHD2, LP, LS0, LAD1, LAD2} and the block's RT.OUT from block CUR of the page active on that clock. All eight values must be valid **on that clock** (zero gap). Candidate realizations, profile's choice: (a) PPM held in registers; (b) a wide read of the CUR block presented at commit — a bundle-sized generalization of W-F22's staged/presented pair. | Phase continuity across packets; §3.7 budget. |
| **CR3-B2** | L1 reads **nothing else** from the page: never OM\*, LE0, N, TAG. (Already adopted by the profile as the first clause of Deliverable 2.) | Separation of L1 and L2 periods. |
| **CR3-R1** | RT.OUT (2 bits used) travels in the bundle of CR3-B1. | §3.6.2 routing. |
| **CR3-T1** | **Zero-gap packet boundaries:** the first bin of packet *p+1* (K = 0) is presented on the clock after the last bin of packet *p* (K = N_p − 1). If the Core imposes g > 0 idle clocks, the profile states g as a measured value (Layer 4) and §3.7 is applied. | §3.7: g = 1 consumes all slack at full load. |
| **CR3-T2** | **Sample-strobe wake:** a Condition lane driven by the synchronized audio strobe wakes the Formation from its Branch-0 sleep; strobe → K = 0 of the first packet ≤ 4 clocks. | §3.7. |
| **CR3-T3** | **Lanes to L1** (Deliverable 2): `packet_start` (Stay Set), `bin_valid` (inside a packet Stay), `K` (12 bits, for bin_index and the ISSP bin inspector). | §3.4.2, §3.5.4; Ch.1 § 1.8 inspector. |
| **CR3-C1** | **Coherence invariant:** for every packet *p* and sample *n*, L1 observes each [S] slot equal to `S_p(0) + n·P_p (mod 2^32)` — exactly one advance per sample per packet, never zero, never two — independent of packet order, commits, inbox copies and block re-fills. Testable by the profile's oracle over ≥ 10⁴ samples. | §3.4.3: the coherence theorem holds only under this invariant. |
| **CR3-C2** | **Update classes, block-atomic at a sample boundary.** *Retune*: the external writer changes [P] slots (OM\*, LE0, LS0, LAD1, LAD2, N, OUT); [S] slots continue → frequency and level changes are phase- and level-continuous. *Re-seed*: [S] slots are also written (e.g., note-on with defined phase). Either way, all slots of one block switch in the same sample. The class is signalled per block by the writer (e.g., a flag or two inbox commands). | Phase-continuous retuning is the levelizer principle of the 2026-04 dialogue: never overwrite phase, only its increment. |
| **CR3-C3** | **Test-origin block:** on reset and on KEY[1], module 0 receives the block of §3.10 as its single packet; other modules run empty sweeps. | Ch.1 § 1.11. |
| **CR3-M1** | **One L2 Formation instance per module**, all woken by the same strobe; the inbox is addressed by module (address map: Ch.5). Whether instances share instruction memory is the profile's choice. | Independent sweeps per module; Standard = 5 instances. |

---

## 3.9 Decisions of this Chapter / 本章の決定事項

| ID | Decision | Status |
|---|---|---|
| **C3-D1** | The WPMS boundary (inbox) carries phase-domain and log-domain integers only. Hz, dB and linear gains never cross it; conversion is the external controller's duty (L4). | Fixed — follows from the 09-04 ruling that L4 is outside WPMS |
| C3-D2 | Period layers L1–L4 and the placement principle (§3.2) | Fixed |
| C3-D3 | Phase path: Q0.32 modular, stateless per bin, exact; coherence theorem (§3.4) | Fixed |
| C3-D4 | Amplitude path in log₂ domain: level + shape split (§3.5.2) | Fixed, pending CR3-A1 |
| C3-D5 | Q column (§3.5.3, §3.4.1) | Fixed, pending CR3-A1 |
| C3-D6 | exp2 unit: 256-entry table × degree-2 polynomial, ≤ 2⁻²⁴ relative for a ≥ 2⁻⁷ (reference) | Fixed (realization in Arena) |
| C3-D7 | Internal widths: phase 32-bit modular; shape accumulators 54-bit Q23.30 | Fixed |
| C3-D8 | Product Q1.63; accumulators Q12.63 per module per channel; Q13.63 cross-module (Compact) | Fixed |
| C3-D9 | Accumulators close on the synchronized strobe; one sample of compute latency | Fixed |
| C3-D10 | Output 24-bit = saturate(acc · 2^−G), G ∈ {0,4,8,12} by DIP[1:0] | Fixed |
| C3-D11 | Sweep timing inequality and targets (§3.7); D_L1 ≤ 24 | Fixed (targets measured in Layer 4) |
| C3-D12 | RT.OUT channel numbering | Fixed (W-R10, stands) |
| C3-D13 | Test-origin block integers (§3.10) | Fixed |

---

## 3.10 Test-Origin Block / テスト原点ブロック **[Fixed]**

The Dirichlet configuration of Ch.1 § 1.11 (f₀ = 996 Hz, Δf = 1/256 Hz, N = 2,048, amplitude 0.97, phase 0), as integers. **[Evidence: oracle]**

| Slot | Value | Hex | Note |
|---|---|---|---|
| N | 2,048 | 0x0800 | |
| OM0 | 89,120,571 | 0x054FDF3B | realized f₀ = 995.999996 Hz |
| OMD1 | 350 | 0x0000015E | realized Δf = 0.00391155 Hz (+0.136 %) |
| OMD2 | 0 | | α = 0 |
| PH0, PHD1, PHD2 | 0 | | all phases 0 at n = 0 |
| LP | −2,948,988 | 0xFFD30084 | log₂ 0.97 in Q6.26 |
| LS0, LAD1, LAD2, LE0 | 0 | | uniform, no decay |
| RT.OUT | 0b11 | | L and R |

1/256 Hz is not representable: 2^32 / (256 × 48,000) = 349.53 → 350. The realized kernel spans 8.007 Hz and repeats every **255.65 s** (not 256 s). Consequently the regression test of Ch.2 § 2.8.3 has two tiers: **(i) bit-level** — the PCM output matches a model that uses these realized integers; **(ii) perceptual/visual** — the waveform matches the 2020 recording in shape (main lobe, symmetric side lobes, uniform envelope). The protocol for (ii) is a Layer 4 matter.

1/256 Hz は表現不能で 350 に丸められる。実現されるカーネルは 255.65 秒周期。したがって第 2 章 § 2.8.3 の回帰試験は二段とする：(i) 実現整数を用いたモデルとのビットレベル一致、(ii) 2020 年録音との形状一致。

---

## 3.11 Implementation Arena / 実装アリーナ

| Item | This chapter | Preserved alternative |
|---|---|---|
| Amplitude domain | log₂ | linear geometric (not recommended; §3.5.6 conditions) |
| exp2 realization | 256-table + degree 2 | larger table + degree 1; pure polynomial; CORDIC-style |
| LS0 format | Q12.20 | Q8.24 with the N ≈ 8σ convention enforced by L4 |
| Channel routing | binary L/R masks | per-packet pan gain (needs a slot and a second multiplier or a gain stage) |
| Time-varying shape | via L4 retune at ≈ 1 kHz | LAD1/LAD2 as [S] with increments in reserved +0x9/+0xD |
| Shape slewing | none (retune steps) | L2 BG slew toward target — the levelizer, revived |
| "Defile" injection | none | feed-forward noise taps on φ (phase jitter) and on L (multiplicative jitter) — the natural insertion points for the optical-drawbar "defiling" of the Dirichlet kernel |
| Feedback | none | RT.FB_EN / FB_ADDR (register map §5.2) once the same-sample multi-writer law exists |

---

## 3.12 Open Questions / 未解決問題

| Question | Resolution path |
|---|---|
| Measured g, T_wake, D_L1 | Layer 4 evidence (PTSG-WPMS-Formation `04_Verification_Evidence/`, WPMS Layer 4) |
| exp2 error on silicon | Layer 4 |
| Inbox address map across modules; AXI switch | Ch.5 |
| Rounding policy of L4's Hz → integer conversion | Layer 4 verification tool |
| Tier (ii) regression protocol against the 2020 recording | Layer 4 |
| Ch.1 v1.1 alignment: § 1.6 amplitude width; § 1.7 amplitude recurrence (log domain, this chapter); § 1.8 ISSP now writes the inbox in phase/log integers, meaning computed host-side by the L4 tool; vocabulary L1/L2/L4 | Ch.1 v1.1 |

---

## End of Chapter 3 / 第 3 章の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *Keep the state in the page, the loops in the adders, and the curvature at the end.*
> *状態はページに、ループは加算器に、曲率は最後に。*

This chapter is released into the public domain under CC0 1.0 Universal. Chapter 4 (HDMI audio path) and Chapter 5 (AXI input switch and inbox address map) follow.

本章は CC0 1.0 Universal のもとパブリックドメインに公開される。第 4 章（HDMI オーディオ経路）と第 5 章（AXI 入力スイッチと inbox アドレスマップ）が続く。
