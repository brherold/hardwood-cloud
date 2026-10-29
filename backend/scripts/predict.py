import numpy as np
import joblib
import warnings
import os

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
MODEL_DIR = os.path.join(BASE_DIR, "BPM_Model")

POSITIONS = ["PG", "SG", "SF", "PF", "C", "TEAM"]
BPM_CACHE = {}

def _load_bpm_models(pos):
    pos = pos.upper()
    if pos in BPM_CACHE:
        return BPM_CACHE[pos]

    scaler_off = joblib.load(os.path.join(MODEL_DIR, f"scaler_off_{pos}.pkl"))
    pca_off    = joblib.load(os.path.join(MODEL_DIR, f"pca_off_{pos}.pkl"))
    model_off  = joblib.load(os.path.join(MODEL_DIR, f"model_off_{pos}.pkl"))

    scaler_def = joblib.load(os.path.join(MODEL_DIR, f"scaler_def_{pos}.pkl"))
    pca_def    = joblib.load(os.path.join(MODEL_DIR, f"pca_def_{pos}.pkl"))
    model_def  = joblib.load(os.path.join(MODEL_DIR, f"model_def_{pos}.pkl"))

    y_off_pred = joblib.load(os.path.join(MODEL_DIR, f"y_off_pred_{pos}.pkl"))
    y_def_pred = joblib.load(os.path.join(MODEL_DIR, f"y_def_pred_{pos}.pkl"))

    BPM_CACHE[pos] = {
        "scaler_off": scaler_off,
        "pca_off": pca_off,
        "model_off": model_off,
        "scaler_def": scaler_def,
        "pca_def": pca_def,
        "model_def": model_def,
        "y_off_mean": float(np.mean(y_off_pred)),
        "y_off_std": float(np.std(y_off_pred)),
        "y_def_mean": float(np.mean(y_def_pred)),
        "y_def_std": float(np.std(y_def_pred)),
    }
    return BPM_CACHE[pos]

def predict_bpm(pos, Poss, O_Poss, off_values, def_values):
    pos = pos.upper()
    data = _load_bpm_models(pos)

    scaler_off = data["scaler_off"]
    pca_off    = data["pca_off"]
    model_off  = data["model_off"]

    scaler_def = data["scaler_def"]
    pca_def    = data["pca_def"]
    model_def  = data["model_def"]

    y_off_mean = data["y_off_mean"]
    y_off_std  = data["y_off_std"]
    y_def_mean = data["y_def_mean"]
    y_def_std  = data["y_def_std"]

    Poss = max(Poss, 1)
    O_Poss = max(O_Poss, 1)

    # ==========================================
    # Offensive Features
    # off_values = [PTS, FGA, FTA, Off, AST, TO, FD]
    # ==========================================

    PTS, FGA, FTA, Off, AST, TO, FD = off_values

    denom = (2 * (FGA + 0.44 * FTA))
    TS = PTS / denom if denom != 0 else 0

    off_per100 = np.array([
        100 * PTS / Poss,
        100 * Off / Poss,
        100 * AST / Poss,
        100 * TO / Poss,
        100 * FD / Poss,
        TS
    ], dtype=float).reshape(1, -1)

    off_scaled = scaler_off.transform(off_per100)
    off_pca = pca_off.transform(off_scaled)
    obpm = model_off.predict(off_pca)[0]

    # ==========================================
    # Defensive Features
    # def_values = [OPTS, OFGA, Def, STL, PF]
    # ==========================================

    OPTS, OFGA, DREB, STL, PF = def_values

    denom_def = 2 * OFGA
    O_efG = OPTS / denom_def if denom_def != 0 else 0

    def_per100 = np.array([
        100 * OPTS / O_Poss,
        100 * DREB / O_Poss,
        100 * STL / O_Poss,
        100 * PF / O_Poss,
        O_efG
    ], dtype=float).reshape(1, -1)

    def_scaled = scaler_def.transform(def_per100)
    def_pca = pca_def.transform(def_scaled)
    dbpm = model_def.predict(def_pca)[0]




    target_mean = 0
    target_std = 5

    obpm_scaled = (
        ((obpm - y_off_mean) / y_off_std) * target_std + target_mean
        if y_off_std != 0 else target_mean
    )

    dbpm_scaled = (
        ((dbpm - y_def_mean) / y_def_std) * target_std + target_mean
        if y_def_std != 0 else target_mean
    )

    bpm_total = obpm_scaled + dbpm_scaled

    return (
        round(float(obpm_scaled), 1),
        round(float(dbpm_scaled), 1),
        round(float(bpm_total), 1),
    )

'''
# =====================================================
# Example
# =====================================================

if __name__ == "__main__":
    pos = "C"
    Poss = 60
    O_Poss = 50

    off_values = [22, 18, 4, 1, 5, 2, 3]
    def_values = [18, 16, 3, 2, 2]

    print(predict_bpm(pos, Poss, O_Poss, off_values, def_values))

'''