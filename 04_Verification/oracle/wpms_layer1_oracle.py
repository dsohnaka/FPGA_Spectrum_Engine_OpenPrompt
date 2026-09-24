#!/usr/bin/env python3
"""
WPMS Synthesizer — Layer 1 numerical oracle (Chapters 2 v1.1 – 5)
===================================================================

Reproduces every number that WPMS Layer 1 Chapters 2 v1.1, 3, 4 and 5 mark as
[Evidence: oracle], and checks it against the value quoted in the chapter.

    python3 wpms_layer1_oracle.py            # run all checks, print a summary
    python3 wpms_layer1_oracle.py -v         # also print details of every check
    python3 wpms_layer1_oracle.py CH3-EXP2   # run selected checks by ID prefix

Exit status 0 if every check passes, 1 otherwise.

Evidence class: ORACLE — host arithmetic in Python, NOT silicon. A PASS here says
the arithmetic of the specification is self-consistent; it says nothing about an
FPGA implementation until the same quantities are measured on hardware (Layer 4).

Requirements: Python 3.8+. numpy is used only by CH4-CREST (skipped, not failed,
if numpy is absent).

Reference models in this file are written to be read: exp2_q131(), l1_amplitude(),
l1_phase(), step_toward() and the slot-mapping helpers are the executable form of
Ch.3 § 3.4–3.5, Ch.4 § 4.4 and Ch.5 § 5.3, and may serve as golden models for
testbench authors.

Two measurement pitfalls are demonstrated as INFO lines (not failures):
  * CH3-EXP2  : relative error measured on outputs near the Q1.31 floor looks like
                2^-8 — that is the format's LSB, not the unit's error.
  * CH3-E2E   : a Gaussian with A0 = 1 sits exactly on the per-bin clamp (a <= 1);
                rounding pushes its apex over and the clamp looks like 2^-15.7 error.
                Test at A0 < 1.

License: CC0 1.0 Universal (provisional — the license of the verification layer is
the architect's decision). Provenance: drafted with Claude (Anthropic), 2026-09-24,
for the FPGA Spectrum Engine / WPMS Open Prompt repository.
"""

import math
import random
import sys

# --------------------------------------------------------------------------------
# Constants (Ch.1–Ch.5)
# --------------------------------------------------------------------------------
FS = 48_000                 # sample rate
CLK = 100_000_000           # clk_sys
M32 = 1 << 32
NMAX = 2048                 # bins per module
LN2 = math.log(2.0)
DB_PER_LOG2 = 20.0 * math.log10(2.0)     # 6.0206 dB per octave of amplitude

# --------------------------------------------------------------------------------
# Reference models
# --------------------------------------------------------------------------------
# exp2 unit (Ch.3 § 3.5.4): 256-entry table x degree-2 polynomial, output Q1.31.
_T = [round(2 ** (i / 256) * 2 ** 30) for i in range(256)]   # Q2.30, [1, 2)
_C1 = round(LN2 * 2 ** 30)
_C2 = round(LN2 ** 2 / 2 * 2 ** 30)


def exp2_q131(Lq):
    """a = 2^L for L given as a Q.30 integer; returns a Q1.31 integer.
    Clamp: L >= 0 -> 1 - 2^-31 ; L < -31 -> 0 (Ch.3 § 3.5.4)."""
    if Lq >= 0:
        return (1 << 31) - 1
    if Lq < -31 * (1 << 30):
        return 0
    ip = Lq >> 30                       # integer part (floor)
    fr = Lq - (ip << 30)                # fraction in [0, 1), Q0.30
    hi = fr >> 22                       # top 8 bits -> table index
    lo = fr & ((1 << 22) - 1)           # remainder < 2^-8
    p = (1 << 30) + ((_C1 * lo) >> 30) + ((_C2 * ((lo * lo) >> 30)) >> 30)
    m = (_T[hi] * p) >> 30              # Q2.30 in [1, 2)
    return (m << 1) >> (-ip)            # to Q1.31, times 2^ip


def l1_amplitude(LS0, LAD1, LAD2, LP, n_bins, MG=0):
    """L1 amplitude path of one packet (Ch.3 § 3.5.4, Ch.4 § 4.4.1).
    Slots: LS0 Q12.20, LAD1 Q8.24, LAD2 Q2.30, LP Q6.26, MG Q6.26. Returns Q1.31 list."""
    s, e, c = LS0 << 10, LAD1 << 6, LAD2      # align to Q.30 (shifts are wiring)
    lvl = (LP << 4) + (MG << 4)
    out = []
    for _ in range(n_bins):
        out.append(exp2_q131(lvl + s))
        s += e                               # 54-bit signed in hardware
        e += c
    return out


