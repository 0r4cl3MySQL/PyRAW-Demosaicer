# PyRAW-Demosaicer

Python RAW image demosaicing app

## Features
- Bayer demosaic (OpenCV)
- RAW pattern normalization (G2 → G)
- Stage-based processing

## Notes
Some RAW files use Bayer patterns with dual green (value 3).
This is normalized before OpenCV demosaic to avoid crashes.