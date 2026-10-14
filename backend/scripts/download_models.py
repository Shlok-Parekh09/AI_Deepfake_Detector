import os

if not os.environ.get("KAGGLE_USERNAME") or not os.environ.get("KAGGLE_KEY"):
    raise ValueError(
        "KAGGLE_USERNAME and KAGGLE_KEY environment variables must be set."
    )

from kaggle.api.kaggle_api_extended import KaggleApi  # noqa: E402

api = KaggleApi()
api.authenticate()

print(
    "Status:",
    api.kernels_status('shlokparekh08/deepfake-detector-training')
)
try:
    api.kernels_output(
        'shlokparekh08/deepfake-detector-training',
        './downloaded_models'
    )
    print("Downloaded successfully!")
except Exception as e:
    print("Download failed:", e)
