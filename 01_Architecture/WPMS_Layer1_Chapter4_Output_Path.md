# WPMS Synthesizer — Layer 1 Specification
# Chapter 4: The Output Path — Gain Staging, Clock Domains and HDMI Audio
# WPMS シンセサイザー — 第1層仕様書
# 第4章：出力経路——ゲイン段、クロックドメイン、HDMI オーディオ

> **License: CC0 1.0 Universal (Public Domain)**
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**

*v1.0 DRAFT · 2026-09-24 · WPMS / FPGA Spectrum Engine amanuensis.*
*Depends on: Ch.1 v1.0 (§ 1.3, § 1.8), Ch.2 v1.1, Ch.3 v1.0 DRAFT (§ 3.5–3.7, C3-D1 Fixed 2026-09-24). No new customer requirements to the L2 profile arise here; CR3-T2 (strobe wake) is anchored in § 4.3.*

*第 3 章草案に依存。本章から L2 プロファイルへの新たな顧客要求は生じない。CR3-T2（ストローブによる起床）の起点は § 4.3 で定まる。*

**Legend / 凡例:** **[Fixed]** · **[Arena]** · **[Evidence: oracle]** (Python, *not silicon*) · **[Board fact]** a property of the DE10-nano to be confirmed against the Terasic schematic during pin assignment.

---

## 4.0 Reading guide / 読み方

Chapter 3 ends at two accumulators per module. This chapter carries their sum to the wire and answers three questions:

第 3 章はモジュールあたり二つの累算器で終わる。本章はその和を配線まで運び、三つの問いに答える：

1. **How loud, and how safely?** — the output amplitude chain after the accumulators: master gain, coarse gain, rounding, saturation, and the headroom that coherent wave packets demand (§ 4.4). / **どれだけの音量を、どれだけ安全に？**
2. **Who keeps time?** — which clock owns the L3 sample period, and how samples cross clock domains (§ 4.3, § 4.5). / **誰が時を刻むのか？**
3. **What does "HDMI audio" mean on this board?** — the division of labour between WPMS logic and the ADV7513 transmitter (§ 4.2, § 4.6, § 4.7). / **この基板で「HDMI オーディオ」とは何か？**

The chapter also checks whether the log-domain amplitude of Chapter 3 meets any obstacle on the way out. It does not; it helps (§ 4.4.1, § 4.4.4).

本章は、第 3 章の対数領域振幅が出口までの間に障害に出会わないかも確かめる。出会わない。むしろ助けになる（§ 4.4.1、§ 4.4.4）。

---

## 4.1 Role and Boundary / 役割と境界

### Owned / 所有

- The output amplitude chain: master gain MG (applied inside L1 as one added term), coarse gain G, rounding, saturation, clip detection / 出力振幅チェーン
- The origin of the L3 sample strobe and all clock domains / L3 サンプルストローブの起点と全クロックドメイン
- The sample handoff from the synthesis domain to the audio domain / 合成ドメインからオーディオドメインへのサンプル受け渡し
- The I2S master, the ADV7513 configuration intent, and the video carrier / I2S マスター、ADV7513 設定の意図、ビデオキャリア
- Latency definitions, and the PCM tap for Layer 4 bit-level verification / レイテンシの定義、第 4 層のビットレベル検証用 PCM タップ

### Not owned / 所有しない

- L1 internals up to the accumulators (Ch.3) / 累算器までの L1 内部（第 3 章）
- The inbox, AXI input switch, and the address of MG and G registers in the external address map (Ch.5) / inbox、AXI 入力スイッチ、MG・G レジスタの外部アドレス（第 5 章）
- The behaviour of the HDMI sink (monitor, TV, extractor) — its latency and DAC are outside WPMS / HDMI シンクの振る舞い——そのレイテンシと DAC は WPMS の外

---

## 4.2 What "HDMI Audio" Means on the DE10-nano / DE10-nano における「HDMI オーディオ」 **[Fixed]**