def l1_phase(PH0, PHD1, PHD2, k):
    """Phase of bin k by forward differences, mod 2^32 (Ch.3 § 3.4.2)."""
    phi, d = PH0, PHD1
    for _ in range(k):
        phi = (phi + d) % M32
        d = (d + PHD2) % M32
    return phi


def step_toward(LP, LPT, LE0):
    """Level glide (Ch.5 § 5.3.2, CR5-L1): LP <- LP + clamp(LPT - LP, -LE0, +LE0)."""
    d = LPT - LP
    return LP + max(-LE0, min(LE0, d))


def gaussian_slots(N, gamma, beta=0.0, A0=1.0, consistent=True):
    """Ch.1 § 1.4 Gaussian -> (LS0, LAD1, LAD2, LP) integers (Ch.3 § 3.5.5).
    consistent=True derives LAD1 and LS0 from the ROUNDED LAD2, which keeps the
    apex at N/2 and at level A0 (guideline for the L4 tool)."""
    LP = round(math.log2(A0) * 2 ** 26)
    LAD2 = round(-2 * gamma / LN2 * 2 ** 30)
    if consistent:
        c = LAD2 / 2 ** 30
        LAD1 = round((-c * (N - 1) / 2 - beta / LN2) * 2 ** 24)
        LS0 = round(c * N * N / 8 * 2 ** 20)
    else:
        LAD1 = round((-beta + gamma * (N - 1)) / LN2 * 2 ** 24)
        LS0 = round(-gamma * N * N / (4 * LN2) * 2 ** 20)
    return LS0, LAD1, LAD2, LP


# --------------------------------------------------------------------------------
# Check framework
# --------------------------------------------------------------------------------
CHECKS = []


def check(cid, title, ref):
    def deco(fn):
        CHECKS.append((cid, title, ref, fn))
        return fn
    return deco


class Ctx:
    def __init__(self):
        self.ok = True
        self.lines = []

    def expect(self, cond, msg):
        self.lines.append(("PASS" if cond else "FAIL") + "  " + msg)
        self.ok = self.ok and bool(cond)

    def info(self, msg):
        self.lines.append("INFO  " + msg)


def close(a, b, tol):
    return abs(a - b) <= tol


# --------------------------------------------------------------------------------
# Chapter 2 v1.1
# --------------------------------------------------------------------------------
@check("CH2-CLOCK", "clock budget per sample period per module", "Ch.2 v1.1 § 2.5.2")
def _(x):
    per = CLK / FS
    tmin = math.floor(per)
    x.expect(tmin == 2083 and math.ceil(per) == 2084, f"period = {per:.3f} clocks -> 2,083 / 2,084")
    x.expect(tmin - NMAX == 35, "margin = 2,083 - 2,048 = 35 clocks (not a per-bin budget)")
    x.expect(35 - 16 == 19, "last bin drains 16 clocks -> 19 clocks left for the flush")


@check("CH2-WIDTH", "product and accumulator widths", "Ch.2 v1.1 § 2.4.2, Ch.3 § 3.6")
def _(x):
    prod_bits = 41 + 32
    x.expect(prod_bits == 73, "Q0.40 (41 b) x Q1.31 (32 b) -> Q1.71 = 73 bits, truncated to Q1.63")
    for bins, q, name in ((2048, 12, "per module"), (4096, 13, "Compact"), (10240, 15, "Standard")):
        need = 1 + math.ceil(math.log2(bins))
        x.expect(need == q, f"{name}: {bins} bins of |x|<1 -> Q{q}.63 ({q + 63} bits)")


