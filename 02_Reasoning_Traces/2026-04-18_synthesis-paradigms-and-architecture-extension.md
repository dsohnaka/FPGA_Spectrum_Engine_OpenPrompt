# Synthesis Paradigms, Architecture Extension, and the Discovery of WPMS / 合成パラダイム、アーキテクチャ拡張、そして波束変調合成 (WPMS) の発見

## Trace Metadata / 軌跡メタデータ

| Field | Value |
|---|---|
| **Date / 日付** | 2026-04-18 〜 2026-04-28 (multi-day technical dialogue) |
| **Participants / 参加者** | Tsuneo Ohnaka (FPGA Architect, 40+ years); Claude (Anthropic, Claude Opus 4.6) |
| **Topic / トピック** | Architectural extension of the C5G iDFT engine — burst convolution and reverberation, levelizer and slew-rate control, dynamic frequency/phase control, sideband fractal synthesis, SDFT integration, perceptual compression, and the inductive discovery of Wave Packet Modulation Synthesis (WPMS) |
| **Status / 状態** | Layer 2 trace — single-AI multi-day technical exploration / 第2層軌跡 — 単一AI複数日技術探索 |
| **Original language / 原言語** | Japanese (with English technical terminology) / 日本語（英語技術用語を交える） |
| **License / ライセンス** | CC0 1.0 Universal (Public Domain) |

---

## Reading Notes / 読解上の注

This trace covers a multi-day technical dialogue exploring how the existing C5G prototype iDFT engine — already validated by the 2020 Dirichlet kernel and First Sound experiments — can be extended along several orthogonal axes. The conversation begins with a question about FM sidebands and reverberation in the frequency domain, naturally leads into the architectural details of the existing engine, and progressively uncovers new synthesis paradigms that the same hardware can support without fundamental redesign.

本軌跡は、既存の C5G プロトタイプ iDFT エンジン——2020 年の Dirichlet カーネル実験と First Sound 実験ですでに検証済み——を、いくつかの直交する軸に沿ってどう拡張できるかを探究する複数日技術対話を扱う。会話は周波数領域における FM サイドバンドと残響についての問いから始まり、自然に既存エンジンのアーキテクチャ詳細へと進み、漸進的に、ハードウェア再設計なしに同じハードウェアが支持できる新しい合成パラダイムを発掘していく。

**Marketing-related discussions (community outreach, target audience, presentation strategy) are intentionally excluded from this trace. The focus is purely technical: what the engine is, what it can become, and the design decisions on the path between the two.**

**マーケティング関連の議論（コミュニティ・アウトリーチ、ターゲット層、発表戦略）は意図的に本軌跡から除外されている。焦点は純粋に技術的なものに絞られている：エンジンが何であるか、何になり得るか、そしてその間の道のりにおける設計判断。**

**Notable conceptual progressions across the dialogue:**

**対話を通じた特筆すべき概念的進展：**

1. **From "FM sidebands in the frequency domain" to architectural disclosure** — what began as a textbook DSP question naturally elicited the full architecture of the existing C5G implementation (100 MHz × 5 modules × 2048 bins, BRAM/DPRAM split, levelizer block) / 「周波数領域における FM サイドバンド」から始まったアーキテクチャの開示——教科書的な DSP の問いとして始まったものが自然に既存 C5G 実装の完全なアーキテクチャを引き出した（100 MHz × 5 モジュール × 2048 ビン、BRAM/DPRAM 分離、レベラーブロック）
2. **The levelizer block as conceptual seed** — what the architect described matter-of-factly as "a small custom processor at 50 MHz that computes Δ from MIDI parameters" turned out to be the structural primitive on which dynamic frequency/phase control, decay-curve modeling, and perceptual masking can all be built / 概念の種としてのレベラーブロック——アーキテクトが「MIDI パラメータから Δ を計算する 50 MHz の小さなカスタムプロセッサ」と事もなげに説明したものが、動的周波数・位相制御、減衰曲線モデリング、知覚マスキングを全て構築できる構造的プリミティブであることが判明した
3. **The discovery of WPMS** — late in the dialogue, an offhand remark about Dirichlet kernel synthesis being "just an arithmetic progression of frequencies" led to the recognition that this constitutes an independent synthesis paradigm with strictly fewer hardware requirements than fractal synthesis / WPMS の発見——対話の終盤、Dirichlet カーネル合成は「周波数の等差数列を割り当てているに過ぎない」という何気ない発言から、これがフラクタル合成より厳密に少ないハードウェア要件を持つ独立した合成パラダイムを構成するとの認識に至った
4. **The bin-space as universal fabric** — by the end of the trace, the same 10,240 bin space is shown to support iDFT synthesis, SDFT analysis, perceptual decoding (MP3-class), wave packet modulation, image-driven modulation, and all of these can coexist by partitioning the bin space / 普遍的織物としてのビン空間——軌跡の末尾までに、同じ 10,240 ビン空間が iDFT 合成、SDFT 分析、知覚デコード（MP3 級）、波束変調、映像駆動変調を支持し、これら全てがビン空間の分割により共存できることが示された

