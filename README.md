# FaceTrack

A Streamlit application for detecting and tracking multiple faces in video using OpenCV Haar Cascade detection, Mean Shift tracking, and IoU-based association.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Customize the YouTube video

At the top of `app.py`, replace the value of `WALKTHROUGH_YOUTUBE_URL` with your preferred YouTube URL. The current link is a placeholder.

## Deploy

Push `app.py`, `requirements.txt`, and this README to GitHub. Deploy the repository through Streamlit Community Cloud, using `app.py` as the main file.

## OpenCV note

Install only one OpenCV package in the environment. This project uses `opencv-python-headless`; do not also install `opencv-python`, `opencv-contrib-python`, or their headless variants.