# --------------------------------------------------------------------------------
# Chapter 3
# --------------------------------------------------------------------------------
@check("CH3-ORIGIN", "test-origin (Dirichlet) block integers", "Ch.3 § 3.10")
def _(x):
    f0, df, A = 996.0, 1 / 256, 0.97
    OM0 = round(f0 * M32 / FS) % M32
    OMD1 = round(df * M32 / FS)
    LP = round(math.log2(A) * 2 ** 26)
    x.expect(OM0 == 89_120_571 and f"{OM0:08X}" == "054FDF3B", f"OM0 = {OM0} (0x{OM0:08X})")
    x.expect(OMD1 == 350, f"OMD1 = {OMD1}  (2^32/(256*48000) = {M32 / (256 * FS):.2f})")
    x.expect(LP == -2_948_988 and f"{LP & 0xFFFFFFFF:08X}" == "FFD30084", f"LP = {LP} (0x{LP & 0xFFFFFFFF:08X})")
    df_r = OMD1 * FS / M32
    x.expect(close((df_r - df) / df, 0.00136, 2e-5), f"realized df = {df_r:.8f} Hz ({(df_r - df) / df:+.3%})")
    x.expect(close(M32 / (OMD1 * FS), 255.653, 1e-3), f"kernel repeats every {M32 / (OMD1 * FS):.3f} s (not 256 s)")
    peak = NMAX * A
    x.expect(math.ceil(math.log2(peak)) == 11, f"coherent peak {peak:.1f} -> 11 integer bits")
    x.expect(close(20 * math.log10(peak / 2 ** 12), -6.285, 1e-3), "peak at G = 12: -6.3 dBFS")


@check("CH3-UNDERFLOW", "linear-domain k=0 amplitude underflow", "Ch.3 § 3.5.1 (1)")
def _(x):
    expect = {1e-5: 59_982, 1e-4: 0, 1e-3: 0}
    for g, q_exp in expect.items():
        sigma = 1 / math.sqrt(2 * g)
        a0 = math.exp(-g * NMAX * NMAX / 4)
        q = round(a0 * 2 ** 31)
        x.expect(q == q_exp, f"gamma={g:g} (sigma={sigma:.0f} bins): a0={a0:.2e} -> Q1.31 {q}"
                 + ("  -> SILENT PACKET" if q == 0 else ""))


@check("CH3-LINBIAS", "linear-domain Q1.31/Q4.28 recurrence bias", "Ch.3 § 3.5.1 (3)")
def _(x):
    g, N = 1e-5, NMAX
    qa = round(math.exp(-g * N * N / 4) * 2 ** 31)
    qm = round(math.exp(g * (N - 1)) * 2 ** 28)
    q2 = round(math.exp(-2 * g) * 2 ** 28)
    worst, wk = 0.0, -1
    for k in range(N):
        ref = math.exp(-g * (k - N / 2) ** 2)
        if ref > 1e-3:
            r = abs(qa / 2 ** 31 - ref) / ref
            if r > worst:
                worst, wk = r, k
        qa = (qa * qm) >> 28
        qm = (qm * q2) >> 28
    x.expect(close(worst, 0.0058, 2e-4) and wk == 1855, f"worst relative error {worst:.3%} at k = {wk}")