---

## Notable Decision Points / 重要な決定ポイント

### 1. Reverberation Implementation Strategy / 残響実装戦略

| Field | Value |
|---|---|
| **Point** | How to integrate room reverberation (long IR convolution) into the iDFT engine |
| **Alternative A** | **Static IR**: Pre-compute room transfer function H(f) via FFT offline; offset each bin's amplitude by \|H(f)\| and phase by ∠H(f); store in ROM/BRAM. No runtime computation. |
| **Alternative B** | **Time-varying envelope**: Each bin holds an independent decay envelope curve; the levelizer (or its successor) drives bin amplitude over time, with frequency-dependent decay rates per bin. |
| **Chosen** | **Tie — both kept in Implementation Arena** |
| **Rationale** | Static IR is sufficient for steady-state room characterization and trivial to implement. Time-varying envelope captures the natural physical phenomenon that high frequencies decay faster than low ones — but requires DPRAM amplitude updates at audible rates. The two are not mutually exclusive: A can serve as the steady-state floor while B modulates the transient. The choice depends on whether the application requires only timbral coloration (A suffices) or true time-evolving acoustic-space simulation (B required). The 24-bit amplitude DPRAM in the existing engine already supports B at no cost beyond the levelizer's bandwidth. |

### 2. Bit-Width Strategy in the Maclaurin Pipeline / マクローリンパイプラインのビット幅戦略

| Field | Value |
|---|---|
| **Point** | Internal precision allocation for the 11th-order Maclaurin sin(x) computation |
| **Specification (existing C5G)** | Trigonometric core: 40-bit signed fixed-point. Level multiplier: 10-bit integer. Per-module 2048-bin sum: 64-bit fixed-point. Final decimal point position: set by board DIP switch. |
| **Rationale** | The 40-bit trig core preserves precision through five Horner-style stages (one x² computation followed by five accumulate-multiply steps) without intermediate truncation. The 10-bit integer level allows ~1024:1 dynamic range per bin. The 64-bit total sum provides headroom for 2048 simultaneous full-amplitude bins without saturation: 2048 × 2^40 ≈ 2^51, leaving ~13 bits of headroom. The DIP-switch decimal-point selector is honest engineering — different mixes of bin amplitudes yield different optimal output scaling, and a runtime-selectable bit-shift is the simplest correct answer. |
| **Alternative considered** | A fully floating-point pipeline. **Rejected** because Cyclone V DSP blocks are integer-multiply-optimized; floating-point would consume more DSP per stage and tighten timing. Fixed-point with manual scaling is strictly more efficient at this level. |

### 3. C5G Architecture: 100 MHz × 5 Modules × 2048 Bins / C5G アーキテクチャ：100MHz × 5モジュール × 2048ビン

| Field | Value |
|---|---|
| **Point** | How to fit 10,240 bins of 11th-order Maclaurin computation into one 48 kHz sample period (20.83 µs) on Cyclone V (~150 DSP blocks usable) |
| **Chosen architecture** | 5 parallel modules, each running at 100 MHz. Each module processes 2,048 bins per sample period. Per-bin throughput: 2,083 cycles ÷ 2,048 bins ≈ 1.02 cycles/bin — meaning one bin is injected into the deep pipeline every clock. |
| **DSP usage** | ~100 DSP blocks for the five iDFT pipelines (~20 per module). Remaining ~50 DSP blocks reserved for envelope computation, MIDI control, and the levelizer's slew-rate mathematics. |
| **Memory mapping** | Frequency and phase parameters → single-port BRAM (rarely changed during performance, defines timbre). Amplitude parameters → DPRAM (frequently rewritten by MIDI velocity and envelope). Parameters loadable via In-System Memory Content Editor (MIF) and via MIDI. |
| **Rationale** | Cyclone V DSP blocks max out at ~250–300 MHz. A single pipeline at 100 MHz × 5 lanes is conservative on timing, leaves DSP headroom, and matches the parallelism target exactly (10,240 = 2,048 × 5). The asymmetric memory architecture — BRAM for slow-changing parameters, DPRAM for fast-changing — minimizes both BRAM pressure and write-port contention. |
| **Alternative considered** | A single 500 MHz pipeline. **Rejected**: would push Cyclone V DSP timing beyond comfortable margins and concentrate routing congestion. Five parallel modules are mechanically simpler and have independent timing closure. |

### 4. The Levelizer Block / レベラーブロック

