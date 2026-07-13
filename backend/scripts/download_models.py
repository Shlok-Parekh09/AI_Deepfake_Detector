import os
os.environ["KAGGLE_USERNAME"] = "shlokparekh08"
os.environ["KAGGLE_KEY"] = "KGAT_3318763298ba77f93465e2a991fe577f"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

print("Status:", api.kernels_status('shlokparekh08/deepfake-detector-training'))
try:
    api.kernels_output('shlokparekh08/deepfake-detector-training', './downloaded_models')
    print("Downloaded successfully!")
except Exception as e:
    print("Download failed:", e)