**[Board fact]** The DE10-nano drives its HDMI connector through an **Analog Devices ADV7513** transmitter. The FPGA delivers parallel video (RGB, HS, VS, DE, pixel clock), I2S audio (MCLK, SCLK, LRCLK, one data line) and an I2C configuration bus. The HDMI protocol itself — TMDS encoding, data-island packetization of audio samples, InfoFrames, audio clock regeneration (N/CTS) — is performed **inside the ADV7513**.

**[基板の事実]** DE10-nano は HDMI コネクタを **ADV7513** 送信器経由で駆動する。FPGA はパラレルビデオ、I2S オーディオ（データ線 1 本）、I2C 設定バスを供給する。HDMI プロトコルそのもの——TMDS、音声サンプルのデータアイランド化、InfoFrame、オーディオクロック再生（N/CTS）——は **ADV7513 内部**で行われる。

Therefore the "HDMI audio core" of Ch.1 § 1.3 decomposes into four small blocks, none of which touches the HDMI protocol:

したがって第 1 章 § 1.3 の「HDMI オーディオコア」は、HDMI プロトコルに触れない四つの小ブロックに分解される：

| Block | Function | Domain |
|---|---|---|
| **I2S master** | serializes the output bank; emits the L3 strobe | clk_aud |
| **Video carrier** | 1280×720p60 timing and a static frame (HDMI audio rides in video blanking) | clk_pix |
| **ADV7513 configurator** | one-time I2C initialization after power-up / hot-plug | clk_sys (slow) |
| **Output stage** | MG slew, G, rounding, saturation, clip flag, output bank | clk_sys |

**Why a video carrier at all.** HDMI carries audio only inside a video stream, and only in HDMI mode (a DVI-mode stream drops audio). The video is a carrier, not a feature; its content is an Arena item (§ 4.11).

**なぜビデオキャリアが要るか。** HDMI はビデオストリームの中でのみ、かつ HDMI モードでのみ音声を運ぶ（DVI モードでは音声は落ちる）。ビデオは機能ではなくキャリアであり、その内容は Arena 項目。

### 4.2.1 License boundary with the MiSTer framework / MiSTer フレームワークとのライセンス境界 **[Fixed]**

Ch.1 § 1.3 named an open-source MiSTer-ecosystem HDMI core as the starting point. The MiSTer framework (`sys/`) is licensed under the GPL (to be verified file by file). Copying it into Layer 3 would bind that layer to the GPL, which conflicts with this repository's MIT Layer 3 and with the Open Prompt rule that a regenerated implementation is the regenerator's own work.

第 1 章 § 1.3 は MiSTer エコシステムの HDMI コアを出発点とした。MiSTer フレームワーク（`sys/`）は GPL である（ファイルごとに要確認）。これを第 3 層へ複製すると同層が GPL に拘束され、本リポジトリの MIT 第 3 層、および「再生成された実装は再生成者自身の著作物」という Open Prompt の原則と衝突する。

**Decision:** the four blocks are **regenerated** from the ADV7513 documentation and this chapter; MiSTer is consulted as **prior art, not copied**. The blocks are small (§ 4.10), and regenerating them is itself a small demonstration of the Open Prompt claim. Board-level compatibility with MiSTer (same board, same pins, same transmitter) is unaffected.

**決定：** 四ブロックは ADV7513 の資料と本章から**再生成**する。MiSTer は**先行例として参照し、複製しない**。ブロックは小さく（§ 4.10）、その再生成自体が Open Prompt の主張の小さな実証になる。MiSTer との基板レベルの互換性（同じ基板・ピン・送信器）は損なわれない。

---

## 4.3 Clock Domains and the Master of L3 / クロックドメインと L3 の主 **[Fixed]**

### 4.3.1 Domains / ドメイン