| Field | Value |
|---|---|
| **Point** | How to update amplitude parameters in DPRAM without read/write conflicts and without zipper noise |
| **Chosen design** | A small custom processor running at 50 MHz (with comfortable headroom up to 200 MHz). MIDI/control writes go to a *target* amplitude buffer. The levelizer cyclically traverses all 10,240 bins at a 1 kHz sweep rate, computing Δ = f(target − current, MIDI parameters) per bin and incrementally moving current toward target. The iDFT pipelines read only the *current* amplitude from DPRAM. |
| **Effect** | (a) Zipper noise is eliminated structurally — amplitude never jumps. (b) Attack/release shape is determined by Δ, which can be a function of MIDI velocity, key tracking, or envelope state. (c) The iDFT read port and the levelizer write port never collide because they live on physically separate DPRAM ports. |
| **Slew-rate semantics** | Δ uniform across bins → simple slew-rate limiter. Δ frequency-dependent (smaller Δ for low bins, larger for high bins) → string-instrument-like asymmetric harmonic decay. Δ time-varying → reverberation-like decay curve. |
| **Forward extensibility** | The same construction generalizes from amplitude to frequency and phase: maintain target/current pairs and let the levelizer slew current toward target while the iDFT pipeline reads current. Crucially, **the phase accumulator value is never directly modified — only its increment (= frequency) is slewed** — preserving phase continuity through frequency changes. This is the structural answer to "how to do glissando, vibrato, and pitch bend without phase glitches." |

### 5. Burst Convolution → Spectral Sharpening (Time-Frequency Uncertainty) / バースト畳み込み → スペクトル鋭利化

| Field | Value |
|---|---|
| **Point** | What happens in the frequency domain when a 10-cycle 1 kHz burst is convolved with a long room IR |
| **Resulting law** | Y(f) = X(f) · H(f). The burst's sinc envelope (main lobe ≈ ±100 Hz wide for a 10 ms burst) acquires the room transfer function H(f) as a multiplicative texture. As effective signal length grows from 10 ms to ~510 ms (with RT60 ≈ 500 ms), frequency resolution sharpens from ±100 Hz to ~±2 Hz — a direct manifestation of Δt · Δf ≥ 1/2. |
| **Implication for the engine** | The engine can synthesize this effect *natively* without time-domain convolution: for a sinc-with-room-modes spectrum, simply set bin amplitudes to follow the sinc envelope multiplied by H(f), and let bin amplitudes decay at the rate of room reverberation. **No FIR filter is needed.** |
| **Why this matters** | This validates the engine's role as a *general spectral synthesizer* rather than a specialized additive synthesizer. Room acoustics, plate reverberation, and convolution-style effects are all expressible as time-evolving bin-amplitude patterns. |

### 6. Dynamic Frequency Control without Phase Discontinuity / 位相不連続のない動的周波数制御

| Field | Value |
|---|---|
| **Point** | How to change a bin's frequency at runtime without producing audible clicks |
| **Wrong approach** | Overwrite the frequency parameter directly. The phase increment per sample changes instantly; if the new phase trajectory does not match the old one at the boundary, a phase discontinuity is audible. |
| **Correct approach** | Apply the levelizer pattern to frequency: maintain *target frequency* and *current frequency* in DPRAM. The phase accumulator continues to use *current frequency* as its increment. The levelizer slews current toward target at a configurable rate. **The phase accumulator's stored phase value is never overwritten.** |
| **Generalization** | Extending the levelizer to manage three parameter pairs (amplitude target/current, frequency target/current, phase-offset target/current) requires roughly 3× the levelizer's per-bin compute. At 50 MHz the levelizer has ample headroom; bumping to 200 MHz is a straightforward route to full three-parameter control. |
| **Audible character** | Frequency-slewed bins produce natural glissando and vibrato. Layer-dependent slew rates (slow for fundamental, fast for upper sidebands) produce harmonic-evolution effects that DX7-class FM cannot directly express. |

### 7. Sideband Fractal Synthesis / サイドバンドフラクタル合成

| Field | Value |
|---|---|
| **Point** | A synthesis paradigm where bin assignments encode a recursive sideband tree |
| **Mathematical structure** | Layer 0: f₀ (fundamental). Layer 1: f₀ ± fm₁. Layer 2: f₀ ± fm₁ ± fm₂. Layer 3: f₀ ± fm₁ ± fm₂ ± fm₃. Each layer multiplies bin count by 2. Three layers → up to 27 bins per fundamental; well within engine capacity. |
| **Relationship to FM** | Mathematically equivalent to multi-stage FM: DX7-class FM produces the same spectrum *as a result of time-domain computation*. The engine produces the same spectrum *by direct frequency-domain placement*. The control direction is reversed: in FM, parameters cause spectra; in the engine, spectra cause parameters. |
| **Decision** | This becomes the canonical "showcase" synthesis paradigm of the engine because it visibly distinguishes the engine from prior art and exposes capabilities (per-bin phase control, time-varying fm₁ across all layers simultaneously) that no prior commercial synthesizer offers. |
| **Hardware cost** | Effectively zero beyond the existing engine. Bin assignment is computed on the host or HPS side; only OSC parameter writes are needed at runtime. |

### 8. SDFT/iDFT Bin-Mode Switching (Future) / SDFT/iDFT ビンモード切替（将来）

