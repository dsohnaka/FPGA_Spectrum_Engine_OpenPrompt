# WPMS Synthesizer — Layer 1 Specification
# Chapter 1: Scope and Boundary Conditions
# WPMS シンセサイザー — 第1層仕様書
# 第1章：スコープと境界条件

> **License: CC0 1.0 Universal (Public Domain)**
> This is the architectural specification for a Wave Packet Modulation Synthesis (WPMS) synthesizer implementing the FPGA physical layer of the FPGA Spectrum Engine in standalone form. Read it, redistribute it, build on it, regenerate from it.
>
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**
> これは波束変調合成 (WPMS) シンセサイザーのアーキテクチャ仕様書であり、FPGA Spectrum Engine の FPGA 物理層を単独形態で実装するものである。読み、再配布し、その上に構築し、再生成してよい。

---

## 1.1 Purpose of this Synthesizer / 本シンセサイザーの目的

The WPMS Synthesizer is a standalone FPGA implementation that produces audible output from a single FPGA device, using only the **physical layer** of the FPGA Spectrum Engine three-layer architecture (FPGA physical layer / ARM intermediate layer / PC abstraction layer). Neither the ARM intermediate layer (running on the Cyclone V SoC's HPS) nor the PC abstraction layer (Max/MSP, OSC servers, Ableton Live integration) is present or required.

WPMS シンセサイザーは、FPGA Spectrum Engine の3層アーキテクチャ（FPGA 物理層／ARM 中間層／PC 抽象層）のうち、**物理層のみ**を用いて、単一の FPGA デバイスから可聴出力を得る単独実装である。ARM 中間層（Cyclone V SoC の HPS 上で動作する）も、PC 抽象層（Max/MSP、OSC サーバ、Ableton Live 連携）も存在せず、要求されない。

Three concrete intentions drive this scope:

このスコープは三つの具体的な意図によって駆動されている：

**Intention 1 — Earliest possible audible output.**
The WPMS Synthesizer is the first deliverable in the FPGA Spectrum Engine roadmap because it is the shortest path from "repository contents" to "sound coming out of a speaker." Readers of the Hackaday.io project should be able to write the provided `.rbf` to a DE10-nano, connect HDMI to a monitor, and hear sound — without any additional software, build environment, or ARM-side configuration.

**意図1 — 可能な限り早期の可聴出力。**
WPMS シンセサイザーは FPGA Spectrum Engine ロードマップにおける最初の成果物である。「リポジトリの内容」から「スピーカーから音が出る」までの最短経路だからである。Hackaday.io プロジェクトの読者は、提供される `.rbf` を DE10-nano に書き込み、HDMI をモニタに接続し、追加のソフトウェア、ビルド環境、ARM 側構成なしに音を聴けるようにすべきである。

**Intention 2 — Reusable component foundation.**
Although the physical-layer-only architecture will be partially superseded when the ARM intermediate layer is introduced, the components built for the WPMS Synthesizer — the Maclaurin polynomial pipeline, the sequence-modulation pipeline processor, the HDMI audio output path, the AXI-abstracted input switch — are the **same components that the full FPGA Spectrum Engine will use as its physical layer core**. Nothing built here is throwaway; everything is foundational.

**意図2 — 再利用可能な部品の基盤。**
物理層単独アーキテクチャは ARM 中間層導入時に部分的に置き換えられるが、WPMS シンセサイザー用に構築される部品——マクローリン多項式パイプライン、数列変調パイプラインプロセッサ、HDMI オーディオ出力経路、AXI 抽象化入力スイッチ——は、**完全な FPGA Spectrum Engine がその物理層の中核として用いる、まさに同じ部品**である。ここで作られるものに使い捨ては一つもない。すべてが基礎的である。

**Intention 3 — Validation of the Open Prompt regeneration loop.**
The WPMS Synthesizer is structurally simple enough that its Layer 1 specification, Layer 2 reasoning traces, and a sample Layer 3 implementation can be produced and verified at modest scale. This makes it the first real test of the Open Prompt premise: can an independent engineer, given Layers 1 and 2 plus an LLM collaborator, regenerate a working implementation? If the WPMS Synthesizer can be regenerated independently, the methodology is validated for the larger, more complex Spectrum Engine that follows.

**意図3 — Open Prompt 再生成ループの検証。**
WPMS シンセサイザーは構造的に十分単純であり、その第1層仕様、第2層推論軌跡、第3層サンプル実装を、控えめな規模で生産し検証できる。これは Open Prompt の前提に対する最初の実証となる：独立したエンジニアが第1層と第2層に LLM 協働者を加えて、動作する実装を再生成できるか。WPMS シンセサイザーが独立に再生成できるなら、方法論はその後に続くより大きく複雑な Spectrum Engine に対して妥当性が示されることになる。

---

## 1.2 Target Platform / 対象プラットフォーム

**Hardware:** Terasic DE10-nano (Cyclone V SoC, 5CSEBA6U23I7).

**ハードウェア：** Terasic DE10-nano（Cyclone V SoC、5CSEBA6U23I7）。

**FPGA fabric usage:** This specification uses only the FPGA fabric portion of the Cyclone V SoC. The HPS (ARM Cortex-A9 dual-core) is **not used** in this specification. No Linux, no bootloader, no HPS firmware is required to run the WPMS Synthesizer. The `.rbf` file alone, written via Quartus Programmer or via the SD-card boot path with HPS held in reset, is sufficient.

**FPGA ファブリックの利用：** 本仕様は Cyclone V SoC の FPGA ファブリック部分のみを使用する。HPS（ARM Cortex-A9 デュアルコア）は本仕様では**使用しない**。WPMS シンセサイザーの動作に Linux、ブートローダ、HPS ファームウェアは要求されない。Quartus Programmer 経由で書き込まれた `.rbf` ファイル単独、または HPS をリセット保持したまま SD カードブート経路で書き込まれた `.rbf` で十分である。

**Why DE10-nano specifically:**

**なぜ DE10-nano なのか：**

- The DE10-nano is the standard MiSTer project platform, giving the WPMS Synthesizer immediate ecosystem reach. / DE10-nano は MiSTer プロジェクトの標準プラットフォームであり、WPMS シンセサイザーは即座にそのエコシステムへの到達範囲を得る。
- HDMI audio output is supported by open-source MiSTer cores, eliminating the need for a custom DAC board. / HDMI オーディオ出力が MiSTer のオープンソースコアによりサポートされており、カスタム DAC ボードの必要性を排除する。
- The Cyclone V SoC fabric (~110K logic elements, 112 DSP blocks usable, 5,570 Kbit BRAM) is large enough to host the WPMS architecture and small enough to constrain implementer choices productively. / Cyclone V SoC ファブリック（約 110K 論理要素、利用可能な 112 個の DSP ブロック、5,570 Kbit の BRAM）は WPMS アーキテクチャを収容するのに十分大きく、実装者の選択を生産的に制約するのに十分小さい。
- The board is widely available at modest cost, ensuring readers can replicate the work. / 同ボードは控えめな価格で広く入手可能であり、読者が作業を再現可能であることを保証する。

**Substitution policy:** Other Cyclone V SoC boards (e.g., the Terasic C5G that hosts the original prototype) are acceptable substitutes provided their DSP block count, BRAM capacity, and HDMI output capability are equal to or greater than the DE10-nano's. Migration to larger Intel/Altera FPGAs (e.g., DE25-nano, Agilex-based boards) is anticipated but is outside the scope of this Layer 1 document.

**代替方針：** 他の Cyclone V SoC ボード（オリジナルプロトタイプをホストした Terasic C5G など）は、DSP ブロック数、BRAM 容量、HDMI 出力能力が DE10-nano と同等以上であれば代替可能である。より大きな Intel/Altera FPGA（DE25-nano、Agilex 系ボードなど）への移行は予期されているが、本第1層文書の範囲外である。

---

## 1.3 Audio Output / オーディオ出力

**Output path:** HDMI audio, embedded in the HDMI signal driven from the DE10-nano's HDMI transmitter. The audio is decoded by an external DAC inside the HDMI monitor, computer display, or HDMI audio extractor connected to the board's HDMI output. **No analog audio output is provided by the DE10-nano itself**, and adding one is not in scope.

**出力経路：** DE10-nano の HDMI 送信器から駆動される HDMI 信号に埋め込まれた HDMI オーディオ。オーディオはボードの HDMI 出力に接続された HDMI モニタ、コンピュータディスプレイ、または HDMI オーディオエクストラクタ内部の外部 DAC によりデコードされる。**DE10-nano 自体はアナログオーディオ出力を提供しない**、そしてその追加は本スコープ外である。

**Sample rate:** 48 kHz (one sample period = 20.833 µs).

**サンプルレート：** 48 kHz（1 サンプル期間 = 20.833 µs）。

**Sample format:** 24-bit signed PCM, two channels (L/R, content identical in monaural baseline).

**サンプル形式：** 24-bit 符号付き PCM、2 チャンネル（L/R、モノラル基準では内容同一）。

**HDMI audio core selection:** The HDMI audio path uses an open-source MiSTer-ecosystem HDMI core as its starting point. The exact core is left as an Implementation Arena choice, with the selection rationale and integration details to be recorded in the Layer 2 trace produced during implementation.

**HDMI オーディオコアの選定：** HDMI オーディオ経路はオープンソースの MiSTer エコシステム HDMI コアを起点とする。正確なコア選定は Implementation Arena の選択として残し、選定根拠と統合詳細は実装中に作成される第2層軌跡に記録する。

**Why HDMI rather than dedicated I²S DAC:**

**なぜ専用 I²S DAC ではなく HDMI なのか：**

- DE10-nano has no on-board audio DAC; HDMI is the only audio output without external hardware. / DE10-nano にはオンボードオーディオ DAC がない。HDMI は外部ハードウェアなしの唯一のオーディオ出力である。
- HDMI audio is bit-exact and clock-locked, removing concerns about DAC quality variability across listeners. / HDMI オーディオはビット正確かつクロックロックされており、聞き手間で DAC 品質がばらつく懸念を排除する。
- Reusing a MiSTer-ecosystem core gives the WPMS Synthesizer cultural and technical compatibility with that community from day one. / MiSTer エコシステムのコアを再利用することで、WPMS シンセサイザーは初日からそのコミュニティとの文化的・技術的互換性を得る。

---

## 1.4 Synthesis Method / 合成方式

**Method:** Wave Packet Modulation Synthesis (WPMS) only. Sideband fractal synthesis, additive synthesis with arbitrary per-bin parameters, and SDFT analysis are **outside the scope of this Layer 1 document** and are deferred to subsequent specifications.

**方式：** 波束変調合成 (WPMS) のみ。サイドバンドフラクタル合成、任意のビン別パラメータを持つ加算合成、SDFT 分析は**本第1層文書の範囲外**であり、後続の仕様に延期される。

**Mathematical formulation:** Each bin k ∈ {0, 1, ..., N−1} contributes a sinusoidal component whose frequency, amplitude, and phase are closed-form functions of k and a small set of scalar parameters:

**数学的定式化：** 各ビン k ∈ {0, 1, ..., N−1} は、その周波数、振幅、位相が k と少数のスカラーパラメータの閉形式関数となる正弦波成分を寄与する：

```
f_k = f₀ + k · Δf + α · k²
A_k = A₀ · exp(−β · k) · exp(−γ · (k − N/2)²)
φ_k = φ₀ + k · δφ + ψ · k²
```

**Free parameters:**

**自由パラメータ：**

| Symbol | Meaning | Role |
|---|---|---|
| f₀ | Fundamental (lowest bin) frequency | Center of the wave packet |
| Δf | Linear frequency spacing | Bin density |
| α | Quadratic frequency spread | Inharmonicity / chirp |
| A₀ | Peak amplitude | Overall level |
| β | Exponential amplitude decay | Spectral tilt |
| γ | Gaussian amplitude weighting | Wave-packet smoothness |
| φ₀ | Phase at k = 0 | Global phase offset |
| δφ | Linear phase gradient | Group delay (time shift) |
| ψ | Quadratic phase coefficient | Linear chirp / pulse compression |
| N | Number of active bins | Wave packet sharpness / count |

**Total: nine scalar parameters plus one count parameter.**

**合計：9 個のスカラーパラメータと 1 個の数量パラメータ。**

**Phenomenological span of the parameter space:**

**パラメータ空間の現象学的広がり：**

- All five modulation parameters at zero (α = β = γ = δφ = ψ = 0) and uniform amplitude → pure Dirichlet kernel; sharp metallic transient with sinc-shaped envelope. **This is the test-origin configuration**, which the 2020 prototype experiment validated. / 5 つの変調パラメータすべてが 0（α = β = γ = δφ = ψ = 0）かつ一様振幅 → 純粋な Dirichlet カーネル。sinc 状の包絡を持つ鋭い金属的な過渡音。**これはテスト原点構成**であり、2020 年プロトタイプ実験で検証済みである。
- Non-zero γ → Gaussian wave packet; smooth bell-like envelope. / 非ゼロ γ → ガウシアン波束。滑らかな鐘状包絡。
- Non-zero ψ → linear chirp pulse; radar-pulse-like swept tone. / 非ゼロ ψ → 線形チャープパルス。レーダーパルス状の掃引音。
- Small non-zero α → mildly stretched harmonic series; piano-like inharmonicity. / 小さな非ゼロ α → 弱く拡張された倍音列。ピアノ状のイナハーモニシティ。
- Non-zero δφ → group-delay-shifted packet; spatial / chorus-like effect. / 非ゼロ δφ → 群遅延シフトされた波束。空間的・コーラス状の効果。

**Why WPMS rather than full additive:**

**なぜフル加算合成ではなく WPMS なのか：**

- WPMS expresses each bin's parameters as a closed-form polynomial function of bin index k. **No per-bin parameter memory is required** — neither BRAM nor DPRAM. The pipeline stage that computes f_{k+1} from f_k uses a single accumulator and a small constant register set (the difference-engine structure named in Theme 4 of the 2026-04-18 reasoning trace, the *Polynomial Bin-Sequence Pattern*). / WPMS は各ビンのパラメータをビン番号 k の閉形式多項式関数として表現する。**ビン別パラメータメモリは要求されない**——BRAM も DPRAM も。f_k から f_{k+1} を計算するパイプライン段は、単一の累算器と小さな定数レジスタ群（2026-04-18 推論軌跡のテーマ 4 で命名された差分エンジン構造、*多項式ビン系列パターン*）を用いる。
- This makes WPMS the simplest possible implementation that exercises the full Maclaurin pipeline at audio rates with non-trivial frequency, amplitude, and phase dynamics. / これにより WPMS は、自明でない周波数・振幅・位相のダイナミクスを伴ってマクローリンパイプライン全体をオーディオレートで動作させる、可能な限り最も単純な実装となる。
- The mathematics generalizes: should fractal synthesis or arbitrary per-bin parameters be required later, the same pipeline accepts them by replacing the difference-engine output with a memory-fetched parameter vector. WPMS is the polynomial-difference *case* of a more general bin-parameter sourcing architecture. / 数学は一般化する：フラクタル合成や任意のビン別パラメータが後に要求される場合でも、差分エンジン出力をメモリ取得パラメータベクトルに置き換えることで、同じパイプラインがそれらを受け入れる。WPMS はより一般的なビンパラメータ供給アーキテクチャの多項式差分*ケース*である。

---

## 1.5 Bin Count and Module Configuration / ビン数とモジュール構成

**Decision: Tie — multiple module configurations are kept in the Implementation Arena.**

**決定：引き分け — 複数のモジュール構成を Implementation Arena に保持する。**

The Layer 1 specification recognizes three logically equivalent module configurations:

第1層仕様は、3 つの論理的に等価なモジュール構成を認める：

| Configuration | Modules | Bins | Target Platform |
|---|---|---|---|
| **Compact** | 2 modules × 2,048 bins | 4,096 | DE10-nano (this document's reference) |
| **Standard** | 5 modules × 2,048 bins | 10,240 | C5G-equivalent on DE10-nano (subject to timing) |
| **Extended** | 10 modules × 2,048 bins | 20,480 | DE25-nano or larger (anticipated, out of scope here) |

**Logical equivalence:** At the source-level architecture, the three configurations differ only in the value of a single `generate` parameter that instantiates the module count. The Maclaurin pipeline, the sequence-modulation pipeline processor, the per-module bin allocation, and the summation tree structure are all parameterized to accept any value M ∈ {2, 5, 10, ...} at compile time.

**論理的等価性：** ソースレベルアーキテクチャにおいて、3 つの構成はモジュール数をインスタンス化する単一の `generate` パラメータの値においてのみ異なる。マクローリンパイプライン、数列変調パイプラインプロセッサ、モジュールごとのビン配分、総和ツリー構造はすべてパラメータ化されており、コンパイル時に任意の値 M ∈ {2, 5, 10, ...} を受け入れる。

**Implementation reality is not the same as logical equivalence.** As module count rises, implementation-level pressures emerge non-linearly:

**実装現実は論理的等価性と同じではない。** モジュール数が上昇するにつれ、実装レベルの圧力が非線形に立ち現れる：

- Routing congestion as the summation tree fan-in grows / 総和ツリーのファンインが増大するにつれての配線輻輳
- Clock-tree skew across distributed pipeline stages / 分散パイプライン段にわたるクロックツリースキュー
- BRAM port contention if multiple modules access shared memory / 複数モジュールが共有メモリにアクセスする場合の BRAM ポート競合
- DSP block placement across the device's DSP columns / デバイスの DSP カラムにわたる DSP ブロック配置
- Fmax erosion as critical paths lengthen / クリティカルパスが長くなるにつれての Fmax の侵食

**Each module-count threshold is a real engineering frontier.** Crossing it typically requires implementation-level work — pipeline retiming, register replication, manual placement constraints, sometimes architectural refinements that raise the achievable Fmax. **Such Fmax improvements can in turn unlock the next module-count tier**, creating a recursive expansion path that is not predictable from the logical specification alone.

**各モジュール数の閾値は本物の工学的前線である。** これを越えるには通常、実装レベルの作業——パイプラインリタイミング、レジスタ複製、手動配置制約、時にはアーキテクチャの洗練によって達成可能 Fmax を引き上げること——が要求される。**そのような Fmax の改善は、今度は次のモジュール数階層を解錠し得る**——論理仕様単独では予測不能な再帰的拡張経路を作り出す。

**This phenomenon is one of the strongest reasons for the existence of Open Prompt as a methodology.** The reasoning behind a specific Fmax breakthrough — what was tried, what failed, what timing reports said, what the decisive trade-off was — is precisely the kind of knowledge that does not survive in source code alone. It must be preserved as Layer 2 reasoning traces. A future implementer porting to DE25-nano three years from now should be able to load these traces into their LLM collaborator and recover not just the code but the **judgment** behind the code.

**この現象は、方法論としての Open Prompt の存在理由の最も強いものの一つである。** 特定の Fmax 突破の背後にある推論——何を試み、何が失敗し、タイミングレポートが何を言い、決定的なトレードオフが何だったか——は、まさにソースコード単独では生き残らない種類の知識である。それは第2層推論軌跡として保存されねばならない。3 年後に DE25-nano に移植する将来の実装者は、これらの軌跡を LLM 協働者にロードし、コードだけでなくコードの背後にある**判断**を回復できるべきである。

**Reference implementation choice for Layer 3:**

**第3層リファレンス実装の選択：**

The first reference implementation provided in Layer 3 will use the **Compact configuration (2 modules, 4,096 bins)**. This is selected as the starting point for three reasons:

第3層で提供される最初のリファレンス実装は **Compact 構成（2 モジュール、4,096 ビン）** を用いる。これは 3 つの理由により出発点として選定される：

1. Compact has the highest probability of timing closure on DE10-nano on first attempt, ensuring the inaugural release works for all readers. / Compact は初回試行で DE10-nano 上でのタイミング収束確率が最も高く、最初のリリースがすべての読者で動作することを保証する。
2. Compact has comfortable DSP budget, allowing the 11th-order Maclaurin polynomial and 24-bit amplitude width to be retained. / Compact は快適な DSP 予算を持ち、11 次マクローリン多項式と 24 ビット振幅幅の維持を可能にする。
3. The progression Compact → Standard → Extended provides clear motivating boundaries for future Layer 2 reasoning traces, each documenting an Fmax-threshold breakthrough. / Compact → Standard → Extended の進展は、それぞれ Fmax 閾値突破を文書化する将来の第2層推論軌跡に対する、明確な動機付けの境界を提供する。

The Standard and Extended configurations are explicitly invited as community contributions. The bin-count choice itself is therefore a **Tie Decision** in the Implementation Arena, with the Compact starting point being a *first-implementation* convention rather than an architectural commitment.

Standard と Extended の構成はコミュニティ貢献として明示的に招待される。したがってビン数の選択そのものが Implementation Arena における**引き分け判断**であり、Compact 出発点はアーキテクチャ的コミットメントではなく*最初の実装*の慣行である。

---

## 1.6 Maclaurin Pipeline Configuration / マクローリンパイプライン構成

**Polynomial degree:** 11th-order Maclaurin expansion of sin(x), retained from the C5G prototype.

**多項式次数：** sin(x) の 11 次マクローリン展開、C5G プロトタイプから継承。

**Internal bit widths (Compact-configuration reference):**

**内部ビット幅（Compact 構成基準）：**

| Stage | Width | Format |
|---|---|---|
| Trigonometric core | 40 bits | signed fixed-point |
| Amplitude (level) multiplier | 24 bits | unsigned fixed-point (Compact configuration retains C5G-era width) |
| Per-module summation accumulator | 64 bits | signed fixed-point |
| Output to HDMI audio path | 24 bits | signed PCM |
| Final decimal-point selector | 6-bit shift | DIP-switch-controlled (3 DIP positions × 2 bits resolution) |

The 11th-order / 24-bit retention is permitted by the Compact configuration's reduced module count: with only 2 modules instead of 5, DSP-block budget is comfortable on DE10-nano (2 modules × ~20 DSP ≈ 40 DSP for the iDFT/WPMS pipelines, with ~72 DSP remaining for the sequence-modulation processor, the HDMI core, and other subsystems).

11 次／24 ビットの維持は、Compact 構成の縮小されたモジュール数により許容される：5 モジュールではなく 2 モジュールのみで、DSP ブロック予算は DE10-nano 上で快適である（2 モジュール × 約 20 DSP ≈ 40 DSP が iDFT/WPMS パイプライン用、約 72 DSP が数列変調プロセッサ、HDMI コア、その他のサブシステム用に残る）。

**For Standard and Extended configurations**, polynomial degree and amplitude bit-width may be reduced (e.g., 7th-order Maclaurin and 16-bit amplitude) as discussed in the 2026-04-18 reasoning trace decision-point DP-9. Such trade-offs are recorded as Implementation Arena variants when they are realized.

**Standard と Extended の構成では**、2026-04-18 推論軌跡の決定点 DP-9 で議論されたように、多項式次数と振幅ビット幅は削減され得る（7 次マクローリンと 16 ビット振幅など）。そのようなトレードオフは、それらが実現される時点で Implementation Arena の変種として記録される。

**Detailed pipeline architecture:** Deferred to Chapter 2 (Maclaurin Pipeline Specification), to be drafted in subsequent dialogue.

**詳細パイプラインアーキテクチャ：** 第 2 章（マクローリンパイプライン仕様）に委ね、後続の対話で起草される。

---

## 1.7 Sequence-Modulation Pipeline Processor / 数列変調パイプラインプロセッサ

**Role:** The sequence-modulation pipeline processor is the WPMS-specific component that computes per-bin parameters (f_k, A_k, φ_k) on the fly, using the difference-engine structure rather than per-bin memory storage.

**役割：** 数列変調パイプラインプロセッサは WPMS 固有の構成要素であり、ビンごとのパラメータ (f_k, A_k, φ_k) を、ビン別メモリ記憶ではなく差分エンジン構造を用いてオンザフライで計算する。

**Recurrences (one accumulator update per bin transition):**

**漸化式（ビン遷移ごとに 1 回の累算器更新）：**

```
f_{k+1} = f_k + (Δf + α) + 2α · k
φ_{k+1} = φ_k + (δφ + ψ) + 2ψ · k
A_{k+1} = A_k · exp(−β) · exp(−γ · (2k − N + 1))
```

The frequency and phase recurrences require only addition; no multiplier is consumed beyond what the Maclaurin core already uses for its trigonometric computation. The amplitude recurrence multiplies the previous amplitude by a small dynamic factor; this can be implemented either with a single dedicated DSP block per module or with log-domain accumulation.

周波数と位相の漸化式は加算のみを要求する。マクローリンコアがすでにその三角関数計算に用いている以上の乗算器は消費されない。振幅の漸化式は前段の振幅を小さな動的因子で乗じる。これはモジュールあたり 1 個の専用 DSP ブロックで実装するか、対数領域累算で実装するかのいずれかが可能である。

**Detailed processor architecture:** Deferred to Chapter 3 (Sequence-Modulation Pipeline Processor Specification), to be drafted in subsequent dialogue. Parameter bit-widths for f₀, A₀, φ₀, Δf, α, β, γ, δφ, ψ, and N are specified there.

**詳細プロセッサアーキテクチャ：** 第 3 章（数列変調パイプラインプロセッサ仕様）に委ね、後続の対話で起草される。f₀, A₀, φ₀, Δf, α, β, γ, δφ, ψ, N のパラメータビット幅はそこで指定される。

**Component reusability commitment:** The sequence-modulation pipeline processor is designed not for WPMS alone but as a **general-purpose per-bin parameter computation engine**. Its instruction set, register architecture, and AXI interface are specified such that, in subsequent FPGA Spectrum Engine development phases, the same processor can compute fractal-synthesis bin parameters, SDFT bin parameters, or hybrid combinations. Component carry-forward to the next development phase is a hard requirement on the Chapter 3 specification.

**部品再利用コミットメント：** 数列変調パイプラインプロセッサは WPMS 単独のためではなく、**汎用的なビン別パラメータ計算エンジン**として設計される。その命令セット、レジスタアーキテクチャ、AXI インターフェースは、後続の FPGA Spectrum Engine 開発フェーズにおいて、同じプロセッサがフラクタル合成のビンパラメータ、SDFT のビンパラメータ、またはハイブリッド組み合わせを計算できるように指定される。次の開発フェーズへの部品の持ち越しは、第 3 章仕様に対する厳格な要件である。

---

## 1.8 Input Interface — Required Subset / 入力インターフェース — 必須部

The required input interfaces are sufficient to operate the WPMS Synthesizer with full parameter coverage and to perform live experimentation with parameter values. They require no hardware beyond the DE10-nano itself, the host PC running Quartus, and the JTAG cable that ships with the board.

必須入力インターフェースは、WPMS シンセサイザーをフルパラメータカバーで動作させ、パラメータ値の実時間実験を行うのに十分である。DE10-nano 本体、Quartus を動作させるホスト PC、ボード付属の JTAG ケーブル以外のハードウェアを要求しない。

**Interface 1 — DIP switches and push buttons.**

**インターフェース 1 — DIP スイッチと押しボタン。**

The DE10-nano provides 4 user DIP switches and 2 user push buttons. These are mapped as follows in the Compact configuration:

DE10-nano は 4 個のユーザ DIP スイッチと 2 個のユーザ押しボタンを提供する。Compact 構成では以下のようにマップされる：

- **DIP[1:0]:** Output amplitude headroom selector (final decimal-point shift, 4 positions). / 出力振幅ヘッドルームセレクタ（最終 decimal-point シフト、4 位置）。
- **DIP[2]:** Reset hold (active high; deassert to start synthesis after parameter load). / リセット保持（アクティブハイ；パラメータロード後に解除して合成開始）。
- **DIP[3]:** Audio mute (force HDMI audio output to zero independent of synthesizer state). / オーディオミュート（合成器状態に関係なく HDMI オーディオ出力をゼロに強制）。
- **KEY[0]:** Parameter snapshot trigger (commits the current target parameters to the active set; rising-edge sensitive). / パラメータスナップショットトリガ（現在のターゲットパラメータをアクティブセットにコミット；立ち上がりエッジ感知）。
- **KEY[1]:** Test-origin restore (loads α = β = γ = δφ = ψ = 0, default f₀, A₀, φ₀, N = 2,048; produces pure Dirichlet kernel). / テスト原点復元（α = β = γ = δφ = ψ = 0、デフォルトの f₀, A₀, φ₀, N = 2,048 をロード；純粋な Dirichlet カーネルを生成）。

KEY[1] is significant: it makes the 2020-prototype-validated test-origin configuration always one button-press away. This is the first configuration any new user should hear.

KEY[1] は意義深い：2020 年プロトタイプで検証されたテスト原点構成を、常にボタン押下 1 回の距離に置く。これは新規ユーザが最初に聴くべき構成である。

**Interface 2 — In-System Sources and Probes (ISSP, JTAG-based).**

**インターフェース 2 — In-System Sources and Probes（ISSP、JTAG ベース）。**

ISSP provides Quartus-side widgets that drive register inputs and observe register outputs over JTAG, with no additional hardware. The WPMS Synthesizer exposes all nine scalar parameters and the count parameter as ISSP source registers. Each parameter has a dedicated source register sized for its full bit width.

ISSP は Quartus 側のウィジェットを提供し、JTAG 経由でレジスタ入力を駆動しレジスタ出力を観察する。追加ハードウェアは不要。WPMS シンセサイザーは 9 個のスカラーパラメータすべてと数量パラメータを ISSP ソースレジスタとして公開する。各パラメータはその完全なビット幅にサイズされた専用ソースレジスタを持つ。

ISSP probes additionally expose, for diagnostic purposes:

ISSP プローブは追加で、診断目的のため以下を公開する：

- The current f_k, A_k, φ_k for a selectable bin index (a "bin inspector" probe). / 選択可能なビン番号についての現在の f_k, A_k, φ_k（"ビンインスペクタ" プローブ）。
- The summation accumulator value at sample boundaries. / サンプル境界における総和累算器値。
- Pipeline overflow / saturation flags. / パイプラインオーバーフロー／飽和フラグ。

**Interface 3 — In-System Memory Content Editor (ISMCE, JTAG-based).**

**インターフェース 3 — In-System Memory Content Editor（ISMCE、JTAG ベース）。**

For configurations that include any BRAM-resident parameter table (e.g., for future fractal-mode experiments that share infrastructure with WPMS), ISMCE provides edit access. In the pure WPMS Compact configuration, ISMCE is not strictly required, since all parameters are register-resident. ISMCE remains specified here so that the same Quartus project can be rebuilt with optional BRAM extensions without revising the input-interface specification.

WPMS と基盤を共有する将来のフラクタルモード実験のための、いかなる BRAM 常駐パラメータテーブルを含む構成においても、ISMCE は編集アクセスを提供する。純粋な WPMS Compact 構成では、すべてのパラメータがレジスタ常駐であるため、ISMCE は厳密には要求されない。同じ Quartus プロジェクトが入力インターフェース仕様を改訂することなくオプションの BRAM 拡張で再構築できるよう、ISMCE はここに仕様される。

**Persistence:** ISSP and ISMCE persistence is the responsibility of the user (manual save of Quartus probe sessions). The WPMS Synthesizer itself does not store parameters in non-volatile memory; on power cycle, the FPGA resets to a built-in default that is identical to the KEY[1] test-origin restore.

**永続化：** ISSP と ISMCE の永続化はユーザの責任である（Quartus プローブセッションの手動保存）。WPMS シンセサイザー自体はパラメータを不揮発性メモリに記憶しない；電源サイクル時、FPGA は KEY[1] テスト原点復元と同一の組み込みデフォルトにリセットされる。

---

## 1.9 Input Interface — Optional Extension (Camera Modulation Source) / 入力インターフェース — オプション拡張（カメラ変調源）

**Status:** Optional extension. The WPMS Synthesizer is fully functional without it. This section is included so that the architectural decisions in this Layer 1 document preserve compatibility with the camera extension; it is not a mandatory build target.

**ステータス：** オプション拡張。WPMS シンセサイザーはこれなしで完全に機能する。本節は、本第1層文書のアーキテクチャ的決定がカメラ拡張との互換性を保持するために含まれている；必須のビルドターゲットではない。

**Camera selection:** OmniVision OV7670 (parallel DVP, 8-bit, QVGA-VGA, ≤ 30 fps). The selection is dictated by physical availability of the device and by the abundance of FPGA-direct examples in publicly accessible documentation.

**カメラの選定：** OmniVision OV7670（パラレル DVP、8 ビット、QVGA-VGA、≤ 30 fps）。選定はデバイスの物理的可用性と、公的にアクセス可能な文書における FPGA 直結例の豊富さによって規定される。

**Connection:** OV7670 connects to one of the DE10-nano's 2×20 GPIO headers via the OV7670's parallel DVP interface (D[7:0], HSYNC, VSYNC, PCLK, XCLK, plus SCCB clock and data — approximately 13 GPIO pins).

**接続：** OV7670 は、OV7670 のパラレル DVP インターフェース（D[7:0]、HSYNC、VSYNC、PCLK、XCLK、加えて SCCB クロックとデータ——約 13 個の GPIO ピン）を介して、DE10-nano の 2×20 GPIO ヘッダの 1 つに接続する。

**Architectural role: stimulus source for parameter modulation, behind an AXI-abstracted input switch.**

**アーキテクチャ的役割：AXI 抽象化入力スイッチの背後にある、パラメータ変調のためのスティミュラス源。**

The camera block is implemented as a self-contained FPGA subsystem with the following structure:

カメラブロックは、以下の構造を持つ自己完結型 FPGA サブシステムとして実装される：

1. **Camera driver:** Generates SCCB initialization, latches D[7:0] on PCLK, tracks HSYNC/VSYNC. / カメラドライバ：SCCB 初期化を生成し、PCLK で D[7:0] をラッチし、HSYNC/VSYNC を追跡する。
2. **Frame aggregator:** Computes from each captured frame the centroid (cx, cy), the variance (σx², σy²), the inter-frame difference magnitude, and the global mean intensity. These six aggregate values are the camera block's external output. / フレーム集計器：各キャプチャフレームから重心 (cx, cy)、分散 (σx², σy²)、フレーム間差分の大きさ、全体の平均輝度を計算する。これら 6 個の集計値がカメラブロックの外部出力となる。
3. **Mapping template (initial draft):** cx → α, cy → β, σx² → γ, σy² → δφ, inter-frame diff → ψ, global mean → A₀. The mapping is intentionally exposed as a configurable lookup so that experimenters can substitute alternative mappings. / マッピングテンプレート（初期ドラフト）：cx → α、cy → β、σx² → γ、σy² → δφ、フレーム間差分 → ψ、全体平均 → A₀。マッピングは意図的に構成可能なルックアップとして公開され、実験者が代替マッピングを置き換えられる。
4. **AXI input switch:** The camera block's six aggregate outputs feed an AXI-Stream-style input switch. The switch's other input is from the ISSP-driven manual parameter source. A control register selects which source drives the live parameters of the sequence-modulation processor. / AXI 入力スイッチ：カメラブロックの 6 個の集計出力は AXI-Stream 様式の入力スイッチに供給される。スイッチのもう一方の入力は ISSP 駆動の手動パラメータ源からのものである。制御レジスタがどちらのソースが数列変調プロセッサのライブパラメータを駆動するかを選択する。

**Why the AXI abstraction matters:**

**なぜ AXI 抽象化が重要なのか：**

The AXI input switch is **the structural commitment that allows the camera block to outlive the WPMS Synthesizer phase**. In subsequent FPGA Spectrum Engine development phases, the same input switch can route AXI traffic from the HPS (in the ARM intermediate layer) or from synthesized video sources or from arbitrary external modulation sources. The camera block, once authored, becomes a permanent component of the engine's modulation-source library — not a throwaway element of the standalone phase.

AXI 入力スイッチは、**カメラブロックが WPMS シンセサイザーフェーズを超えて生き残ることを可能にする構造的コミットメント**である。後続の FPGA Spectrum Engine 開発フェーズにおいて、同じ入力スイッチが、HPS（ARM 中間層）からの、または合成ビデオソースからの、または任意の外部変調ソースからの AXI トラフィックを経路づけることができる。カメラブロックは、一度作成されれば、独立フェーズの使い捨て要素ではなく、エンジンの変調源ライブラリの永続的な構成要素となる。

**Spin-Off-Ready Subsystem framing:** The camera block is structured such that an independent project — a "Real-Time Video Processing on FPGA" Open Prompt repository — could fork only this subsystem and develop it on its own trajectory without dragging the WPMS Synthesizer along. This is an explicit invitation: should community members find the camera-block direction more compelling than the synthesizer-block direction, the architecture supports their specialization. The sequence-modulation pipeline processor and the WPMS synthesis core do not depend on any specific behavior of the camera block beyond the AXI interface contract.

**Spin-Off-Ready Subsystem フレーミング：** カメラブロックは、独立したプロジェクト——「FPGA 上のリアルタイム映像処理」Open Prompt リポジトリ——がこのサブシステムのみをフォークし、WPMS シンセサイザーを引きずることなく独自の軌跡で発展させ得るよう構造化される。これは明示的な招待である：コミュニティメンバーがカメラブロックの方向性をシンセサイザーブロックの方向性より魅力的と感じる場合、アーキテクチャは彼らの専門化を支持する。数列変調パイプラインプロセッサと WPMS 合成コアは、AXI インターフェース契約以上にはカメラブロックの特定の挙動に依存しない。

**Detailed camera-block specification:** Deferred to a separate optional chapter to be drafted after the required-subset chapters are complete.

**詳細カメラブロック仕様：** 必須サブセットの章が完了した後に起草される、別個のオプション章に委ねる。

---

## 1.10 What is NOT in this Layer 1 Document / 本第1層文書に含まれないもの

To make the boundary unambiguous:

境界を曖昧でなくするために：

- **HPS / ARM software.** No Linux, bootloader, device tree, or HPS firmware. Should the SD card boot the HPS, the HPS must be held in reset or be running an idle loop. / HPS / ARM ソフトウェア。Linux、ブートローダ、デバイスツリー、HPS ファームウェアなし。SD カードが HPS をブートする場合、HPS はリセット保持されるか、アイドルループを実行していなければならない。
- **MIDI input.** No MIDI parsing, no MIDI controller support. Parameter input is via DIP/buttons, ISSP, ISMCE, or (optionally) camera only. / MIDI 入力。MIDI 解析なし、MIDI コントローラサポートなし。パラメータ入力は DIP/ボタン、ISSP、ISMCE、または（オプションで）カメラのみを介する。
- **OSC, Ethernet, USB.** No network connectivity. The DE10-nano's Ethernet PHY and USB OTG ports are unused in this specification. / OSC、Ethernet、USB。ネットワーク接続性なし。DE10-nano の Ethernet PHY と USB OTG ポートは本仕様で未使用である。
- **Reverberation, perceptual masking, MP3-class processing.** All of these are anticipated future features of the FPGA Spectrum Engine but are out of scope for the WPMS Synthesizer. / 残響、知覚マスキング、MP3 クラス処理。これらはすべて FPGA Spectrum Engine の予期される将来機能だが、WPMS シンセサイザーのスコープ外である。
- **SDFT analysis, fractal synthesis.** Out of scope for this synthesizer. Architectural compatibility with future addition is preserved (e.g., the AXI input switch, the parameterized module count, the general-purpose sequence-modulation processor) but no SDFT or fractal logic is built. / SDFT 分析、フラクタル合成。本シンセサイザーのスコープ外である。将来追加とのアーキテクチャ的互換性は保持される（AXI 入力スイッチ、パラメータ化されたモジュール数、汎用数列変調プロセッサなど）が、SDFT またはフラクタルロジックは構築されない。
- **Polyphony in the conventional sense.** WPMS treats the entire bin space as a single wave packet, not as a collection of independent "voices." There is one packet at any moment, parameterized by the nine scalars. Multi-packet superposition (e.g., a chord built from multiple WPMS packets) requires either time-multiplexing or further architectural extension and is out of scope here. / 従来的意味でのポリフォニー。WPMS はビン空間全体を独立した「ボイス」の集合ではなく、単一の波束として扱う。任意の時点で 1 つの波束があり、9 個のスカラーでパラメータ化される。マルチパケット重ね合わせ（複数 WPMS 波束で構築される和音など）は時分割多重化または追加のアーキテクチャ拡張を要求し、本仕様のスコープ外である。

---

## 1.11 Validation Origin / 検証起点

**The first regression test.** The KEY[1] test-origin restore loads:

**最初のリグレッションテスト。** KEY[1] テスト原点復元は以下をロードする：

```
α = β = γ = δφ = ψ = 0
f₀ = configuration default (proposed: 996 Hz to match the 2020 prototype)
Δf = configuration default (proposed: 1/256 Hz to match the 2020 prototype)
A₀ = 0.97 × full scale (matching the 2020 prototype)
φ₀ = 0
N = 2,048
```

This produces, by construction, a Dirichlet kernel whose audible result matches the 2020 prototype recording. **A WPMS Synthesizer implementation is considered to have passed its first regression test when its KEY[1] output matches the 2020 prototype waveform within the precision dictated by the chosen output bit-width.**

これは構造上、その可聴結果が 2020 年プロトタイプ録音に一致する Dirichlet カーネルを生成する。**WPMS シンセサイザー実装は、その KEY[1] 出力が、選定された出力ビット幅により規定される精度内で 2020 年プロトタイプ波形に一致した時、最初のリグレッションテストを通過したとみなされる。**

This single test exercises every critical subsystem simultaneously: bin-parameter generation (uniform progression), Maclaurin computation (correct sin values across 2,048 phases), summation tree (no overflow, no precision loss), HDMI audio path (correct sample rate and format), and DIP/key handling (correct loading of the test-origin parameters). Any defect anywhere in the synthesizer manifests as a deviation in the Dirichlet kernel waveform.

この単一テストはすべての重要なサブシステムを同時に行使する：ビンパラメータ生成（一様な進行）、マクローリン計算（2,048 位相にわたる正しい sin 値）、総和ツリー（オーバーフローなし、精度損失なし）、HDMI オーディオパス（正しいサンプルレートと形式）、DIP/キー処理（テスト原点パラメータの正しいロード）。シンセサイザーのどこかにある欠陥はすべて、Dirichlet カーネル波形における偏差として現れる。

The diagnostic strength of this test mirrors the "First Sound" coherence test of the original C5G prototype: the boring uniform output is paradoxically the strongest possible test signal, because any error anywhere produces immediate decoherence visible in the waveform.

このテストの診断強度はオリジナル C5G プロトタイプの「First Sound」コヒーレンステストを反映する：退屈な一様出力は逆説的に可能な限り最強のテスト信号である。どこかの任意のエラーが、波形に見える即時のデコヒーレンスを生み出すからである。

---

## 1.12 Open Questions Carried Forward to Subsequent Chapters / 後続章へ持ち越される未解決問題

The following are deliberately left unresolved in this chapter and will be addressed in subsequent chapters of this Layer 1 specification:

以下は意図的に本章で未解決のまま残され、本第1層仕様の後続章で扱われる：

| Question | Deferred to |
|---|---|
| Pipeline depth, retiming strategy, DSP-block placement strategy for the Maclaurin core / マクローリンコアのパイプライン深度、リタイミング戦略、DSP ブロック配置戦略 | Chapter 2 / 第 2 章 |
| Bit widths for the nine scalar parameters and N / 9 個のスカラーパラメータと N のビット幅 | Chapter 3 / 第 3 章 |
| Instruction set and register architecture of the sequence-modulation pipeline processor / 数列変調パイプラインプロセッサの命令セットとレジスタアーキテクチャ | Chapter 3 / 第 3 章 |
| Choice of MiSTer-ecosystem HDMI core and integration details / MiSTer エコシステム HDMI コアの選定と統合詳細 | Chapter 4 / 第 4 章 |
| AXI input switch protocol and register map / AXI 入力スイッチプロトコルとレジスタマップ | Chapter 5 / 第 5 章 |
| Camera-block frame-aggregator details, mapping template specification / カメラブロックフレーム集計器詳細、マッピングテンプレート仕様 | Optional camera chapter / オプションカメラ章 |
| Reference-implementation HDL, build flow, `.rbf` packaging / リファレンス実装 HDL、ビルドフロー、`.rbf` パッケージング | Layer 3, separate document / 第 3 層、別文書 |

---

## 1.13 Summary of Chapter 1 Decisions / 第 1 章決定事項のまとめ

| ID | Decision | Status |
|---|---|---|
| C1-D1 | Target platform: DE10-nano (Cyclone V SoC), FPGA fabric only, HPS unused / 対象プラットフォーム：DE10-nano（Cyclone V SoC）、FPGA ファブリックのみ、HPS 未使用 | Fixed / 確定 |
| C1-D2 | Audio output: HDMI audio at 48 kHz / 24-bit, MiSTer-ecosystem core / オーディオ出力：HDMI オーディオ 48 kHz / 24-bit、MiSTer エコシステムコア | Fixed / 確定 |
| C1-D3 | Synthesis method: WPMS only, nine-scalar-plus-N parameter space / 合成方式：WPMS のみ、9 スカラー + N のパラメータ空間 | Fixed / 確定 |
| C1-D4 | Bin count and module configuration: Tie. Compact (2 × 2,048), Standard (5 × 2,048), Extended (10 × 2,048) all in Implementation Arena / ビン数とモジュール構成：引き分け。Compact、Standard、Extended すべてを Implementation Arena に保持 | Tie / 引き分け |
| C1-D5 | Reference implementation: Compact configuration first / リファレンス実装：Compact 構成を最初に | Convention, not commitment / 慣行であり、コミットメントではない |
| C1-D6 | Maclaurin pipeline: 11th-order, 40-bit trig, 24-bit amplitude (Compact) / マクローリンパイプライン：11 次、40-bit 三角関数、24-bit 振幅（Compact） | Fixed for Compact / Compact について確定 |
| C1-D7 | Sequence-modulation processor: difference-engine structure, general-purpose AXI interface, designed for carry-forward to subsequent FPGA Spectrum Engine phases / 数列変調プロセッサ：差分エンジン構造、汎用 AXI インターフェース、後続 FPGA Spectrum Engine フェーズへの持ち越し設計 | Fixed / 確定 |
| C1-D8 | Required input: DIP + buttons, ISSP, ISMCE / 必須入力：DIP + ボタン、ISSP、ISMCE | Fixed / 確定 |
| C1-D9 | Optional input: OV7670 camera via GPIO, behind AXI input switch, Spin-Off-Ready / オプション入力：GPIO 経由 OV7670 カメラ、AXI 入力スイッチの背後、Spin-Off-Ready | Optional, structurally enabled / オプション、構造的に有効化 |
| C1-D10 | Validation origin: Dirichlet kernel via KEY[1] test-origin restore / 検証起点：KEY[1] テスト原点復元による Dirichlet カーネル | Fixed / 確定 |

---

## End of Chapter 1 / 第 1 章の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *The shortest path from a repository to a sound is the foundation on which longer paths are built.*
> *リポジトリから音への最短経路は、より長い経路がその上に構築される基礎である。*

This chapter is released into the public domain under CC0 1.0 Universal. Subsequent chapters (Chapter 2: Maclaurin Pipeline Specification, Chapter 3: Sequence-Modulation Pipeline Processor, Chapter 4: HDMI Audio Path, Chapter 5: AXI Input Switch, Optional Camera Chapter) will be drafted in subsequent dialogues.

本章は CC0 1.0 Universal のもとパブリックドメインに公開される。後続の章（第 2 章：マクローリンパイプライン仕様、第 3 章：数列変調パイプラインプロセッサ、第 4 章：HDMI オーディオパス、第 5 章：AXI 入力スイッチ、オプションのカメラ章）は後続の対話で起草される。
