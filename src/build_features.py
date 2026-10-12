import sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pandas as pd, numpy as np
from features import build, feature_columns, TARGET
from paths import DATA, OUT

t0 = time.time()
df = pd.read_csv(DATA)
for c in df.columns:
    if c != "profile_id":
        df[c] = df[c].astype("float32")
print("loaded", df.shape, f"{time.time()-t0:.0f}s")

df = build(df)
print("featurised", df.shape, f"{time.time()-t0:.0f}s")

feats = feature_columns(df)
keep = feats + [TARGET, "profile_id"]
df[keep].to_parquet(OUT / "features.parquet", index=False)
print(f"{len(feats)} features -> outputs/features.parquet  ({time.time()-t0:.0f}s)")
print("mem:", round(df[keep].memory_usage(deep=True).sum()/1e6), "MB")