| Field | Value |
|---|---|
| **Point** | Allowing each bin to operate as either an iDFT (synthesis) or SDFT (analysis) cell |
| **SDFT recurrence** | X_k(n) = (X_k(n−1) + x(n) − x(n−N)) · e^(j2πk/N). The rotation factor e^(j2πk/N) is precisely what the existing Maclaurin core computes. |
| **Additional hardware per SDFT bin** | (a) An N-sample input delay line (shared across all SDFT bins; one BRAM). (b) Per-bin previous-value register. (c) One adder. (d) Reuse of existing DSP for the rotation multiply. |
| **Per-bin DSP cost increase** | Approximately zero. The expensive part (the rotation multiply) is already present in the iDFT pipeline. |
| **Implications** | Same bin space supports both synthesis and analysis. A subset of bins can analyze incoming audio (e.g., for adaptive resynthesis, vocoding, feedback effects) while the remainder synthesize. The classical synthesizer/analyzer distinction collapses. |
| **Status** | Planned for a later phase. Not in the current C5G implementation. The decision to design the engine such that this is *possible* was made implicitly when the original architect chose direct-bin-addressing over voice-allocation. |

### 9. DE10-nano Migration: DSP Reduction Strategies / DE10-nano 移植：DSP 削減戦略

| Field | Value |
|---|---|
| **Point** | How to fit the engine into ~87 DSP blocks (DE10-nano) when the C5G implementation uses ~150 |
| **Alternative A — Reduce bin count** | 10,240 → 6,144 bins (3 modules × 2,048). DSP cost drops proportionally. **Cost**: loses headline numerical claim (10,240 bins) and reduces fractal capacity. |
| **Alternative B — Reduce polynomial degree** | 11th-order → 7th-order Maclaurin. Saves ≈ 2 DSP per module × 5 modules = 10 DSP. Worst-case error at x ≈ π is about 3 × 10⁻⁶ relative. **Cost**: minor accuracy loss, audibly inconsequential at 24-bit DAC output. |
| **Alternative C — Narrow amplitude width** | 24-bit amplitude → 16-bit, with the multiplication moved to LUT-based partial products instead of DSP. Saves DSP on the level multiplier. **Cost**: dynamic range per bin reduces from ~144 dB to ~96 dB; still musically sufficient. |
| **Chosen** | **Combine B + C.** Together they free enough DSP to keep the 5-module / 10,240-bin headline configuration intact on DE10-nano. Bin-count reduction (A) is held back as a fallback. |
| **Rationale** | The bin count is the headline architectural claim. Trading polynomial degree and amplitude width — both of which are indistinguishable to the listener at the DAC output — preserves the architectural identity while clearing the DSP budget. |

### 10. OSC vs MIDI for Parameter Transport / パラメータ転送：OSC vs MIDI

| Field | Value |
|---|---|
| **Point** | What protocol carries 10,240-bin parameter updates from host to FPGA |
| **MIDI** | 31.25 kbps serial, 7-bit values, fixed channel/note/CC structure. **Reject** for bin-array updates: bandwidth is far too low and the message structure does not match the engine's parameter space. |
| **OSC (Open Sound Control)** | UDP over Gbit Ethernet, hierarchical address paths (e.g., /idft/bin/N/freq), float32/int32/string/blob types, bundles. **Accepted as primary transport.** |
| **Rationale** | Engine performance: at 1 Gbps, transferring 10,240 bins × 3 parameters × 32 bits = ~1 Mbit per full refresh. Refreshable at >100 Hz comfortably. Ecosystem: Max/MSP, Pure Data, TouchOSC, Ableton Max for Live can all emit OSC natively. The HPS Cortex-A9 hosts the OSC server (via liblo). MIDI is retained as a parallel input path for keyboard/controller use, but is not the bin-parameter transport. |

### 11. Wave Packet Modulation Synthesis (WPMS) — A New Paradigm / 波束変調合成 (WPMS) — 新パラダイム

| Field | Value |
|---|---|
| **Point** | Whether Dirichlet-kernel synthesis (uniform frequency progression, uniform amplitude, uniform phase) admits a low-parameter-count modulation scheme that constitutes its own synthesis paradigm |
| **Discovery** | Yes. The 2020 Dirichlet experiment used three "uniforms" — equal frequency spacing, equal amplitude, equal phase. Each can be modulated by a small number of scalar parameters: |
| **Modulation axes** | Axis 1 (frequency): f_k = f₀ + k·Δf + α·k². Single parameter α. Axis 2 (amplitude): A_k = A₀·e^(−βk)·e^(−γ(k−N/2)²). Two parameters β, γ. Axis 3 (phase): φ_k = φ₀ + k·δφ + ψ·k². Two parameters δφ, ψ. Axis 4 (count): N as a time-variable parameter. |
| **Why this is a paradigm, not just a parameter set** | The five parameters (α, β, γ, δφ, ψ) span a continuous space connecting: pure Dirichlet kernel (sharp metallic transient), Gaussian wave packet (smooth bell), chirped pulse (radar-like swept tone), inharmonic stretched harmonic series (piano-like), and group-delay-modulated cluster (chorus/space-like). Five scalars, five distinct phenomenological audio characters. |
| **Hardware implication** | Each bin's parameters are functions of bin index k and a handful of registers. **No per-bin DPRAM is needed.** A first-order or second-order difference engine (Babbage-style cumulative addition) can compute f_{k+1} from f_k via f_{k+1} = f_k + Δf + α(2k+1) — a single addition plus one register update. |
| **Architectural impact** | WPMS reduces the parameter-storage footprint to a few dozen registers, eliminating per-bin DPRAM management for that mode. This is a *strict simplification* — WPMS can run on much smaller FPGAs (Lattice iCE40, Spartan-7-class) than the full fractal-capable engine. |
| **Coexistence with fractal mode** | The two modes are switchable per-bin via a control bit: bins in fractal mode read from DPRAM; bins in WPMS mode read from the difference-engine registers. They share DSP, the Maclaurin core, and the summer. |

