# HKH Glacier 3D, Deep Learning Glacier Segmentation & Visualization

> A deep learning pipeline for segmenting glaciers in the Hindu Kush Himalaya (HKH) region from satellite imagery, paired with an interactive 3D visualization that lets users compare glacier extent year-by-year (2008–2026) against a DEM-based terrain model.

---

## Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Pipeline](#pipeline)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Training](#training)
- [Inference & Visualization](#inference--visualization)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

Glaciers in the Hindu Kush Himalaya region are retreating at an accelerating rate, and monitoring that change at scale requires automated, satellite-driven segmentation rather than manual delineation. This project trains a deep learning model to segment glacier extent from multi-band satellite imagery and elevation data, then renders the results as an interactive 3D terrain visualization, letting a user pick a year (or two years to compare) and see how the glacier has shrunk or grown against the original 2002–2008 training baseline.

## Motivation

Existing glacier inventories are often static snapshots. This project aims to build a properly engineered, open-source pipeline, not a one-off notebook, that:

- Learns glacier boundaries directly from raw satellite + elevation data
- Generalizes beyond the training window using on-demand imagery for years outside the original dataset
- Communicates change visually in 3D rather than as flat masks, which is far more intuitive for understanding shrinkage/growth over time

## Dataset

- **Source:** HKH glacier dataset, spanning **2002–2008**, hosted on **DagsHub** and version-controlled with **DVC**
- **Format:** 10 `.tar.gz` shards, each containing an `images/` and `masks/` folder
  - `images/`: `512×512×7` channel patches
  - `masks/`: `512×512` single-channel glacier masks
- **Provenance:** 34 large source images sliced into 512×512 patches (`slice_0` … `slice_33`, ~209 patches each), then sharded into `shard_00`–`shard_09` (710 image/mask pairs per shard)
- **Bands:** Raw (uncalibrated) Landsat 7 values, optical bands are Blue, Green, Red, Narrow NIR, SWIR 1, SWIR 2, plus a DEM/elevation band
- **Normalization:** Empirical per-band mean/std computed from the training set is used for z-scoring, rather than the pretrained Prithvi reflectance statistics, since the source imagery is uncalibrated

For years outside the 2002–2008 range (up to 2026), imagery is pulled on demand from **Google Earth Engine (GEE)** at inference time rather than bundled into the dataset.

## Model Architecture

**`DualEncoderGlacierModel`**  a dual-encoder design that fuses a large pretrained remote-sensing foundation model with a lightweight terrain-aware CNN:

| Component | Details |
|---|---|
| **Encoder A** | Frozen **Prithvi-EO-2.0-300M-TL** (ViT, single time-step mode), ingests 6 optical bands → 32×32 grid of 1024-dim embeddings |
| **Encoder B** | Custom 2D CNN over the 1-channel DEM/elevation band, 4 stride-2 convs down to 32×32, extracting spatial gradients (slopes, ridges, valleys); `dem_channels` tuned via Optuna over `[32, 64, 128]` |
| **Fusion** | Channel-wise concatenation of both encoder outputs, compressed by a `fusion_conv` to 256 channels (fixed, not Optuna-searched) |
| **Decoder** | 4× `ConvTranspose2d` stages upsampling back to 512×512, followed by a final `Conv2d` producing a single-channel logit mask |

The optical branch stays frozen to leverage Prithvi's pretraining, while the DEM branch and fusion/decoder layers are trained from scratch on the HKH dataset.

## Pipeline

1. **Data versioning**, imagery and masks tracked via DVC, pulled from DagsHub
2. **Preprocessing**, per-band z-score normalization using empirically computed statistics
3. **Training**, run on free-tier Google Colab, streaming data from DagsHub via DVC
4. **Hyperparameter search**, Optuna sweeps over DEM encoder width
5. **Inference (out-of-range years)**, fetch matching imagery from Google Earth Engine for the requested year(s)
6. **Visualization**, render DEM as a 3D heightmap with the predicted glacier mask overlaid, and support year-over-year comparison

## Tech Stack

- **Model/Training:** PyTorch, Prithvi-EO-2.0-300M-TL, Optuna
- **Data versioning:** DVC + DagsHub
- **Training compute:** Google Colab (free tier)
- **External imagery:** Google Earth Engine (GEE)
- **Visualization:** 3D DEM heightmap rendering with mask overlay

## Project Structure

```
hkh-glacier-3d/
├── data/
│   ├── shard_00 ... shard_09/
│   │   ├── images/        # 512x512x7 .npy patches
│   │   └── masks/         # 512x512 .npy masks
│   └── dvc.yaml
├── src/
│   ├── model.py            # DualEncoderGlacierModel definition
│   ├── train.py             # Training loop
│   ├── preprocess.py        # Normalization, patching utilities
│   ├── gee_fetch.py         # On-demand imagery fetch for out-of-range years
│   └── visualize.py         # 3D DEM + mask rendering
├── notebooks/
│   └── colab_training.ipynb
├── requirements.txt
└── README.md
```

## Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/hkh-glacier-3d.git
cd hkh-glacier-3d

# Install dependencies
pip install -r requirements.txt

# Pull versioned data via DVC (requires DagsHub credentials)
dvc pull
```

## Training

Training is designed to run on Google Colab's free tier, streaming shards from DagsHub via DVC rather than requiring local storage of the full dataset.

```bash
python src/train.py --config configs/train.yaml
```

Key config options include DEM encoder channel width (searched via Optuna), learning rate, and shard subset for quick iteration.

## Inference & Visualization

```bash
python src/visualize.py --year 2020 --compare-year 2008
```

This fetches (or loads cached) imagery for the requested year(s), runs segmentation, and renders an interactive 3D comparison of glacier extent against the DEM terrain.

## Roadmap

- [ ] Finalize Optuna search over DEM encoder width
- [ ] Automate GEE imagery fetch + caching layer
- [ ] Build interactive frontend for year selection and 3D comparison
- [ ] Package as open-source release with documentation and example notebooks
- [ ] Evaluate against independent glacier inventory data for validation

## License

*(To be determined, project is intended for open-source release.)*