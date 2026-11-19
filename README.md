# The World Today — 18 November 2026

A newspaper front page summing up the world's news of Wednesday
18 November 2026, drawn as one 1024×1024 PNG.

## Stories

- **Lead — NVIDIA posts a record $115.8bn quarter.** Revenue rose 103%
  to $115.84bn in Q3 on data-centre sales of $107.6bn. The board
  turned down a comeback proposal from chief Jensen Huang.
- **Cyclone Akvan bears down on India.** Due ashore 20 November with
  winds of 130 km/h; 74 rescue teams stand by.
- **Ukraine.** The UN says 372 civilians were killed in October, the
  deadliest month of the year.
- **St Kitts and Nevis.** The island ends its "golden passport"
  citizenship-by-investment sales.

## Files

- `generate.py` — the generator (PIL + DejaVu). Run it to rebuild
  `entry.png` from `assets/`. Deterministic: two runs write identical
  bytes. No network, no clock, no randomness.
- `main.py` — the entry point (Python standard library only). It copies
  `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `entry.png` — the front page itself (1024×1024, under 1 MiB).
- `assets/` — the two embedded photos.

## Photos (freely licensed)

- Jensen Huang: Maurizio Pesce, CC BY 2.0, via Wikimedia Commons.
- Cyclone Akvan satellite view, 18 Nov 2026: NASA–JTWC imagery via
  Wikimedia Commons (public domain).

## Rebuild

```
python3 generate.py out/entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