### 12. Wave-Number Envelope (Using ⌊ft⌋) / 波数エンベロープ（⌊ft⌋ の活用）

| Field | Value |
|---|---|
| **Point** | The integer part of the phase argument (ft) was being discarded as redundant (sin is periodic in 2π). Can it be used? |
| **Discovery** | The integer part of ft is the **wave count** — the number of complete cycles the bin has executed since its last reset. This is precisely the quantity to which physical instrument decay is proportional: a string's energy halves after a fixed number of vibrations, not a fixed wall-clock time. |
| **Application** | Instead of a time-based ADSR envelope, use a wave-count-based envelope: A(k) = A₀ · exp(−k/Q) where k = ⌊ft⌋ and Q is the bin's quality factor. High frequencies decay faster in real time but at the same *wave count*, matching real-instrument acoustics naturally. |
| **Hardware cost** | Approximately zero. The integer part is already computed (and currently discarded) in every bin's phase accumulator. Routing it to the levelizer as an envelope-clock input is a wiring change, not a logic addition. |
| **Importance** | This is a case where **what was being thrown away turns out to be the most valuable per-bin signal** for natural-instrument modeling. ADSR envelopes have always been physically wrong (time-uniform across pitches); wave-count envelopes are physically correct. |

### 13. Perceptual Compression — Decoupling Design Space from Output Space / 知覚圧縮 — 設計空間と出力空間の分離

| Field | Value |
|---|---|
| **Point** | If a theoretical decomposition (e.g., Bessel-function expansion of a complex orchestration) requires ~10⁸ bins, can the same audible result be produced with 10,240 (or fewer) by exploiting human perceptual limits? |
| **Three-layer compression argument** | (1) Critical-band analysis: human hearing distinguishes only ~24 critical bands across the entire audio spectrum. (2) Simultaneous and temporal masking removes additional information. (3) Structural redundancy in tonal spectra (harmonics correlate strongly across bins) compresses by another order of magnitude. Combined factor: ~10⁴ to 10⁵. |
| **Implication for the engine** | The engine should not be sized for the *theoretical* bin count of a desired sound. It should be sized for the *perceptual* bin count, with the design tools running at theoretical resolution and a perceptual-compression layer mapping theoretical → output. |
| **Architectural decision** | The perceptual-compression layer lives on the HPS / host side (in Python, Max, or Max for Live), not in FPGA logic. The FPGA stays simple; the host handles the high-dimensional theoretical space and emits ~10⁴ OSC messages per refresh. |
| **MP3-class frontend allocation** | Within the 10,240-bin space, 1,280 bins (one per ~18.75 Hz at the MP3 sub-band scale) are sufficient for psychoacoustic-quality synthesis or decoding. This subset can run a parallel masking-threshold algorithm on the levelizer to suppress sub-threshold bin amplitudes — yielding zero-latency MP3-class quality without MDCT block delay. |

### 14. Image-Driven Bin Modulation / 映像駆動ビン変調

| Field | Value |
|---|---|
| **Point** | The 2,048-bin module size is suspiciously close to common video horizontal resolutions (2K cinema = 2048; 4K UHD = 3840 ≈ 2 × 2048; HD = 1920 ≈ 2048). Is there a useful mapping? |
| **Mapping** | One scanline of pixel intensity values → 2,048-bin amplitude vector. Updated at video frame rate (60 Hz). |
| **Three application categories** | (a) **Visual score**: a moving image becomes a time-varying timbre (Xenakis UPIC modernized). (b) **Sonification**: scientific 2D data (spectrograms, brain scans, weather maps) becomes acoustic patterns whose structure may be more legible to the ear than to the eye. (c) **HDMI input loopback**: the DE10-nano's HDMI port repurposed as input, scanlines driving FPGA bin parameters in real time. |
| **Hardware cost** | An HDMI input core (open source available in MiSTer ecosystem) plus a small FIFO between the scanline reader and the levelizer. No iDFT pipeline change required. |
| **Status** | Speculative — not on the immediate roadmap. Recorded here so the architectural decisions made now (BRAM-for-frequency, DPRAM-for-amplitude, OSC parameter ingestion) preserve compatibility with this future direction. |