| Clock | Frequency | Role |
|---|---|---|
| clk_ref | 50 MHz | board oscillator; reference of all PLLs |
| **clk_sys** | 100 MHz | L1 pipeline, L2 Formation, output stage |
| **clk_aud** (MCLK) | 12.288 MHz = 256·Fs | I2S master; **origin of the L3 strobe** |
| clk_pix | 74.25 MHz | video carrier (720p60) |

All are synthesized from clk_ref by Cyclone V PLLs. The realized Fs deviates from 48 kHz by the PLL's residual error (to be measured, Layer 4); all bin frequencies scale with it (Ω_k·Fs), a ppm-level pitch offset that is musically irrelevant.

### 4.3.2 The audio domain is the master of L3 / オーディオドメインが L3 の主

**The L3 sample period is defined by the I2S frame, not by clk_sys.** Since 100 MHz / 48 kHz = 2,083.33…, clk_sys cannot divide it; L1 and L2 are **slaves** (Ch.3 § 3.2.1).

**L3 サンプル周期は clk_sys ではなく I2S フレームで定義される。** 100 MHz / 48 kHz は整数でないため clk_sys では分周できず、L1・L2 は**スレーブ**である。

Let F_m be the frame boundary (LRCLK falling edge; left channel of frame m begins). The I2S master emits the **L3 strobe S_m at F_m − Δ_pre**, with **Δ_pre = 1 SCLK = 4 MCLK = 325.5 ns**. S_m reaches clk_sys through a **toggle synchronizer** (the audio side toggles a bit; the sys side detects the edge after two flip-flops). The synchronized strobe is the single event that (a) wakes every L2 Formation (CR3-T2), (b) closes every accumulator into the output stage (Ch.3 C3-D9), and (c) advances MG's slew (§ 4.4.1).

F_m をフレーム境界とする。I2S マスターは **L3 ストローブ S_m を F_m − Δ_pre**（Δ_pre = 1 SCLK = 4 MCLK = 325.5 ns）で発し、**トグル同期器**で clk_sys へ渡す。同期化されたストローブは唯一のイベントとして、(a) 全 L2 Formation を起こし、(b) 全累算器を出力段へ閉じ、(c) MG のスルーを進める。

Why Δ_pre: it gives the output bank time to settle before the audio side captures it at F_{m+1} (§ 4.5), so a finished sweep reaches the wire in the very next frame. The measured clk_sys period between synchronized strobes is 2,083 or 2,084 clocks; Ch.3 § 3.7 uses T_min = 2,083.

---

## 4.4 The Output Amplitude Chain / 出力振幅チェーン **[Fixed]**

```
   L1 (Ch.3):  L_k = ℓ + s_k + MG  →  clamp  →  exp2  →  × sin  →  accumulators (Q12.63 per module)
                                ▲
                          master gain (log₂, ≤ 0)
   output stage:  Σ modules (Q13.63) → × 2^(−G) → round → saturate → Q1.23 (L, R) → bank → I2S
```

### 4.4.1 Master gain MG — one adder, in the log domain / マスターゲイン MG——対数領域の加算器一つ

A global master gain **MG** (Q6.26, log₂, **MG ≤ 0**) is added to every bin's log-amplitude in L1: `L_k = ℓ + s_k + MG`. Cost: one input on an adder that already exists, per module. It is exact, needs no multiplier, and cannot overflow because the per-bin clamp (a ≤ 1) already exists. MG attenuates only; boost is G's job.

グローバルなマスターゲイン **MG**（Q6.26、log₂、**MG ≤ 0**）を L1 で各ビンの対数振幅に加える。コストはモジュールあたり既存加算器の入力一つ。厳密で、乗算器が要らず、ビンごとのクランプが既にあるのでオーバーフローしない。MG は減衰のみ、増幅は G の役目。

