import numpy as np
import joblib
import os
import warnings

try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
warnings.filterwarnings("ignore", message=".*trying to unpickle estimator.*")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "BPM_Model_TAVG")

# Cache for loaded models
MODEL_CACHE = {}

def _load_position_models(pos):
    pos = pos.lower().strip()

    """Load and cache models for a given position."""
    if pos in MODEL_CACHE:
        return MODEL_CACHE[pos]

    scaler_off = joblib.load(os.path.join(MODEL_DIR, f"scaler_off_{pos}.pkl"))
    pca_off    = joblib.load(os.path.join(MODEL_DIR, f"pca_off_{pos}.pkl"))
    model_off  = joblib.load(os.path.join(MODEL_DIR, f"model_off_{pos}.pkl"))

    scaler_def = joblib.load(os.path.join(MODEL_DIR, f"scaler_def_{pos}.pkl"))
    pca_def    = joblib.load(os.path.join(MODEL_DIR, f"pca_def_{pos}.pkl"))
    model_def  = joblib.load(os.path.join(MODEL_DIR, f"model_def_{pos}.pkl"))

    y_off_pred = joblib.load(os.path.join(MODEL_DIR, f"y_off_pred_{pos}.pkl"))
    y_def_pred = joblib.load(os.path.join(MODEL_DIR, f"y_def_pred_{pos}.pkl"))

    MODEL_CACHE[pos] = {
        "scaler_off": scaler_off,
        "pca_off": pca_off,
        "model_off": model_off,
        "scaler_def": scaler_def,
        "pca_def": pca_def,
        "model_def": model_def,
        "y_off_mean": np.mean(y_off_pred),
        "y_off_std": np.std(y_off_pred),
        "y_def_mean": np.mean(y_def_pred),
        "y_def_std": np.std(y_def_pred),
    }

    return MODEL_CACHE[pos]


def predict_bpm_tavg(pos, off_values, def_values):
    """
    off_values = [Poss,Pts,FGA,FTA,Off,AST,TO,FD]
    def_values = [OPoss,OPTS,OFGA,OFTA,DReb,STL,PF]
    """

    models = _load_position_models(pos)

    off = np.array(off_values, dtype=float)
    deff = np.array(def_values, dtype=float)

    # Prevent division by zero
    off_poss = off[0] if off[0] != 0 else 1.0
    def_poss = deff[0] if deff[0] != 0 else 1.0

    # OFFENSE PER 100
    off_per100 = 100 * off[[1,4,5,6,7]] / off_poss
    ts_off = 0 if (off[2] == 0 and off[3] == 0) else off[1] / (2 * (off[2] + 0.44 * off[3]))
    off_input = np.append(off_per100, ts_off).reshape(1, -1)

    # DEFENSE PER 100
    def_per100 = 100 * deff[[1,4,5,6]] / def_poss
    ts_def = 0 if deff[2] == 0 else deff[1] / (2 * (deff[2] + 0.44 * deff[3]))
    def_input = np.append(def_per100, ts_def).reshape(1, -1)

    # Predictions
    off_scaled = models["scaler_off"].transform(off_input)
    off_pca = models["pca_off"].transform(off_scaled)
    obpm_raw = models["model_off"].predict(off_pca)[0]

    def_scaled = models["scaler_def"].transform(def_input)
    def_pca = models["pca_def"].transform(def_scaled)
    dbpm_raw = models["model_def"].predict(def_pca)[0]

    # Rescale
    target_std = 5

    obpm = (
        ((obpm_raw - models["y_off_mean"]) / models["y_off_std"]) * target_std
        if models["y_off_std"] != 0 else 0
    )

    dbpm = (
        ((dbpm_raw - models["y_def_mean"]) / models["y_def_std"]) * target_std
        if models["y_def_std"] != 0 else 0
    )

    bpm = obpm + dbpm

    return round(float(obpm), 1), round(float(dbpm), 1), round(float(bpm), 1)

'''
# Example usage
pos = "TEAM"

#off_values = [Poss,Pts,FGA,FTA,Off,AST,TO,FD]
off_values = [79.491,84.232,69.566,16.667,11.165,14.267,13.766,15.168]

#def_values = [OPoss,OPTS,OFGA,OFTA,DReb,STL,PF]
def_values = [78.746,78.368,60.766,17.833,26.635,9.467,15.433]

print(predict_bpm_tavg(pos, off_values, def_values))
'''

