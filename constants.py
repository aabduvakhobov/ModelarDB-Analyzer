from pathlib import Path

HOME = Path.home()
MODELARDB_PATH = f"{HOME}/ModelarDB-Home/ModelarDB"
ERROR_BOUND = "0.0 0.01 0.05 0.1 0.2 0.5 1.0"
# ERROR_BOUND = "0.0"
OUTPUT_PATH = "/srv/data5/abduvoris/Ingested" # f"{HOME}/ModelarDB-Home/tempDBs/Ingested" 
DATA_PATH = "/srv/data5/abduvoris/ukwan-selected" # for estimating size of raw data
VERIFIER_PATH = f"{HOME}/ModelarDB-Home/ModelarDB-Evaluation-Tool/Verifier"

# 2 - PMC_MeanModelType, 4- FacebookGorilla, 3 - Swing, 1- UncompressedModel 
GORILLA_ID = 4
PMC_ID = 2
SWING_ID = 3