**Slew.** The external controller writes MG_target; at each synchronized strobe, `MG ← MG + clamp(MG_target − MG, ±MG_rate)`. Because MG is logarithmic, a constant slew is a **constant dB/s fade** — the perceptually uniform fade, obtained with an adder and a comparator. Default MG_rate = 60 dB/s = 13,933 (Q6.26 per sample). **[Evidence: oracle]** This is the levelizer principle of the 2026-04 dialogue, revived for the master level, and it is simpler in log coordinates than it ever was in linear ones.

**スルー。** 外部制御者が MG_target を書き、毎ストローブで MG が MG_rate 以内で追従する。MG は対数なので、一定スルーは**一定 dB/s のフェード**——知覚的に一様なフェード——となり、加算器と比較器だけで得られる。2026-04 対話のレベラー原理のマスターレベルへの復活であり、線形座標のときよりも対数座標のほうが単純である。

Ch.3 v1.1 will add the MG term to § 3.5.4; this is a wiring change within Ch.3's own scope and needs nothing from the L2 profile.

### 4.4.2 Coarse gain G, rounding, saturation / 粗ゲイン G、丸め、飽和

`out = saturate( round( acc · 2^(−G) ) )` in Q1.23 per channel.

- **G** is selected by DIP[1:0] ∈ {0, 4, 8, 12} (Ch.1 § 1.8); an ISSP override register may select any G ∈ 0…15. / G は DIP で選択、ISSP で 0〜15 を上書き可。
- **Rounding** to nearest (one adder); v1.0's truncation policy of Ch.2 applies inside the Maclaurin core only. / 最近接丸め。
- **Saturation**, never wrap. A sticky **clip flag** per channel is set on any saturation, readable and clearable by ISSP and mirrored on a board LED. / 飽和のみ、折り返しなし。スティッキーなクリップフラグを ISSP と LED に出す。

### 4.4.3 Headroom and the crest factor of coherent wave packets / ヘッドルームとコヒーレント波束のクレストファクタ

WPMS packets are phase-structured by design, so their peaks add coherently. The output stage must be sized for that. **[Evidence: oracle]** N = 2,048 bins of equal amplitude:

WPMS のパケットは設計上位相構造を持つため、ピークはコヒーレントに加算される。出力段はそれに見合うよう設計しなければならない。

| Phase law | Peak / RMS (crest) | Test-origin level (A = 0.97) |
|---|---|---|
| all zero — Dirichlet (test origin) | 64.0 = **36.1 dB** | G = 12: peak −6.3 dBFS, RMS **−42.4 dBFS** |
| random | 4.06 = 12.2 dB | — |
| **quadratic, ψ = π/N — Schroeder phase** | 1.91 = **5.6 dB** | G = 8: peak −12.7 dBFS, RMS **−18.3 dBFS** |

The Schroeder low-peak-factor multisine (1970) is **exactly a WPMS packet**: φ_k = πk²/N, i.e. PHD1 = 2³²/(2N), PHD2 = 2³²/N (= 2²¹ for N = 2,048). The same bins at the same amplitudes carry the same energy with 30 dB less crest factor. In WPMS terms: **ψ is the loudness-versus-impulse knob.** The Dirichlet kernel is maximally impulsive and therefore quiet at safe gain; a Schroeder-chirped packet is a steady tone cluster and can be played about 24 dB louder with G = 8 instead of 12.

Schroeder の低ピークファクタ・マルチサイン（1970）は**そのまま WPMS の一パケット**である。同じビン・同じ振幅で同じエネルギーを運びつつ、クレストファクタが 30 dB 低い。WPMS の言葉では、**ψ は「音量対インパルス性」のつまみ**である。

Guidance to the L4 controller (non-normative): choose G from the expected peak (Σ a_k for coherent packets), then trim with MG; watch the clip flag. No limiter is specified; clipping is visible, never silent.

### 4.4.4 Sign lives in the phase / 符号は位相に住む

In the log domain every amplitude is non-negative. Nothing in Ch.1 § 1.4 needs a negative amplitude, and any sign pattern that WPMS can express at all is a phase pattern: a global inversion is PH0 + 2³¹; the alternation (−1)^k is PHD1 + 2³¹. Both are exact (Ch.3 § 3.4). The log-domain choice therefore loses no expressible sound.