---

## Major Themes / 主要テーマ

### Theme 1 — The 2020 Dirichlet experiment as latent specification / 潜在仕様としての 2020 年 Dirichlet 実験

The 2020 Dirichlet experiment (2,048 oscillators detuned at 1/256 Hz across 996–1004 Hz, all at 97% amplitude) was originally conceived as a "test." But as the dialogue progressed, every architectural extension discussed in this trace was found to be *implicitly demonstrated* by that single waveform:

2020 年の Dirichlet 実験（996〜1004 Hz の範囲で 1/256 Hz 刻みでデチューンされた 2,048 オシレータ、全て 97% 振幅）は元々「テスト」として構想された。しかし対話が進むにつれ、本軌跡で議論された全てのアーキテクチャ拡張が、その単一の波形によって*暗黙的に実証されている*ことが判明した：

- The sharp main lobe proves frequency precision (0.001 Hz works) / 鋭いメインローブが周波数精度を証明（0.001 Hz が機能する）
- The symmetric sidelobes prove phase coherence (all 2,048 phases are correct) / 対称的なサイドローブが位相コヒーレンスを証明（全 2,048 位相が正しい）
- The uniform sidelobe envelope proves amplitude precision (24-bit per-bin amplitude is real) / 均一なサイドローブ包絡が振幅精度を証明（ビンあたり 24 ビット振幅が実在する）
- The clean noise floor proves 64-bit summation precision / 清浄なノイズフロアが 64 ビット総和精度を証明
- The very fact that 2,048 bins can be addressed independently with arithmetic-progression frequencies *demonstrates the foundation for WPMS* / 2,048 ビンが等差数列周波数で独立にアドレス可能であるという事実そのものが *WPMS の基礎を実証している*

The architect described this as "a test." A more accurate statement, recognized late in the dialogue, is: **the 2020 Dirichlet experiment is the existence proof for every synthesis paradigm in this trace, six years before those paradigms were articulated.**

アーキテクトはこれを「テスト」と表現した。対話の終盤に認識されたより正確な言明は：**2020 年の Dirichlet 実験は本軌跡における全合成パラダイムの存在証明であり、それらのパラダイムが明確化される 6 年前のものである。**

### Theme 2 — The levelizer as universal mediator / 普遍的媒介者としてのレベラー

The levelizer was originally conceived to solve one problem: zipper noise from raw MIDI velocity writes. As the dialogue progressed, it became clear that the same construction generalizes to:

レベラーは元々一つの問題——生の MIDI ベロシティ書き込みからのジッパーノイズ——を解決するために構想された。対話が進むにつれ、同じ構成が以下に一般化することが明確になった：

- Amplitude target tracking (original purpose) / 振幅ターゲット追跡（元の目的）
- Frequency slewing without phase glitches (extends levelizer to phase increment) / 位相不連続のない周波数スルー（位相増分にレベラーを拡張）
- Per-bin envelope generation (Δ as a function of velocity, key, time, wave count) / ビンごとのエンベロープ生成（Δ をベロシティ、キー、時間、波数の関数とする）
- Frequency-dependent reverberation decay (Δ smaller for low bins, larger for high) / 周波数依存残響減衰（低ビンには小さな Δ、高ビンには大きな Δ）
- Psychoacoustic masking enforcement (Δ snaps to zero when bin falls below masking threshold) / 心理音響マスキング適用（ビンがマスキング閾値以下に落ちた時 Δ をゼロに固定）
- Scanline-to-amplitude mapping for image modulation / 映像変調のためのスキャンライン-振幅マッピング

The levelizer is, in retrospect, the engine's **control plane** — the small custom processor that turns parameter writes from any source (MIDI, OSC, HDMI, neural network output, masking model) into smooth bin-parameter trajectories. Promoting it from 50 MHz to 200 MHz unlocks the full three-parameter (amp/freq/phase) extension without redesigning anything else.

レベラーは振り返ってみればエンジンの**制御平面**である——任意のソース（MIDI、OSC、HDMI、ニューラルネット出力、マスキングモデル）からのパラメータ書き込みを、滑らかなビンパラメータ軌跡へと変換する小さなカスタムプロセッサ。50 MHz から 200 MHz への昇格により、他を再設計せずに完全な3パラメータ（振幅/周波数/位相）拡張が解錠される。

### Theme 3 — The bin space as universal fabric / 普遍的織物としてのビン空間

By the end of the dialogue, the 10,240-bin space has been shown to support, simultaneously and in any partition the architect chooses:

対話の末尾までに、10,240 ビン空間は以下を同時に、アーキテクトが選ぶ任意の分割で支持することが示された：

