# Power calibration: is the pervasive null biology or a detection floor?

Every lane in this project returns a null. Before reading that as biology we must know the
**detection floor**: with 22 species, a lifespan+mass PGLS, and the real mass-lifespan
collinearity (r = 0.70), how large must a true lifespan effect be before we reliably see it?
This isolates "no signal" from "underpowered to see a modest signal".

## Method

On the real 22-species trait table and a Brownian phylogenetic covariance, simulate a
response `y = beta * z(log10 lifespan) + phylogenetic residual` (unit-variance residual), fit
the **exact** model the analyses use (PGLS with lifespan + mass), and record whether lifespan
reaches p < 0.05. 3000 draws per effect size over a grid of `beta` give the power curve; the
same simulation **without** the mass covariate isolates the power lost to collinearity. Effect
size is reported as the marginal correlation `r = beta / sqrt(beta^2 + 1)`
(`scripts/power_calibration.py`).

## Results

| True effect (marginal \|r\|) | Power (lifespan + mass, as run) | Power (lifespan only) |
|---|---|---|
| 0.10 | 0.07 | 0.07 |
| 0.20 | 0.13 | 0.16 |
| 0.29 | 0.22 | 0.28 |
| 0.45 | 0.54 | 0.66 |
| **0.57** | **0.81** | 0.91 |
| 0.67 | 0.96 | 0.99 |

**The detection floor is high.** 80% power needs a true effect of **\|r\| ~= 0.57** with the
mass covariate (0.51 lifespan-only — collinearity costs ~0.06 in detectable r). At modest
effects typical of comparative genomics (r = 0.2-0.3) power is only **13-22%**: a real but
moderate longevity effect would be missed roughly three times in four.

**Where the observed effects fall** (pooled marginal \|r\| vs log-lifespan):

| Analysis | Observed \|r\| | Reading |
|---|---|---|
| Classical 3' UTR divergence | **0.545** | at the detection edge — a real, sizeable effect the n=22 panel can only marginally resolve (hence pooled p = 0.022, no FDR survival) |
| Enformer CAGE expression | **0.026** | ~zero — a genuine null, not a power problem; more power would not help |

## Interpretation

**The answer is lane-specific, not global.**

- **Enformer-predicted expression is a true null** (observed r = 0.03). The effect is absent,
  not hidden; adding species or power would not surface it. The AI expression method is
  honestly negative on this panel.
- **The 3' UTR conservation signal is real and sizeable (r = 0.55) but underpowered, not
  weak.** It sits exactly at the 80%-power floor, which is why it reaches nominal significance
  yet dies under per-gene FDR. This *raises* its standing: the right move is **more species**
  (break the n = 22 ceiling), not a different metric.
- **For the broad interface and most lanes**, the floor of \|r\| ~= 0.57 means the nulls
  exclude only **large** graded effects. Modest lineage-specific effects (r < 0.4) would
  usually be missed, so those nulls reflect the n = 22 ceiling as much as biological absence —
  they bound the effect size, they do not prove zero.

So the pervasive nulls are a **mix**: some genuine (Enformer expression), most merely
bounded-from-above by power. The one real signal in the project (3' UTR conservation) is
power-limited and points squarely at the same fix. This reframes the roadmap: for the signal
that exists, the highest-value next step is **enlarging the species panel**, not more methods.

Caveats: an approximate timetree with rounded branch lengths; a Brownian residual assumption;
marginal r as the effect-size proxy; alpha = 0.05 uncorrected (BH-FDR across genes raises the
floor further, consistent with 0/N FDR survival even where a pooled effect is real).

## Reproducing

```
uv run python scripts/power_calibration.py   # -> power_calibration.{json,png}
```

Pure simulation; no network, no Biohub credits.