対数領域ではすべての振幅が非負である。第 1 章 § 1.4 に負の振幅を要するものはなく、WPMS が表現しうる符号パターンはすべて位相パターンである。対数領域化によって表現可能な音は一つも失われない。

### 4.4.5 Mute / ミュート

DIP[3] (Ch.1 § 1.8) becomes a **soft mute**: it drives MG_target to the floor (−32, below the per-bin clamp), and the output is forced to exact zero once MG reaches the floor. A full fade at the default rate takes ≈ 1 s from 0 dB to −60 dB; no click. Ch.1 § 1.8's "force output to zero" still holds, after the fade.

### 4.4.6 DC and Nyquist / 直流とナイキスト

Frequencies are defined modulo Fs (Ω_k is an integer mod 2³²). A component above Fs/2 is the same sinusoid as its image below, exactly — no aliasing artifact exists in the synthesis itself; a chirp crossing Fs/2 folds back by definition. A packet component at or near 0 Hz produces DC or sub-audio content; WPMS does not filter it. A DC blocker is an Arena item; the L4 tool is expected to warn.

---

## 4.5 Sample Handoff clk_sys → clk_aud / サンプル受け渡し **[Fixed]**

The output bank (L and R in Q1.23, plus the clip flags) is written in clk_sys **only** on the synchronized strobe, i.e. within a few tens of ns after S_{m+1}. It is then stable for a whole period. The audio side captures the whole bank on **F_{m+1} = S_{m+1} + Δ_pre**, at least ≈ 290 ns after any possible change and ≈ 20 µs before the next one.

出力バンクは同期化ストローブでのみ clk_sys で書かれ、その後一周期のあいだ安定する。オーディオ側は **F_{m+1}** でバンク全体を取り込む——変化の約 290 ns 後、次の変化の約 20 µs 前である。

This is a **stability-window crossing**: multi-bit, no handshake, correct by construction because capture and change are separated by a known interval. Timing constraints declare the bank-to-capture path with a maximum-skew / stability requirement rather than as an ordinary synchronous path (detail: Layer 3 `.sdc`). An asynchronous FIFO or a handshake is an Arena alternative, at higher cost and no benefit here.

これは**安定窓による受け渡し**である。多ビット、ハンドシェイクなし、取り込みと変化が既知の間隔で分離されているため構造的に正しい。

---

## 4.6 I2S Master and ADV7513 Configuration / I2S マスターと ADV7513 設定 **[Fixed]**

### 4.6.1 I2S

| Parameter | Value |
|---|---|
| Format | standard (Philips) I2S: LRCLK low = left; data MSB-first, one SCLK after the LRCLK edge |
| MCLK | 256·Fs = 12.288 MHz |
| SCLK | 64·Fs = 3.072 MHz (32-bit slots) |
| Word | 24 bits, left-justified in each 32-bit slot |
| Channels | 2 |

**[Board fact]** The DE10-nano routes **one** I2S data line to the ADV7513, so the audio path carries two channels. RT.OUT bits 2–7 (surround, Ch.3 § 3.6.4) are therefore not realizable on this board's HDMI path; they remain reserved for boards that route more I2S lines.

### 4.6.2 ADV7513 configuration intent / ADV7513 設定の意図

After power-up and on hot-plug, the configurator writes over I2C a sequence whose intent is:

- power up the transmitter; select **HDMI mode** (not DVI);
- video input: 24-bit RGB, separate syncs, 720p60 (VIC 4) in the AVI InfoFrame;
- audio input: **I2S, 24-bit, 2 channels, 48 kHz**; audio clock regeneration with **N = 6144** (the standard value for 48 kHz), CTS generated by the ADV7513;
- audio InfoFrame: 2-channel L-PCM.