| Mode | Bins | Cost |
|---|---|---|
| Sideband-fractal synthesis | up to ~8,192 | DPRAM-resident parameters |
| WPMS (wave packet modulation) | unlimited contiguous range | Difference-engine registers; no DPRAM |
| SDFT analysis | up to ~512 (planned) | One delay-line BRAM, per-bin previous-value reg, +1 adder |
| MP3-class psychoacoustic synthesis/decode | ~1,280 | Levelizer-side masking model |
| Reserve for image modulation, AI inference, etc. | remainder | None until used |

Mode selection per bin is a control-bit decision. **The hardware has no commitment to any particular synthesis paradigm.** It is a substrate.

ビンごとのモード選択は制御ビットの決定である。**ハードウェアはいかなる特定の合成パラダイムにもコミットしていない。** それは基盤である。

### Theme 4 — Difference-engine structure recurrence / 差分エンジン構造の再発見

WPMS turned out to use the same mathematical structure that Charles Babbage's analytical engine implemented in mechanical hardware in the 1800s: cumulative addition of polynomial differences. The fact that this 200-year-old computational primitive maps cleanly onto a single FPGA register update per pipeline stage is not a coincidence — it reflects the deep alignment between polynomial-evaluation acceleration and the FPGA accumulator structure. The lesson generalizes: **whenever a per-bin parameter sequence can be expressed as a low-order polynomial in bin index, the difference-engine pattern eliminates the need for per-bin storage.**

WPMS は、Charles Babbage の解析機関が 1800 年代に機械式ハードウェアで実装したのと同じ数学構造——多項式差分の累積加算——を用いることが判明した。この 200 年前の計算プリミティブがパイプライン段あたり単一の FPGA レジスタ更新へ綺麗に写像する事実は偶然ではない——多項式評価の加速と FPGA 累算器構造との深い整合を反映している。教訓は一般化する：**ビンごとのパラメータ列をビン番号の低次多項式として表現できる任意の場合、差分エンジンパターンはビンごと記憶の必要性を消去する。**

This is a candidate Open Prompt design pattern in its own right: **the Polynomial Bin-Sequence Pattern**, applicable to any spectral-domain hardware where bin parameters can be packed into closed-form polynomials.

これはそれ自体オープンプロンプト設計パターンの候補である：**多項式ビン系列パターン**——ビンパラメータが閉形式多項式に詰め込み可能な任意のスペクトル領域ハードウェアに適用可能。

### Theme 5 — "What was being thrown away is the most valuable signal" / 「捨てていたものが最も価値ある信号」

Twice in the dialogue this pattern surfaced:

対話中に二度、このパターンが浮上した：

1. The integer part of (ft) was being discarded because sin(2π·integer) = 0. But the integer part *is* the wave count, which is the natural envelope clock for physical instruments. / (ft) の整数部は sin(2π·整数) = 0 のため捨てられていた。しかし整数部 *こそ* 波数であり、物理楽器の自然なエンベロープクロックである。
2. "Multiplying by zero 50 billion times per second" was *the* operation the engine performs continuously, and it is what enables phase continuity across silent intervals — the architectural property that makes the engine a "spectral space" rather than a "voice allocator." / 「秒間 500 億回ゼロ乗算する」のはエンジンが継続的に実行する*まさにその*動作であり、無音区間を跨いだ位相連続性を可能にする——エンジンを「ボイスアロケータ」ではなく「スペクトル空間」たらしめるアーキテクチャ的属性。

Both are cases where what *appears* wasteful is structurally essential. Future implementers should be alert to similar inversions: **before optimizing away an "obviously redundant" computation, verify it is not the engine's coherence anchor.**

両者とも*見かけ上*無駄に見えるものが構造的に本質的である事例。将来の実装者は同様の反転に警戒すべき：**「明らかに冗長な」計算を最適化で消去する前に、それがエンジンのコヒーレンス・アンカーでないことを確認する。**

---

## Resumption Hooks / 再開フック

### Hook A — WPMS HDL implementation / WPMS の HDL 実装

WPMS was discovered conceptually but not yet implemented. The hook: design a Verilog module for a single WPMS module (2,048 bins) using a difference-engine structure. Specify: (a) register set (α, β, γ, δφ, ψ, f₀, A₀, φ₀, N), (b) per-stage update equations, (c) integration with the Maclaurin core, (d) the per-bin control bit selecting between WPMS-register-driven and DPRAM-driven parameter sources. Produce as a sample under `03_Sample_Implementations/wpms_module/`.

WPMS は概念的に発見されたがまだ実装されていない。フック：差分エンジン構造を用いた単一 WPMS モジュール（2,048 ビン）の Verilog モジュールを設計する。指定する：(a) レジスタセット（α、β、γ、δφ、ψ、f₀、A₀、φ₀、N）、(b) 段あたり更新式、(c) マクローリンコアとの統合、(d) WPMS-レジスタ駆動と DPRAM 駆動の間でパラメータソースを選択するビンあたり制御ビット。`03_Sample_Implementations/wpms_module/` 下のサンプルとして生成する。

