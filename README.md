Astro_Engine/
│
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── astro_engine/
│   ├── __init__.py
│   ├── app.py
│   ├── requirements.txt
│   ├── engine/
│   ├── ephe/
│   └── venv/
├── .git/
└── .vscode/

Main Components
1. astro_engine/
This is the core source directory for your Flask web application.

init.py
: Marks the directory as a Python package.
app.py
: The main entry point for the Flask app. It likely initializes the app, registers blueprints, and sets up API endpoints.
requirements.txt
: Lists Python dependencies, including pyswisseph for astronomical calculations.
venv/: Python virtual environment (not part of source, but present for local development).
2. astro_engine/engine/
This folder organizes the core astrological calculation logic and API routing.

ApiEndPoints.txt
: Documentation or listing of all API endpoints.
ashatakavargha/: Logic for Ashtakavarga calculations.
dashas/: Modules for various Dasha systems.
divisionalCharts/: Handles divisional chart calculations (e.g., D9, D10).
kpSystem/: Implements Krishnamurti Paddhati (KP) ayanamsa logic.
lagnaCharts/: Lagna (ascendant) chart calculations.
natalCharts/: Natal (birth) chart calculations.
numerology/: Numerology-related calculations.
ramanDivisionals/: Raman ayanamsa and divisional chart logic.
routes/: Contains Flask route definitions, likely organized by ayanamsa or chart type.
Each of these subfolders contains Python modules and possibly further subdirectories for detailed components.

3. astro_engine/ephe/
This folder contains astronomical data files and resources needed for calculations.

.se1
 files: Swiss Ephemeris data files for planetary positions.
sat/: Likely contains satellite or specific astronomical data.
Text files (
seasnam.txt
, 
sefstars.txt
, etc.): Star names, orbital elements, and other reference data.
astlistn.md
 & 
list.zip
: Large files, possibly containing lists of astrological objects or zipped data.
4. Project-Level Files
.dockerignore
, 
Dockerfile
, 
docker-compose.yml
: Used for containerization and deployment.
.git/: Version control.
.vscode/: Editor settings.
Example Project Structure (Tree View)
Astro_Engine/
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── astro_engine/
│   ├── __init__.py
│   ├── app.py
│   ├── requirements.txt
│   ├── engine/
│   │   ├── ApiEndPoints.txt
│   │   ├── ashatakavargha/
│   │   ├── dashas/
│   │   ├── divisionalCharts/
│   │   ├── kpSystem/
│   │   ├── lagnaCharts/
│   │   ├── natalCharts/
│   │   ├── numerology/
│   │   ├── ramanDivisionals/
│   │   └── routes/
│   ├── ephe/
│   │   ├── *.se1
│   │   ├── sat/
│   │   ├── *.txt
│   │   └── ...
│   └── venv/
├── .git/
└── .vscode/
Summary
astro_engine/: Main application code.
engine/: Astrological calculation modules, organized by system and chart type.
ephe/: Astronomical data files (Swiss Ephemeris).
API: Exposed via Flask, organized by ayanamsa system (Lahiri, KP, Raman), and chart type.
Deployment: Dockerized for easy deployment.
If you want a visual tree or more details on any subfolder/module, let me know!