Register addresses and values are Layer 3 content, derived from the ADV7513 programming documentation. Whether the sequencer is a small hand-written FSM or a PTSG program is an Arena choice (§ 4.11).

レジスタ番地と値は第 3 層の内容。シーケンサを小さな FSM とするか PTSG のプログラムとするかは Arena。

**Sink assumption.** The first implementation assumes an HDMI sink that accepts 2-channel 48 kHz L-PCM — a basic audio capability of HDMI sinks. The EDID is not read; a DVI-only monitor will show the carrier and play nothing.

---

## 4.7 Video Carrier / ビデオキャリア **[Fixed]**

1280×720 progressive, 60 Hz (CEA-861 VIC 4), pixel clock 74.25 MHz, content black or a static frame. 720p60 is chosen for broad sink compatibility and for room in the horizontal blanking for audio data islands. 640×480p60 (VIC 1) is an Arena alternative.

---

## 4.8 Latency / レイテンシ **[Fixed]**

| Interval | Value | Note |
|---|---|---|
| Compute latency: sweep *m* → output bank | **1 sample period** | Ch.3 C3-D9 |
| Sweep start S_m → left-channel MSB of that sample on the I2S wire | T + Δ_pre + 1 SCLK = **21.48 µs = 1.031 periods** | this chapter |
| Parameter commit → effect | ≤ 1 period of waiting for the next sweep, then as above | L2 choreography (Deliverable 3) |
| HDMI transmitter + sink (decode, lip-sync buffering, DAC) | **not WPMS's** — typically milliseconds, sink-dependent | measured in Layer 4 |

The project headline "1-sample latency" is the compute latency, and it holds to the I2S wire within 3 %. What a monitor or TV adds afterwards is outside the engine and should be reported separately whenever latency is published.

プロジェクトの見出し「1 サンプル遅延」は演算レイテンシであり、I2S 配線まで 3 % 以内で成り立つ。モニタや TV がその後に加える遅延はエンジンの外であり、レイテンシを公表する際は別に報告するのが誠実だと考える。

---

## 4.9 The PCM Tap and Layer 4 Hooks / PCM タップと第 4 層への接続点 **[Fixed]**

Bit-level regression (Ch.3 § 3.10, tier (i)) uses the **output bank in clk_sys**, observed through SignalTap or an ISSP probe — not the HDMI output, which passes through a transmitter and a sink outside WPMS. Exposed for Layer 4:

