# Overview
Designed and implemented an engineering tool for spacecraft trajectory analysis and maneuver planning. The application simulates orbital transfers, Δv requirements, and parameter evolution, supporting mission design and aerospace engineering workflows.

# Features
- Input parameters via a Parameters dialog
- Quick setup via Presets dialog (Earth defaults + LEO/GEO/MEO)
- Dynamic orbit visualization with matplotlib
- Δv arrows and markers on orbit plots
- Results panel with Δv and transfer time
- About dialog with project description

# Screenshots
<img width="1398" height="887" alt="Preview_1" src="https://github.com/user-attachments/assets/7b4c7c61-e9b2-49e6-8861-799c173277c5" />
<img width="1398" height="887" alt="Preview_2" src="https://github.com/user-attachments/assets/45780f0c-aaae-42e8-b376-fc2ba8df3d31" />

# Installation
1. Clone the repository
- git clone https://github.com/YOUR_USERNAME/OrbitalMechanicsAnalyzer.git
- cd OrbitalMechanicsAnalyzer

2. Install dependencies  
- pip install pyqt5 matplotlib numpy

3. Run the app
- python main.py

# Mathematical Background
Transfer orbit semi-major axis:
- a_trans = (r1 + r2) / 2
Transfer orbit eccentricity:
- e = |r2 - r1| / (r1 + r2)
Velocity at periapsis & apoapsis:
- v_peri = sqrt(μ * (2/r1 - 1/a_trans))
- v_apo = sqrt(μ * (2/r2 - 1/a_trans))
Required Δv values:
- Δv1 = |v_peri - v1|
- Δv2 = |v2 - v_apo|
- Δv_tot = Δv1 + Δv2
Transfer time:
- t_trans = π * sqrt(a_trans³ / μ)

# License
MIT License – feel free to use, modify, and share.