@check("CH3-LOGEXACT", "log-domain forward differences are exact; 54-bit bound", "Ch.3 § 3.5.2, § 3.5.4")
def _(x):
    rnd = random.Random(1)
    bad = 0
    for _ in range(2000):
        LS0, LAD1, LAD2 = (rnd.randrange(-2 ** 31, 2 ** 31) for _ in range(3))
        k = rnd.randrange(NMAX)
        s, e = LS0 << 10, LAD1 << 6
        for _ in range(k):
            s += e
            e += LAD2
        closed = (LS0 << 10) + k * (LAD1 << 6) + (k * (k - 1) // 2) * LAD2
        bad += s != closed
    x.expect(bad == 0, f"mismatches over 2,000 random packets: {bad}")
    wc = 2 ** 31 * 2 ** 10 + 2047 * 2 ** 31 * 2 ** 6 + (2047 * 2046 // 2) * 2 ** 31
    bits = math.ceil(math.log2(wc)) + 1
    x.expect(bits == 54, f"worst-case |S_k| = 2^{math.log2(wc):.2f} -> {bits} bits signed")


@check("CH3-PHASE", "phase coherence theorem (exact, zero drift)", "Ch.3 § 3.4.3")
def _(x):
    rnd = random.Random(2)
    bad = 0
    for _ in range(500):
        PH0, PHD1, PHD2, OM0, OMD1, OMD2 = (rnd.randrange(M32) for _ in range(6))
        n, k = rnd.randrange(10 ** 6), rnd.randrange(NMAX)
        got = l1_phase((PH0 + n * OM0) % M32, (PHD1 + n * OMD1) % M32, (PHD2 + n * OMD2) % M32, k)
        om = (OM0 + k * OMD1 + (k * (k - 1) // 2) * OMD2) % M32
        ref = (PH0 + k * PHD1 + (k * (k - 1) // 2) * PHD2 + n * om) % M32
        bad += got != ref
    x.expect(bad == 0, f"mismatches over 500 random (packet, n <= 1e6, k): {bad}")


@check("CH3-EXP2", "exp2 unit error; table fits one M10K", "Ch.3 § 3.5.4")
def _(x):
    rnd = random.Random(7)
    worst_lsb = worst_rel = naive = 0.0
    for _ in range(400_000):
        Lq = math.floor(-rnd.random() * 31 * 2 ** 30)
        a = exp2_q131(Lq)
        ref = 2 ** (Lq / 2 ** 30)
        worst_lsb = max(worst_lsb, abs(a - ref * 2 ** 31))
        if ref >= 2 ** -7:
            worst_rel = max(worst_rel, abs(a / 2 ** 31 - ref) / ref)
        if ref * 2 ** 31 > 2 ** 8:
            naive = max(naive, abs(a / 2 ** 31 - ref) / ref)
    x.expect(worst_lsb <= 12, f"max absolute error {worst_lsb:.2f} LSB of Q1.31")
    x.expect(worst_rel <= 2 ** -23.9, f"max relative error for a >= 2^-7: 2^{math.log2(worst_rel):.1f}")
    x.info(f"pitfall: relative error over outputs down to 2^-23 reads 2^{math.log2(naive):.1f} "
           "- that is the Q1.31 LSB near the floor, not the unit")
    x.expect(256 * 31 <= 10_240, f"table 256 x 31 bits = {256 * 31} bits -> one M10K")


@check("CH3-E2E", "end-to-end: sigma = 71 Gaussian plays in the log domain", "Ch.3 § 3.5.1-3.5.5")
def _(x):
    N, g, A0 = NMAX, 1e-4, 0.97
    for consistent, limit in ((False, -12.0), (True, -15.0)):
        LS0, LAD1, LAD2, LP = gaussian_slots(N, g, A0=A0, consistent=consistent)
        a = l1_amplitude(LS0, LAD1, LAD2, LP, N)
        nz = sum(1 for v in a if v)
        req = real = 0.0
        for k in range(N):
            ref = A0 * math.exp(-g * (k - N / 2) ** 2)
            S = LP / 2 ** 26 + LS0 / 2 ** 20 + k * LAD1 / 2 ** 24 + (k * (k - 1) // 2) * LAD2 / 2 ** 30
            if ref >= 2 ** -7:
                req = max(req, abs(a[k] / 2 ** 31 - ref) / ref)
            if 2 ** S >= 2 ** -7:
                real = max(real, abs(a[k] / 2 ** 31 - 2 ** S) / 2 ** S)
        tag = "consistent" if consistent else "naive"
        x.expect(nz == 927, f"{tag}: {nz} audible bins (linear domain: 0)")
        x.expect(real <= 2 ** -23.9, f"{tag}: exp2-only error vs realized slots 2^{math.log2(real):.1f}")
        x.expect(math.log2(req) <= limit, f"{tag}: deviation from requested Gaussian 2^{math.log2(req):.1f} "
                 "(slot quantization)")
    LS0, LAD1, LAD2, LP = gaussian_slots(N, g, A0=1.0, consistent=True)
    a = l1_amplitude(LS0, LAD1, LAD2, LP, N)
    w = 0.0
    for k in range(N):
        S = LS0 / 2 ** 20 + k * LAD1 / 2 ** 24 + (k * (k - 1) // 2) * LAD2 / 2 ** 30
        if 2 ** S >= 2 ** -7:
            w = max(w, abs(a[k] / 2 ** 31 - 2 ** S) / 2 ** S)
    x.info(f"pitfall: with A0 = 1 the apex sits on the per-bin clamp and reads 2^{math.log2(w):.1f} "
           "- test at A0 < 1")


@check("CH3-BUDGET", "sweep timing budget", "Ch.3 § 3.7")
def _(x):
    t_wake, d_l1, tmin = 4, 24, 2083
    full = t_wake + NMAX + 0 + d_l1
    x.expect(tmin - full == 7, f"full load, g = 0: {full} clocks -> slack {tmin - full}")
    x.expect(tmin - (full + 1 * 7) == 0, "full load, g = 1, P = 8: slack 0 (legal, fragile)")
    for g in (0, 1, 2, 3):
        legal = min(NMAX, tmin - t_wake - d_l1 - g * 7)
        x.info(f"g = {g}, P = 8: legal sum of N <= {legal}")


@check("CH3-QFMT", "resolutions and ranges of the log-domain slots", "Ch.3 § 3.5.3")
def _(x):
    x.expect(close(2 ** -26 * DB_PER_LOG2 * FS, 0.00431, 1e-5), "LE0 LSB = 0.0043 dB/s")
    x.expect(close(2 ** -30 * LN2 / 2, 3.228e-10, 1e-13), "LAD2 LSB -> gamma resolution 3.2e-10")
    gmax = 2048 * 4 * LN2 / NMAX ** 2
    x.expect(close(1 / math.sqrt(2 * gmax), 19.22, 0.01), f"LS0 range admits sigma >= {1 / math.sqrt(2 * gmax):.1f} bins at N = 2,048")
    x.expect(close(-8 / LN2, -11.54, 0.01), "N = 8 sigma convention -> LS0 = -11.5")


# --------------------------------------------------------------------------------
# Chapter 4
# --------------------------------------------------------------------------------
@check("CH4-CREST", "crest factor: Dirichlet vs Schroeder vs random", "Ch.4 § 4.4.3")
def _(x):
    try:
        import numpy as np
    except ImportError:
        x.info("numpy not available - skipped")
        return
    N, osr, A = NMAX, 16, 0.97
    k = np.arange(N)

    def crest(ph):
        c = np.zeros(N * osr, complex)
        c[:N] = np.exp(1j * ph)
        env = np.abs(np.fft.ifft(c)) * N * osr
        return env.max(), math.sqrt(N / 2)

    for name, ph, db, tol in (("Dirichlet (zero phase)", np.zeros(N), 36.12, 0.05),
                              ("Schroeder psi = pi/N", np.pi * k * k / N, 5.62, 0.05),
                              ("random (seed 1)", np.random.default_rng(1).uniform(0, 2 * np.pi, N), 12.17, 0.5)):
        pk, rms = crest(ph)
        x.expect(close(20 * math.log10(pk / rms), db, tol), f"{name}: crest {20 * math.log10(pk / rms):.2f} dB")
    pk, rms = crest(np.zeros(N))
    x.expect(close(20 * math.log10(A * rms / 2 ** 12), -42.4, 0.05), "Dirichlet at G = 12: RMS -42.4 dBFS")
    pk, rms = crest(np.pi * k * k / N)
    x.expect(close(20 * math.log10(A * pk / 2 ** 8), -12.7, 0.1), "Schroeder at G = 8: peak -12.7 dBFS")
    x.expect(close(20 * math.log10(A * rms / 2 ** 8), -18.3, 0.05), "Schroeder at G = 8: RMS -18.3 dBFS")
    x.expect(M32 // N == 2 ** 21 and M32 // (2 * N) == 2 ** 20, "Schroeder packet: PHD2 = 2^21, PHD1 = 2^20")


@check("CH4-MG", "master-gain slew and fade time", "Ch.4 § 4.4.1, § 4.4.5")
def _(x):
    step = 60 / (DB_PER_LOG2 * FS)
    q = round(step * 2 ** 26)
    x.expect(q == 13_933, f"60 dB/s -> {q} per sample (Q6.26)")
    target = -round(60 / DB_PER_LOG2 * 2 ** 26)
    lp, n = 0, 0
    while lp != target:
        lp, n = step_toward(lp, target, q), n + 1
    x.expect(close(n / FS, 1.0, 0.01), f"0 dB -> -60 dB in {n / FS:.3f} s")


@check("CH4-LATENCY", "I2S clocks and latency to the wire", "Ch.4 § 4.6.1, § 4.8")
def _(x):
    T, sclk = 1 / FS, 1 / (64 * FS)
    x.expect(256 * FS == 12_288_000 and 64 * FS == 3_072_000, "MCLK 12.288 MHz, SCLK 3.072 MHz")
    x.expect(close(sclk * 1e9, 325.5, 0.1), f"Delta_pre = 1 SCLK = {sclk * 1e9:.1f} ns = 4 MCLK")
    tot = T + 2 * sclk
    x.expect(close(tot * 1e6, 21.484, 1e-3) and close(tot / T, 1.031, 1e-3),
             f"sweep start -> MSB on wire: {tot * 1e6:.3f} us = {tot / T:.3f} periods")


# --------------------------------------------------------------------------------
# Chapter 5
# --------------------------------------------------------------------------------
@check("CH5-VELOCITY", "phase-shape velocity == frequency shape", "Ch.5 § 5.3.3")
def _(x):
    rnd = random.Random(5)
    worst = 0.0
    for _ in range(300):
        v, w = rnd.uniform(-50, 50), rnd.uniform(-0.05, 0.05)       # rad/s
        n, k = rnd.randrange(1, FS), rnd.randrange(NMAX)
        dA = (k * v + k * k * w) * n / FS                            # move delta-phi and psi
        df, al = v / (2 * math.pi), w / (2 * math.pi)                # offset Delta-f and alpha
        dB = n * (k * (df + al) / FS + (k * (k - 1) // 2) * (2 * al) / FS) * 2 * math.pi
        worst = max(worst, abs(((dA - dB + math.pi) % (2 * math.pi)) - math.pi))
    x.expect(worst < 1e-9, f"max phase difference over 300 trials: {worst:.1e} rad")


@check("CH5-GLIDE", "level glide reaches its target exactly and never overshoots", "Ch.5 § 5.3.2 (CR5-L1)")
def _(x):
    rnd = random.Random(11)
    ok = True
    for _ in range(2000):
        lp, lpt = rnd.randrange(-32 << 26, 1), rnd.randrange(-32 << 26, 1)
        rate = rnd.randrange(0, 1 << 22)
        prev = lp
        for _ in range(4000):
            nxt = step_toward(prev, lpt, rate)
            if abs(nxt - prev) > rate or (lpt - prev) * (lpt - nxt) < 0:
                ok = False
            prev = nxt
        if rate and abs(lpt - lp) <= 4000 * rate and prev != lpt:
            ok = False
    x.expect(ok, "2,000 random glides: steps <= rate, no overshoot, exact arrival")
    x.expect(step_toward(-123, 456, 0) == -123, "LE0 = 0 freezes the level")


@check("CH5-MASK", "mask presets", "Ch.5 Appendix 5.B")
def _(x):
    def m(bits):
        return sum(1 << b for b in bits)
    presets = {
        "RETUNE": ([0x0, 0x1, 0x3, 0x4, 0x5, 0x9, 0xA, 0xB, 0xC, 0xF], 0x9E3B),
        "RESEED": ([i for i in range(16) if i not in (0xD, 0xE)], 0x9FFF),
        "LEVEL": ([0x5, 0x9], 0x0220),
        "PITCH": ([0xA, 0xB, 0xC], 0x1C00),
        "PHASE_RESET": ([0x6, 0x7, 0x8], 0x01C0),
    }
    for name, (bits, val) in presets.items():
        x.expect(m(bits) == val and not (val & 0x6000), f"{name} = 0x{val:04X} (bits 13-14 clear)")


@check("CH5-MAP", "address-map spans", "Ch.5 § 5.6")
def _(x):
    last = lambda M: 0x200 + 0x100 * M - 1
    x.expect(last(2) == 0x3FF, "Compact (M = 2) ends at word 0x3FF")
    x.expect(last(10) == 0xBFF, "Extended (M = 10) ends at word 0xBFF")
    x.expect(0x0FF < 0x200, "global region 0x000-0x0FF does not overlap module 0")


# --------------------------------------------------------------------------------
def main(argv):
    verbose = "-v" in argv
    sel = [a for a in argv if not a.startswith("-")]
    n_fail = 0
    print(f"WPMS Layer 1 oracle — evidence class ORACLE (not silicon)\n")
    for cid, title, ref, fn in CHECKS:
        if sel and not any(cid.startswith(s) for s in sel):
            continue
        x = Ctx()
        fn(x)
        n_fail += not x.ok
        print(f"[{'PASS' if x.ok else 'FAIL'}] {cid:13s} {title}  ({ref})")
        if verbose or not x.ok:
            for line in x.lines:
                print("        " + line)
    print(f"\n{'ALL PASS' if n_fail == 0 else f'{n_fail} CHECK(S) FAILED'}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
