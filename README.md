# Fluidization of Granular Media

**TIPE 2025 Project by Even Baudet and Valentine Labous**

This repository contains the experimental and numerical study of **fluidization in granular media**, focusing on validating Darcy and Ergun laws and developing a discrete element model (DEM) to simulate fluidization thresholds.

---

## Project Overview
- **Goal**: Observe fluidization phenomena, validate fluidization laws, and develop a numerical model.
- **Methods**:
  - Experimental: Pressure drop measurements, fluidization velocity tests.
  - Numerical: DEM with Verlet integration, collision detection, and Ergun law for fluid-particle interactions.
- **Materials**: Chia seeds, quinoa, sand, lentils.

---

## Repository Structure
   Folder          | Description                                  |
 |-----------------|----------------------------------------------|
 | `/presentation` | Slides (PDF) and figures from the TIPE.       |
 | `/doc`         | Report (in english)                           |
 | `/src`          | Python scripts for modeling/analysis.         |
 | `/data`         | Experimental data                             |

---
## Key Results
- **Experimental fluidization velocity**
- **Numerical model**: Validated against experimental data for multiple granular media.
- **Limitations**: Non-spherical particles and size distributions not yet modeled.

---
## How to Use
1. **View the presentation**:
   - (presentation/TIPE_Fluidization.pdf)
2. **Run the model**:
   - See `/src/dem_model.py` (requires Python 3.8+ and `numpy`, `matplotlib`).
3. **Reproduce experiments**:
   - Data and protocols are in `/data` and `/docs`.

---
## References
- CNRS, *Les Milieux Granulaires: entre fluide et solide* (2011).
- Ergun, S. (1952). *Fluid flow through packed columns*.