- output bank L, R (Q1.23) and the sticky clip flags;
- MG (current), MG_target, G (effective);
- the count of clk_sys clocks between synchronized strobes (expected 2,083 / 2,084), as a continuous check of the L3 master;
- per module, the clk_sys count from strobe to the last accumulated product (the measured left side of Ch.3 § 3.7's inequality).

The last item turns the sweep timing budget into a live measurement.

---

## 4.10 Resource Estimate / リソース見積もり

| Block | Logic | DSP | Memory |
|---|---|---|---|
| Output stage (MG slew, Σ modules, G, round, saturate, bank) | small (≈ 76-bit adders and shifters) | 0 | 0 |
| I2S master + strobe toggle | ≈ 100 LE | 0 | 0 |
| Video carrier (timing + static frame) | ≈ 200 LE | 0 | 0 |
| ADV7513 configurator (FSM + I2C) | ≈ 300 LE | 0 | small ROM |
| PLLs | 2–3 | — | — |

The output path costs no DSP blocks. Ch.3's estimate (24–32 of 112 DSP for Compact) is unchanged.

---

## 4.11 Implementation Arena / 実装アリーナ

| Item | This chapter | Preserved alternative |
|---|---|---|
| ADV7513 configurator | small FSM | **a PTSG program** — PTSG's second application in the same bitstream, driving I2C |
| Video content | black / static | status page (packet map, clip flags, MG); a view of the bin space |
| Video mode | 720p60 | 640×480p60 |
| Sample handoff | stability window | async FIFO; handshake |
| Crest management | none (G, MG, clip flag) | limiter or soft clip in the output stage |
| DC | not filtered | first-order DC blocker at a few Hz |
| Channel balance / pan | hard L/R via RT.OUT | per-channel gain after accumulation (one wide multiplier per channel) |
| EDID | not read | DDC read to verify audio capability |
| Multichannel | 2 ch | boards routing four I2S lines (RT.OUT bits 2–7) |
| Analog output | none (Ch.1 § 1.3) | MiSTer I/O board audio circuits |

---

## 4.12 Open Questions / 未解決問題

| Question | Resolution path |
|---|---|
| Board facts: ADV7513 pins and single I2S line; CTS mode | pin assignment against the Terasic schematic; Layer 3 |
| Realized Fs deviation of the PLL chain | Layer 4 |
| Sink latency with representative monitors/TVs/extractors | Layer 4 |
| Default MG_rate (60 dB/s) and soft-mute duration | listening, Layer 4 |
| MiSTer `sys/` licenses, file by file | before any MiSTer text is consulted closely |
| Ch.3 v1.1: add MG to § 3.5.4 (`L_k = ℓ + s_k + MG`) | Ch.3 v1.1 |
| Ch.1 v1.1: § 1.3 (MiSTer as prior art, not starting code); § 1.8 DIP[3] = soft mute, G override by ISSP | Ch.1 v1.1 |

---

## 4.13 Decisions of this Chapter / 本章の決定事項

| ID | Decision | Status |
|---|---|---|
| C4-D1 | On DE10-nano the HDMI protocol is the ADV7513's; WPMS supplies I2S audio, a video carrier and I2C configuration; HDMI mode, 2-ch L-PCM, 48 kHz, 24 bit, N = 6144 | Fixed |
| C4-D2 | Clock domains: clk_sys 100 MHz, clk_aud 12.288 MHz, clk_pix 74.25 MHz, all from clk_ref | Fixed |
| C4-D3 | The audio domain is the master of L3; strobe S_m = F_m − 1 SCLK; toggle synchronizer; single strobe event for wake, close and MG slew | Fixed |
| C4-D4 | Master gain MG in log₂ (Q6.26, ≤ 0) added in L1; target + slew per sample (default 60 dB/s) | Fixed |
| C4-D5 | G by DIP[1:0] ∈ {0,4,8,12}, ISSP override 0…15; round to nearest; saturate; sticky clip flags | Fixed |
| C4-D6 | DIP[3] = soft mute via MG, then exact zero | Fixed |
| C4-D7 | Sample handoff by stability window: write on strobe, capture on F_{m+1} | Fixed |
| C4-D8 | I2S: Philips, MCLK 256·Fs, SCLK 64·Fs, 24-bit in 32-bit slots, 2 ch | Fixed |
| C4-D9 | Video carrier 720p60 (VIC 4), static content | Fixed |
| C4-D10 | Latency: compute 1 period; to I2S wire 1.031 periods; sink latency reported separately | Fixed |
| C4-D11 | MiSTer framework is prior art, not copied; the four blocks are regenerated | Fixed |
| C4-D12 | PCM tap in clk_sys for bit-level verification; strobe-interval and sweep-completion counters exposed | Fixed |
| C4-D13 | Crest factor is a WPMS parameter: ψ = π/N (Schroeder) gives 5.6 dB vs 36.1 dB for the Dirichlet test origin | Fixed (guidance to L4) |

---

## End of Chapter 4 / 第 4 章の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *Let the audio clock keep time, and let the phase decide how loud it can be.*
> *時はオーディオクロックに刻ませ、どこまで鳴らせるかは位相に決めさせよ。*

This chapter is released into the public domain under CC0 1.0 Universal. Chapter 5 (AXI input switch and inbox address map) follows.

本章は CC0 1.0 Universal のもとパブリックドメインに公開される。第 5 章（AXI 入力スイッチと inbox アドレスマップ）が続く。