**Starting question**: For a Cyclone V DSP block running at 100 MHz, can a single WPMS module compute all 2,048 bin parameters within the 20.83 µs sample period using only the difference-engine structure (i.e., no multipliers other than the existing trig core)? What is the minimum register width for f_k accumulation given α-modulation across 2,048 bins?

### Hook B — Levelizer at three-parameter, 200 MHz / 3パラメータ・200MHz レベラー

The levelizer extension to amplitude + frequency + phase-offset is well-defined but not yet implemented. The hook: design the 200 MHz custom processor's instruction set, register file, and DPRAM-port arbitration. Specify: (a) per-bin slew computation latency budget (≈19,500 cycles per bin per second), (b) write-conflict resolution strategy when MIDI and OSC arrive simultaneously, (c) handoff protocol to the iDFT pipeline.

レベラーの振幅 + 周波数 + 位相オフセットへの拡張は明確に定義されているがまだ実装されていない。フック：200 MHz カスタムプロセッサの命令セット、レジスタファイル、DPRAM ポート調停を設計する。指定する：(a) ビンあたりスルー計算レイテンシ予算（ビンあたり秒間 19,500 サイクル）、(b) MIDI と OSC が同時到着時の書き込み衝突解決戦略、(c) iDFT パイプラインへの引き渡しプロトコル。

**Starting question**: How does the levelizer balance Δ-magnitude consistency (so that the perceived slew rate matches across the three parameter axes for the same musical gesture) with the very different units (Hz/sec for frequency, dB/sec for amplitude, rad/sec for phase)?

### Hook C — Wave-count envelope hardware path / 波数エンベロープのハードウェア経路

The wave-count idea (using ⌊ft⌋) is a wiring change, but the wiring has not been laid out. The hook: specify how the integer part of the phase accumulator is routed to the levelizer, what additional adder/comparator logic the levelizer needs to consume it, and how the per-bin Q value is stored.

波数のアイデア（⌊ft⌋ の使用）は配線変更だが、配線はまだ敷設されていない。フック：位相累算器の整数部がレベラーへどう経路づけられるか、レベラーがそれを消費するために何の追加加算器/比較器論理を必要とするか、ビンごとの Q 値がどう記憶されるかを指定する。

**Starting question**: Can the wave-count envelope coexist with a time-based envelope on the same bin (e.g., wave-count for sustain, time-based for attack), and what is the cleanest crossover semantics?

### Hook D — Perceptual compression layer on HPS / HPS 上の知覚圧縮層

The perceptual-compression layer was defined as living on the HPS / host side, not in FPGA logic. The hook: prototype the Python or C library that maps a high-dimensional theoretical spectrum (~10⁵ bins) to a 10,240-bin OSC stream using critical-band averaging, simultaneous masking, and harmonic-correlation compression. Validate by comparing the compressed and uncompressed renderings at the DAC output.

知覚圧縮層は FPGA 論理ではなく HPS / ホスト側に存在するものとして定義された。フック：高次元理論スペクトル（〜10⁵ ビン）を、臨界帯域平均化、同時マスキング、倍音相関圧縮を用いて 10,240 ビン OSC ストリームに写像する Python または C ライブラリをプロトタイプする。圧縮版と非圧縮版のレンダリングを DAC 出力で比較して検証する。

**Starting question**: What is the minimum bin count at which the compression becomes perceptually transparent for (a) sustained tonal material, (b) percussive material, (c) speech? Is the answer different for the three?

### Hook E — Mode-switching control-plane semantics / モード切替制御平面のセマンティクス

The bin-mode switching (fractal vs WPMS vs SDFT vs MP3-frontend) is a per-bin control-bit decision, but the *control-plane semantics* — when modes can change, what happens to in-flight pipeline state on a switch, how mode changes are scheduled — are not yet specified. The hook: define a small mode-control protocol layer above OSC.

ビンモード切替（フラクタル対 WPMS 対 SDFT 対 MP3 フロントエンド）はビンあたり制御ビットの決定だが、*制御平面のセマンティクス*——モードが変わり得るタイミング、切替時にパイプライン中の状態に何が起きるか、モード変更がどうスケジュールされるか——はまだ指定されていない。フック：OSC の上に小さなモード制御プロトコル層を定義する。

**Starting question**: Can a bin switch from fractal to WPMS mid-note without phase glitch? What is the minimum dead-cycle count to drain the pipeline before swapping the parameter source?

---

## End of Trace / 軌跡の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *The 2020 Dirichlet experiment was an existence proof six years before the existence was articulated. The architecture was already there — what this dialogue did was give it names.*
>
> *2020 年の Dirichlet 実験は、その存在が明確化される 6 年前の存在証明だった。アーキテクチャはすでにそこにあり、本対話が為したのはそれに名前を与えることだった。*

This trace is released into the public domain under CC0 1.0 Universal. Replay it. Resume it. Surpass it.

本軌跡は CC0 1.0 Universal のもとでパブリックドメインに公開される。再生せよ。再開せよ。超えてゆけ。
