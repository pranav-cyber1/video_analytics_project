import os
import tempfile
from pathlib import Path
import cv2
import numpy as np
import streamlit as st

st.set_page_config(page_title="FaceTrack | Project Report", page_icon="◉", layout="wide")

CSS = """
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none;}
.stApp {background:#fbfcfe; color:#263445;}
.block-container {max-width:1500px; padding:6.0rem 2rem 4rem;}
.topbar {
    position:fixed; top:0; left:0; right:0; height:68px; z-index:9999;
    background:#29465b; color:#fff; display:flex; align-items:center;
    padding:0 max(calc((100vw - 1450px)/2), 30px); gap:16px;
    box-shadow:0 2px 9px rgba(22,42,58,.18); font-family:Arial,sans-serif;
}
.topbar .mark {font-size:27px; font-weight:700; color:#c8e0df;}
.topbar .name {font-size:22px; font-weight:700; letter-spacing:.01em;}
.topbar .tag {margin-left:auto; font-size:14px; color:#d8e5ec;}
.doc-nav {position:sticky; top:88px; padding:12px 15px 24px 0; border-right:1px solid #dce4ea;
    font:14px/1.6 Arial,sans-serif; color:#34495a; max-height:calc(100vh - 110px); overflow:auto;}
.doc-nav .nav-title {color:#477b80; margin:0 0 10px; font-weight:700; font-size:15px;}
.doc-nav a {display:block; color:#34495a; text-decoration:none; padding:5px 8px;
    border-left:2px solid #dce4ea; margin-left:0;}
.doc-nav a.sub {padding-left:22px; font-size:13px;}
.doc-nav a:hover {color:#28777b; border-left:3px solid #4c9292; background:#f0f6f7;}
.article {max-width:1000px; padding:0 22px 24px 30px; font-family:Arial,sans-serif; color:#263445;}
.team-card {
        position:sticky; top:92px; width:100%; box-sizing:border-box;
        margin:8px 0 24px; padding:19px 16px 18px;
        background:linear-gradient(155deg,#ffffff 0%,#f2f7f8 100%);
        border:1px solid #d6e3e6; border-radius:15px;
        box-shadow:0 8px 22px rgba(35,65,79,.08);
        font-family:Arial,sans-serif; color:#29465b;
    }
    .team-card .team-kicker {font-size:10px; letter-spacing:.14em; font-weight:800; color:#56858a; margin-bottom:7px;}
    .team-card .team-heading {font-size:20px; line-height:1.25; font-weight:750; color:#29465b; margin:0 0 15px;}
    .team-member {display:flex; align-items:center; gap:10px; padding:10px 9px; margin:8px 0;
        background:#fff; border:1px solid #e0e9eb; border-radius:10px;}
    .team-index {flex:0 0 28px; height:28px; display:flex; align-items:center; justify-content:center;
        border-radius:8px; background:#e7f0f1; color:#315e70; font-size:11px; font-weight:800;}
    .team-name {font-size:13px; line-height:1.4; font-weight:650; color:#334f60; overflow-wrap:anywhere;}
    .team-guidance {border-top:1px solid #dce7e9; margin-top:17px; padding-top:15px;}
    .team-guidance-label {font-size:10px; letter-spacing:.12em; font-weight:800; color:#6b858e; margin-bottom:7px;}
    .team-guidance-title {font-size:12px; line-height:1.55; font-weight:700; color:#29465b;}
    .team-guidance-place {font-size:12px; color:#617985; margin-top:3px;}
    @media(max-width:1050px) {
        .team-card {position:relative; top:auto; margin:18px 0;}
        .team-member {padding:9px 8px;}
    }
.article h1 {font-size:36px; line-height:1.22; font-weight:650; color:#20384b; margin:0 0 12px;}
.article h2 {font-size:28px; line-height:1.3; font-weight:650; color:#29465b; margin:44px 0 16px; padding-top:8px;}
.article h3 {font-size:21px; font-weight:650; color:#355d70; margin:30px 0 12px;}
.article h4 {font-size:17px; color:#3d6572; margin:22px 0 8px;}
.article p, .article li {font-size:15.5px; line-height:1.82;}
.article p {margin:12px 0 18px;}
.article li {margin:7px 0;}
.article .author {color:#56858a; font-size:15px; margin:0 0 28px;}
.article .rule {border-top:1px solid #dce5e9; margin:34px 0;}
.article .note {padding:12px 16px; background:#f0f6f7; border-left:4px solid #6b9b9d; color:#425b68;}
.article code {background:#edf2f5; color:#29465b; padding:3px 6px; border-radius:4px;}
.article pre {border:1px solid #dce5e9; border-radius:8px;}
.math-caption {color:#586b78; font-size:14px; margin-top:-4px;}
.diagram-wrap {background:#fff; border:1px solid #dbe5e9; border-radius:12px; padding:18px; margin:20px 0 26px; overflow-x:auto;}
.run-panel {background:#f2f7f8; border:1px solid #d5e3e6; border-radius:16px; padding:24px 26px; margin:20px 0;}
.upload-card {background:linear-gradient(145deg,#f6fafb,#edf4f5); border:1px solid #d2e1e5; border-radius:18px; padding:22px; margin:16px 0 20px;}
.upload-title {font-size:20px; font-weight:700; color:#29465b; margin:0 0 6px;}
.upload-description {font-size:14px; line-height:1.65; color:#536d7a; margin:0 0 15px;}
[data-testid="stFileUploader"] {background:transparent; padding:0; width:100%;}
[data-testid="stFileUploader"] label {color:#29465b !important; font-size:15px !important; font-weight:700 !important; opacity:1 !important; margin-bottom:9px !important;}
[data-testid="stFileUploaderDropzone"] {
    background:#ffffff !important; border:2px dashed #7da5ad !important;
    border-radius:15px !important; min-height:158px !important;
    padding:24px 22px !important; transition:background .2s ease,border-color .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {background:#f4f9fa !important; border-color:#477c89 !important;}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] *,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {color:#29465b !important; opacity:1 !important;}
[data-testid="stFileUploaderDropzoneInstructions"] {gap:8px !important;}
[data-testid="stFileUploaderDropzoneInstructions"] div {font-size:15px !important; font-weight:600 !important;}
[data-testid="stFileUploaderDropzone"] button {
    background:#315e70 !important; color:#ffffff !important; border:1px solid #315e70 !important;
    border-radius:9px !important; min-height:43px !important; padding:0 20px !important;
    font-weight:700 !important;
}
[data-testid="stFileUploaderDropzone"] button *,
[data-testid="stFileUploaderDropzone"] button p {color:#ffffff !important; opacity:1 !important;}
[data-testid="stFileUploader"] small {color:#526b78 !important; opacity:1 !important;}
.stButton>button, .stDownloadButton>button {
    min-height:48px; border-radius:9px; border:1px solid #294f62;
    background:#315e70; color:#fff !important; font-weight:700; padding:0 22px;
}
.stButton>button[kind="primary"] {min-height:56px; font-size:16px; letter-spacing:.01em; box-shadow:0 5px 14px rgba(49,94,112,.18);}
.stButton>button[kind="primary"] *, .stDownloadButton>button * {color:#fff !important; opacity:1 !important;}
.stButton>button:hover, .stDownloadButton>button:hover {background:#24485a; border-color:#24485a; color:#fff !important;}
[data-testid="stAlert"] {border-radius:8px;}
@media(max-width:850px) {
    .block-container {padding:5.4rem 1rem 2rem;}
    .doc-nav {position:relative; top:auto; border-right:0; border-bottom:1px solid #dce4ea; max-height:none;}
    .article {padding:12px 0;}
    .article h1 {font-size:29px;}
    .topbar {padding:0 16px;}
    .topbar .tag {display:none;}
}
</style>
<div class="topbar"><span class="mark">◉</span><span class="name">FaceTrack</span>
<span class="tag">Face Detection & Tracking · Technical Project Report</span></div>
"""
st.markdown(CSS, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"

def get_cascade():
    # FaceTrack uses the legacy Haar Cascade API available in OpenCV 4.x.
    # OpenCV 5 moved this API into the contrib xobjdetect module.
    if not hasattr(cv2, "CascadeClassifier"):
        version = getattr(cv2, "__version__", "unknown")
        raise RuntimeError(
            f"Incompatible OpenCV version ({version}): cv2.CascadeClassifier is not available. "
            "This app requires OpenCV 4.x. In the repository root, set "
            "requirements.txt to opencv-python-headless==4.14.0.94 and remove "
            "opencv-python, opencv-contrib-python, and opencv-contrib-python-headless. "
            "Then push the change and reboot the Streamlit app to rebuild its environment."
        )

    cascade_dir = getattr(getattr(cv2, "data", None), "haarcascades", None)
    if not cascade_dir:
        raise RuntimeError(
            "OpenCV did not expose its Haar Cascade data directory. "
            "Verify that opencv-python-headless==4.14.0.94 is installed."
        )

    cascade_path = Path(cascade_dir) / "haarcascade_frontalface_default.xml"
    if not cascade_path.is_file():
        raise RuntimeError(
            f"The Haar Cascade XML file was not found at {cascade_path}. "
            "Reinstall the pinned OpenCV 4.x dependency and rebuild the app."
        )

    cascade = cv2.CascadeClassifier(str(cascade_path))
    if cascade.empty():
        raise RuntimeError(f"OpenCV could not load the Haar Cascade file: {cascade_path}")
    return cascade


@st.cache_resource
def load_cascade():
    return get_cascade()


def detect_faces(frame, cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    boxes = cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=5, minSize=(28, 28))
    return [tuple(map(int, b)) for b in boxes]


def iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - inter
    return inter / union if union else 0.0


def histogram(frame, box):
    x, y, w, h = box
    roi = frame[max(0, y):max(0, y) + h, max(0, x):max(0, x) + w]
    if roi.size == 0:
        return None
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array((0, 25, 25)), np.array((180, 255, 255)))
    if cv2.countNonZero(mask) == 0:
        mask = None
    hist = cv2.calcHist([hsv], [0], mask, [32], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    return hist


def make_track(frame, box, track_id):
    hist = histogram(frame, box)
    if hist is None:
        return None
    x, y, w, h = box
    return {"id": track_id, "box": box, "hist": hist, "missed": 0, "trail": []}


def process_video(input_path, preview, progress, status):
    cascade = load_cascade()
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError("The uploaded video could not be opened. Try a standard MP4, MOV, or AVI file.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps = fps if np.isfinite(fps) and fps > 0 else 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if width < 1 or height < 1:
        cap.release()
        raise RuntimeError("The uploaded video has invalid dimensions.")
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not create the output video. Try a shorter MP4 clip.")
    tracks, next_id, frame_index, total_detections = {}, 1, 0, 0
    max_frames = 500
    try:
        while frame_index < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            frame_index += 1
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            for tr in list(tracks.values()):
                x, y, w, h = tr["box"]
                x = max(0, min(x, width - 1)); y = max(0, min(y, height - 1))
                w = max(1, min(w, width - x)); h = max(1, min(h, height - y))
                back = cv2.calcBackProject([hsv], [0], tr["hist"], [0, 180], 1)
                _, win = cv2.meanShift(back, (x, y, w, h), (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1))
                nx, ny, nw, nh = map(int, win)
                if abs(nx - x) + abs(ny - y) < 90:
                    tr["box"] = (nx, ny, nw, nh)
                    tr["missed"] = 0
                else:
                    tr["missed"] += 1
            if frame_index == 1 or frame_index % 8 == 0:
                detections = detect_faces(frame, cascade)
                total_detections += len(detections)
                pairs = sorted(((iou(tr["box"], box), tid, di) for tid, tr in tracks.items() for di, box in enumerate(detections)), reverse=True)
                used_tracks, used_dets = set(), set()
                for score, tid, di in pairs:
                    if score < 0.12 or tid in used_tracks or di in used_dets:
                        continue
                    box = detections[di]
                    hist = histogram(frame, box)
                    if hist is not None:
                        tracks[tid]["box"] = box
                        tracks[tid]["hist"] = hist
                        tracks[tid]["missed"] = 0
                        used_tracks.add(tid); used_dets.add(di)
                for di, box in enumerate(detections):
                    if di not in used_dets:
                        tr = make_track(frame, box, next_id)
                        if tr is not None:
                            tracks[next_id] = tr
                            next_id += 1
            tracks = {tid: tr for tid, tr in tracks.items() if tr["missed"] <= 16}
            rendered = frame.copy()
            for tid, tr in tracks.items():
                if tr["missed"]:
                    continue
                x, y, w, h = tr["box"]
                color = ((53 * tid + 75) % 150 + 70, (89 * tid + 55) % 150 + 70, (37 * tid + 110) % 150 + 70)
                cv2.rectangle(rendered, (x, y), (x + w, y + h), color, 2, cv2.LINE_AA)
                label_y = max(20, y - 7)
                cv2.rectangle(rendered, (x, label_y - 23), (x + 98, label_y + 2), color, -1)
                cv2.putText(rendered, f"FACE ID {tid}", (x + 5, label_y - 5), cv2.FONT_HERSHEY_SIMPLEX, .48, (9, 18, 27), 1, cv2.LINE_AA)
                center = (x + w // 2, y + h // 2)
                tr["trail"].append(center); tr["trail"] = tr["trail"][-16:]
                for a, b in zip(tr["trail"][:-1], tr["trail"][1:]):
                    cv2.line(rendered, a, b, (104, 230, 210), 2, cv2.LINE_AA)
            writer.write(rendered)
            if frame_index == 1 or frame_index % 5 == 0:
                preview.image(cv2.cvtColor(rendered, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
                stage = "Mean Shift tracking" if frame_index % 8 not in (0, 1) else "Haar Cascade detection + IoU association"
                status.markdown(f"**Live workflow:** `Video input` → `Face detection` → `Mean Shift tracking` → `IoU association` → `Output export`\n\nProcessing frame **{frame_index:,}** · {sum(t['missed'] == 0 for t in tracks.values())} active tracks · Current stage: **{stage}**")
                if total:
                    progress.progress(min(frame_index / min(total, max_frames), 1.0), text=f"Processing frame {frame_index:,}")
    finally:
        cap.release(); writer.release(); progress.empty()
    if frame_index == 0:
        os.remove(output_path)
        raise RuntimeError("No readable frames were found in this video.")
    return output_path, {"frames": frame_index, "tracks": next_id - 1, "detections": total_detections, "width": width, "height": height}


def load_demo_frame():
    demo_path = Path(__file__).with_name("facetrack_group_demo.png")
    if not demo_path.is_file():
        return None
    image = cv2.imread(str(demo_path))
    return image


def create_demo_data():
    frame = load_demo_frame()
    if frame is None:
        return None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    cascade = load_cascade()
    boxes = detect_faces(frame, cascade)
    if not boxes:
        return {"frame": frame, "gray": gray, "equalized": equalized, "boxes": [], "tracks": []}

    annotated = frame.copy()
    for idx, (x, y, w, h) in enumerate(boxes, 1):
        cv2.rectangle(annotated, (x, y), (x+w, y+h), (40, 150, 100), 3)
        cv2.putText(annotated, f"FACE ID {idx}", (x, max(25, y-9)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 90, 65), 2, cv2.LINE_AA)

    # Use the largest detected face as a concrete, reproducible worked example.
    box = max(boxes, key=lambda b: b[2]*b[3])
    x, y, w, h = box
    roi = frame[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0, 25, 25)), np.array((180, 255, 255)))
    hist = cv2.calcHist([hsv_roi], [0], mask if cv2.countNonZero(mask) else None, [32], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

    shifted = cv2.warpAffine(frame, np.float32([[1, 0, 12], [0, 1, 0]]),
                             (frame.shape[1], frame.shape[0]))
    hsv_shifted = cv2.cvtColor(shifted, cv2.COLOR_BGR2HSV)
    back = cv2.calcBackProject([hsv_shifted], [0], hist, [0, 180], 1)
    _, moved_box = cv2.meanShift(back, box,
        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1))
    moved_box = tuple(map(int, moved_box))

    # Exact weighted centroid of the back-projection inside the initial window.
    bx, by, bw, bh = box
    patch = back[by:by+bh, bx:bx+bw].astype(np.float64)
    yy, xx = np.mgrid[by:by+bh, bx:bx+bw]
    mass = patch.sum()
    if mass > 0:
        centroid_x = float((patch * xx).sum() / mass)
        centroid_y = float((patch * yy).sum() / mass)
    else:
        centroid_x, centroid_y = bx + bw/2, by + bh/2

    track_view = shifted.copy()
    mx, my, mw, mh = moved_box
    cv2.rectangle(track_view, (bx, by), (bx+bw, by+bh), (230, 150, 30), 3)
    cv2.rectangle(track_view, (mx, my), (mx+mw, my+mh), (30, 160, 70), 3)
    cv2.circle(track_view, (int(centroid_x), int(centroid_y)), 7, (0, 0, 255), -1)

    # The known +12 px translation provides a corresponding detection for the IoU example.
    detected_next = (min(bx+12, frame.shape[1]-bw), by, bw, bh)
    association_view = shifted.copy()
    cv2.rectangle(association_view, (mx, my), (mx+mw, my+mh), (230, 150, 30), 3)
    dx, dy, dw, dh = detected_next
    cv2.rectangle(association_view, (dx, dy), (dx+dw, dy+dh), (30, 160, 70), 3)

    gray_sample = gray[y:y+min(4,h), x:x+min(6,w)]
    hsv_sample = hsv_roi[:min(4,h), :min(6,w), :]
    return {
        "frame": frame, "gray": gray, "equalized": equalized, "boxes": boxes,
        "annotated": annotated, "box": box, "roi": roi, "hsv_roi": hsv_roi,
        "hist": hist, "back": back, "shifted": shifted, "moved_box": moved_box,
        "track_view": track_view, "association_view": association_view,
        "centroid": (centroid_x, centroid_y), "gray_sample": gray_sample,
        "hsv_sample": hsv_sample, "detected_next": detected_next,
        "iou": iou(moved_box, detected_next)
    }


def show_frame_demo(stage):
    if "face_demo" not in st.session_state:
        st.session_state.face_demo = create_demo_data()
    d = st.session_state.face_demo
    if d is None:
        st.warning("The bundled demonstration image facetrack_group_demo.png is missing. Keep it in the same folder as this Python file.")
        return
    if stage == "pipeline":
        st.image(cv2.cvtColor(d["annotated"], cv2.COLOR_BGR2RGB),
                 caption=f"Input frame with {len(d['boxes'])} Haar detections and illustrative track IDs", use_container_width=True)
        cols = st.columns(4)
        for col, label, image in zip(cols,
            ["1 · Original frame", "2 · Grayscale", "3 · Equalised", "4 · Detected faces"],
            [d["frame"], d["gray"], d["equalized"], d["annotated"]]):
            with col:
                st.image(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB) if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption=label, use_container_width=True)
    elif stage == "detection":
        a, b = st.columns(2)
        with a:
            st.image(cv2.cvtColor(d["gray"], cv2.COLOR_GRAY2RGB), caption="Grayscale frame", use_container_width=True)
        with b:
            st.image(cv2.cvtColor(d["annotated"], cv2.COLOR_BGR2RGB), caption="Haar Cascade detections", use_container_width=True)
        st.caption(f"Detected {len(d['boxes'])} candidate face regions. Worked ROI (largest detected face): x={d['box'][0]}, y={d['box'][1]}, width={d['box'][2]}, height={d['box'][3]}.")
        st.write("Actual grayscale pixel values from the upper-left 4 × 6 part of that detected face crop:")
        st.dataframe(d["gray_sample"], hide_index=True, use_container_width=True)
        x, y, w, h = d["box"]
        gray_value = int(d["gray"][y, x])
        B, G, R = map(int, d["frame"][y, x])
        st.latex(r"Y=0.114B+0.587G+0.299R")
        st.code(f"At pixel (x={x}, y={y}): B={B}, G={G}, R={R}\nY = 0.114({B}) + 0.587({G}) + 0.299({R}) = {gray_value} (rounded)", language="text")
    elif stage == "tracking":
        a, b = st.columns(2)
        with a:
            st.image(cv2.cvtColor(d["roi"], cv2.COLOR_BGR2RGB), caption="Detected face ROI used to build the appearance model", use_container_width=True)
        with b:
            st.image(cv2.cvtColor(d["track_view"], cv2.COLOR_BGR2RGB), caption="Mean Shift on translated frame: orange = initial window, green = updated window, red = weighted centroid", use_container_width=True)
        st.write("Actual HSV values from the first 4 × 6 pixels of the selected face crop (H, S, V):")
        st.dataframe(d["hsv_sample"].reshape(-1, 3), hide_index=True, use_container_width=True)
        st.bar_chart(d["hist"].reshape(-1), height=180)
        st.caption("32-bin hue histogram calculated from the selected face ROI using the same mask and normalisation settings as the application.")
        cx, cy = d["centroid"]
        x, y, w, h = d["box"]
        st.latex(r"c_x=\frac{\sum_{x,y}B(x,y)x}{\sum_{x,y}B(x,y)},\quad c_y=\frac{\sum_{x,y}B(x,y)y}{\sum_{x,y}B(x,y)}")
        st.code(f"Initial window = {d['box']}\nBack-projection weighted centroid = ({cx:.2f}, {cy:.2f})\nOpenCV Mean Shift output window = {d['moved_box']}", language="text")
    elif stage == "association":
        st.image(cv2.cvtColor(d["association_view"], cv2.COLOR_BGR2RGB), caption="Orange = Mean Shift predicted window; green = detection box in the translated frame", use_container_width=True)
        A, B = d["moved_box"], d["detected_next"]
        ax, ay, aw, ah = A; bx, by, bw, bh = B
        ix1, iy1 = max(ax,bx), max(ay,by)
        ix2, iy2 = min(ax+aw,bx+bw), min(ay+ah,by+bh)
        inter = max(0,ix2-ix1)*max(0,iy2-iy1)
        union = aw*ah+bw*bh-inter
        st.latex(r"IoU(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}")
        st.code(f"Predicted A = {A}\nDetection B = {B}\nIntersection area = {inter}\nUnion area = {union}\nIoU = {inter}/{union} = {d['iou']:.4f}\nMatch accepted? {'Yes' if d['iou'] >= 0.12 else 'No'} (threshold = 0.12)", language="text")


PYTHON_EQUIVALENT = r'''
#!/usr/bin/env python3
"""
FaceTrack: standalone Python/OpenCV implementation.

This script implements the same computer-vision pipeline used by the
Streamlit application, without the Streamlit interface:

    Haar Cascade detection
    HSV hue-histogram appearance model
    Histogram back-projection
    Mean Shift window update
    IoU-based detection-to-track association
    Track ID management and annotated MP4 export

Usage:
    python facetrack_python.py input_video.mp4
    python facetrack_python.py input_video.mp4 --output result.mp4
"""

import argparse
import os
from pathlib import Path

import cv2
import numpy as np


# Keep these parameters aligned with the Streamlit application.
DETECTION_INTERVAL = 8
IOU_THRESHOLD = 0.12
MAX_MISSED_FRAMES = 16
MAX_TRACKING_DISPLACEMENT = 90
MAX_MEAN_SHIFT_ITERATIONS = 10
MEAN_SHIFT_EPSILON = 1
MAX_FRAMES = 500


def load_face_detector():
    """Load OpenCV's frontal-face Haar Cascade classifier."""
    cascade_file = (
        Path(cv2.data.haarcascades)
        / "haarcascade_frontalface_default.xml"
    )
    cascade = cv2.CascadeClassifier(str(cascade_file))

    if cascade.empty():
        raise RuntimeError(
            "Could not load haarcascade_frontalface_default.xml. "
            "Check the OpenCV installation."
        )

    return cascade


def detect_faces(frame, cascade):
    """Detect face bounding boxes in one BGR frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    boxes = cascade.detectMultiScale(
        gray,
        scaleFactor=1.12,
        minNeighbors=5,
        minSize=(28, 28),
    )

    return [tuple(map(int, box)) for box in boxes]


def calculate_histogram(frame, box):
    """Calculate the masked, normalised 32-bin hue histogram."""
    x, y, width, height = box
    roi = frame[y:y + height, x:x + width]

    if roi.size == 0:
        return None

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array((0, 25, 25), dtype=np.uint8),
        np.array((180, 255, 255), dtype=np.uint8),
    )

    if cv2.countNonZero(mask) == 0:
        mask = None

    hist = cv2.calcHist([hsv], [0], mask, [32], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

    return hist


def calculate_iou(box_a, box_b):
    """Calculate Intersection over Union for two (x, y, w, h) boxes."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - intersection

    return intersection / union if union else 0.0


def create_track(frame, box, track_id):
    """Create a new track and initialise its appearance model."""
    hist = calculate_histogram(frame, box)

    if hist is None:
        return None

    return {
        "id": track_id,
        "box": box,
        "hist": hist,
        "missed": 0,
        "trail": [],
    }


def process_video(input_path, output_path, max_frames=MAX_FRAMES):
    """
    Process a video and write the annotated result.

    Detection runs on frame 1 and every eighth frame. Mean Shift updates
    active tracks between detection passes. IoU associates periodic
    detections with the current track set.
    """
    cascade = load_face_detector()
    capture = cv2.VideoCapture(str(input_path))

    if not capture.isOpened():
        raise RuntimeError(
            "The input video could not be opened. "
            "Use a valid MP4, MOV, AVI or M4V file."
        )

    fps = capture.get(cv2.CAP_PROP_FPS)
    if not np.isfinite(fps) or fps <= 0:
        fps = 25.0

    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width < 1 or height < 1:
        capture.release()
        raise RuntimeError("The input video has invalid dimensions.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        capture.release()
        raise RuntimeError("Could not create the output MP4 video.")

    tracks = {}
    next_track_id = 1
    frame_index = 0
    total_detections = 0

    try:
        while frame_index < max_frames:
            success, frame = capture.read()

            if not success:
                break

            frame_index += 1
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 1. Predict each active track using histogram back-projection
            #    and Mean Shift.
            for track in list(tracks.values()):
                x, y, box_width, box_height = track["box"]

                x = max(0, min(x, width - 1))
                y = max(0, min(y, height - 1))
                box_width = max(1, min(box_width, width - x))
                box_height = max(1, min(box_height, height - y))

                search_window = (x, y, box_width, box_height)

                back_projection = cv2.calcBackProject(
                    [hsv_frame],
                    [0],
                    track["hist"],
                    [0, 180],
                    1,
                )

                termination = (
                    cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                    MAX_MEAN_SHIFT_ITERATIONS,
                    MEAN_SHIFT_EPSILON,
                )

                _, updated_window = cv2.meanShift(
                    back_projection,
                    search_window,
                    termination,
                )

                new_x, new_y, new_width, new_height = map(
                    int, updated_window
                )

                displacement = abs(new_x - x) + abs(new_y - y)

                if displacement < MAX_TRACKING_DISPLACEMENT:
                    track["box"] = (
                        new_x,
                        new_y,
                        new_width,
                        new_height,
                    )
                    track["missed"] = 0
                else:
                    track["missed"] += 1

            # 2. Periodically detect faces and associate detections with tracks.
            if frame_index == 1 or frame_index % DETECTION_INTERVAL == 0:
                detections = detect_faces(frame, cascade)
                total_detections += len(detections)

                candidate_pairs = sorted(
                    (
                        (calculate_iou(track["box"], detection), track_id, det_id)
                        for track_id, track in tracks.items()
                        for det_id, detection in enumerate(detections)
                    ),
                    reverse=True,
                )

                used_tracks = set()
                used_detections = set()

                for score, track_id, detection_id in candidate_pairs:
                    if score < IOU_THRESHOLD:
                        continue
                    if track_id in used_tracks or detection_id in used_detections:
                        continue

                    detection_box = detections[detection_id]
                    new_histogram = calculate_histogram(frame, detection_box)

                    if new_histogram is not None:
                        tracks[track_id]["box"] = detection_box
                        tracks[track_id]["hist"] = new_histogram
                        tracks[track_id]["missed"] = 0
                        used_tracks.add(track_id)
                        used_detections.add(detection_id)

                # 3. Every unmatched detection starts a new track.
                for detection_id, detection_box in enumerate(detections):
                    if detection_id in used_detections:
                        continue

                    track = create_track(
                        frame,
                        detection_box,
                        next_track_id,
                    )

                    if track is not None:
                        tracks[next_track_id] = track
                        next_track_id += 1

            # 4. Remove tracks that have been missed for too long.
            tracks = {
                track_id: track
                for track_id, track in tracks.items()
                if track["missed"] <= MAX_MISSED_FRAMES
            }

            # 5. Draw boxes, IDs and recent centre-position trails.
            rendered = frame.copy()

            for track_id, track in tracks.items():
                if track["missed"]:
                    continue

                x, y, box_width, box_height = track["box"]
                color = (
                    (53 * track_id + 75) % 150 + 70,
                    (89 * track_id + 55) % 150 + 70,
                    (37 * track_id + 110) % 150 + 70,
                )

                cv2.rectangle(
                    rendered,
                    (x, y),
                    (x + box_width, y + box_height),
                    color,
                    2,
                    cv2.LINE_AA,
                )

                label_y = max(20, y - 7)
                cv2.rectangle(
                    rendered,
                    (x, label_y - 23),
                    (x + 98, label_y + 2),
                    color,
                    -1,
                )
                cv2.putText(
                    rendered,
                    f"FACE ID {track_id}",
                    (x + 5, label_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (9, 18, 27),
                    1,
                    cv2.LINE_AA,
                )

                centre = (
                    x + box_width // 2,
                    y + box_height // 2,
                )
                track["trail"].append(centre)
                track["trail"] = track["trail"][-16:]

                for point_a, point_b in zip(
                    track["trail"][:-1],
                    track["trail"][1:],
                ):
                    cv2.line(
                        rendered,
                        point_a,
                        point_b,
                        (104, 230, 210),
                        2,
                        cv2.LINE_AA,
                    )

            writer.write(rendered)

            if frame_index % 25 == 0 or frame_index == 1:
                active_tracks = sum(
                    track["missed"] == 0
                    for track in tracks.values()
                )
                print(
                    f"Frame {frame_index}/{min(total_frames, max_frames) or '?'}"
                    f" | active tracks: {active_tracks}"
                )

    finally:
        capture.release()
        writer.release()

    if frame_index == 0:
        if output_path.exists():
            output_path.unlink()
        raise RuntimeError("No readable frames were found in the input video.")

    return {
        "frames": frame_index,
        "tracks": next_track_id - 1,
        "detections": total_detections,
        "width": width,
        "height": height,
        "fps": fps,
        "output": str(output_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect and track faces in a video using Haar Cascade and Mean Shift."
    )
    parser.add_argument("input_video", type=Path, help="Path to the input video.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("facetrack_output.mp4"),
        help="Path for the annotated MP4 output.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=MAX_FRAMES,
        help=f"Maximum number of frames to process (default: {MAX_FRAMES}).",
    )
    args = parser.parse_args()

    if not args.input_video.is_file():
        parser.error(f"Input video does not exist: {args.input_video}")
    if args.max_frames < 1:
        parser.error("--max-frames must be at least 1")

    stats = process_video(
        args.input_video,
        args.output,
        max_frames=args.max_frames,
    )

    print("\nFaceTrack processing completed.")
    print(f"Frames processed : {stats['frames']}")
    print(f"Track IDs created: {stats['tracks']}")
    print(f"Face detections  : {stats['detections']}")
    print(f"Resolution       : {stats['width']} × {stats['height']}")
    print(f"Frame rate       : {stats['fps']:.2f} FPS")
    print(f"Output video     : {stats['output']}")


if __name__ == "__main__":
    main()

'''


left, right = st.columns([1.05, 4.0], gap="large")

with left:
    nav_a, nav_b = st.columns(2)
    with nav_a:
        if st.button("⌂ Home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()
    with nav_b:
        if st.button("{ } Code", use_container_width=True):
            st.session_state.page = "Code"
            st.rerun()
    st.markdown("""
    <div class="doc-nav">
      <div class="nav-title">PROJECT REPORT</div>
      <a href="#project-guidance">Project Guidance</a>
      <a href="#introduction">1. Introduction</a>
      <a href="#demonstration">2. Project Demonstration</a>
      <a href="#pipeline">3. Pipeline Architecture</a>
      <a class="sub" href="#detection">3.1 Haar Cascade Detection</a>
      <a class="sub" href="#tracking">3.2 Histogram & Mean Shift</a>
      <a class="sub" href="#association">3.3 IoU Track Association</a>
      <a href="#mathematics">4. Mathematical Formulation</a>
      <a class="sub" href="#video-frame">4.1 Frame Representation</a>
      <a class="sub" href="#histogram-math">4.2 HSV Histogram</a>
      <a class="sub" href="#backprojection">4.3 Back-projection</a>
      <a class="sub" href="#meanshift-math">4.4 Mean Shift Update</a>
      <a class="sub" href="#iou-math">4.5 Intersection over Union</a>
      <a href="#implementation">5. Implementation Details</a>
      <a href="#results">6. Results & Limitations</a>
      <a href="#deployment">7. Deployment</a>
      <a href="#run-model">8. Run FaceTrack</a>
      <a href="#source-code">Source Code</a>
    </div>
    """, unsafe_allow_html=True)

with right:
    report_col, team_col = st.columns([4.1, 1.2], gap="large")

    with team_col:
        st.markdown("""
        <aside class="team-card">
          <div class="team-kicker">FACETRACK PROJECT</div>
          <div class="team-heading">Project Team</div>
          <div class="team-member"><span class="team-index">01</span><span class="team-name">Pranav Kumar Singh</span></div>
          <div class="team-member"><span class="team-index">02</span><span class="team-name">Samanta Suman</span></div>
          <div class="team-member"><span class="team-index">03</span><span class="team-name">Rupak Raj</span></div>
          <div class="team-guidance">
            <div class="team-guidance-label">PROJECT GUIDANCE</div>
            <div class="team-guidance-title">Done under the guidance of</div>
            <div class="team-guidance-title">Prof. Prithwijit Guha</div>
            <div class="team-guidance-place">IIT Guwahati</div>
          </div>
        </aside>
        """, unsafe_allow_html=True)

    with report_col:
        st.markdown('<div class="article">', unsafe_allow_html=True)
        if st.session_state.page == "Code":
            st.markdown('<h1 id="source-code">FaceTrack — Equivalent Python Implementation</h1>', unsafe_allow_html=True)
            st.markdown("""
            <p>This is the standalone Python/OpenCV equivalent of the FaceTrack computer-vision pipeline used in this website. It contains the actual processing logic for Haar Cascade face detection, HSV histogram modelling, histogram back-projection, Mean Shift tracking, IoU association, track-ID management and annotated video export.</p>
            <p class="note">This listing intentionally contains no Streamlit interface code. It is the equivalent Python implementation of the underlying detection and tracking pipeline.</p>
            """, unsafe_allow_html=True)
            st.caption(f"Standalone Python/OpenCV implementation · {len(PYTHON_EQUIVALENT.splitlines()):,} lines")
            st.code(PYTHON_EQUIVALENT, language="python", line_numbers=True, wrap_lines=True)
        else:
            st.markdown("""
            <h1>Face Detection and Multi-Object Tracking in Video Using Haar Cascade and Mean Shift</h1>
            <p class="author">A classical computer-vision implementation using Python, OpenCV, NumPy and Streamlit</p>

            <h2 id="project-guidance">Project Guidance</h2>
            <p>This project develops a complete face-detection and face-tracking pipeline for video. Its objective is not merely to locate faces independently in individual images, but to follow detected face regions over time and maintain a consistent track identity while the subjects move through the scene.</p>
            <p>The system uses a hybrid classical-vision strategy. Haar Cascade provides periodic face detections. For every accepted detection, the application extracts a hue histogram from the face region in HSV colour space. The histogram is used to calculate a back-projection on subsequent frames, and the Mean Shift algorithm iteratively moves the tracking window toward the region with the strongest matching colour distribution.</p>
            <p>Detection and tracking are complementary operations. Detection corrects accumulated tracking drift and can introduce a new face into the system. Mean Shift provides intermediate frame-to-frame localisation without running the detector on every frame. Intersection over Union (IoU) compares a tracked region with a newly detected region so that an existing identity can be updated instead of creating a duplicate track.</p>
            <p>The implementation maintains, for each track, a unique integer ID, a bounding box, a colour histogram, a missed-frame counter and a short centre-position history. The history is rendered as a movement trail. A track is removed after it has remained unmatched for more than 16 frames. The current implementation processes at most 500 frames from an uploaded video.</p>
            <p class="note">Scope: this is a classical tracking pipeline. It does not use a deep neural-network face detector, facial embeddings, or a learned re-identification model. Consequently, track identity is based on spatial overlap and colour similarity, not biometric identity recognition.</p>

            <div class="rule"></div>
            <h2 id="introduction">1. Introduction</h2>
            <p>A video is a time-ordered sequence of images. A face may appear at different positions and scales in consecutive frames because of subject motion, camera motion, changes in pose, or changes in distance from the camera. If a detector is applied independently to every frame, it returns face locations but does not inherently indicate which detection in the current frame corresponds to a face observed earlier.</p>
            <p>Tracking addresses this temporal association problem. Let the video be represented by frames <em>I</em><sub>1</sub>, <em>I</em><sub>2</sub>, ..., <em>I</em><sub>T</sub>. At each time step, the system must estimate the location of every active face and preserve its track label. A track can therefore be viewed as a sequence of bounding boxes associated with one persistent ID:</p>
            """, unsafe_allow_html=True)
            st.latex(r"\mathcal{T}_k=\{(t,\mathbf{b}_{t,k})\mid t\in\mathcal{F}_k\}")
            st.markdown("""
            <p>Here, <em>k</em> is the track ID, <em>t</em> is the frame index, and <strong>b</strong><sub>t,k</sub> = (x, y, w, h) is the face bounding box assigned to that track. The set F<sub>k</sub> contains the frames in which the track is considered active.</p>
            <p>The pipeline in this project has three main responsibilities:</p>
            <ol>
              <li><strong>Initialisation:</strong> detect faces in the first frame, create a bounding box for each face, compute its appearance histogram, and assign a new ID.</li>
              <li><strong>Temporal localisation:</strong> use histogram back-projection and Mean Shift to move each existing window in the next frame.</li>
              <li><strong>Correction and identity association:</strong> periodically run face detection again, match the new detections to existing windows using IoU, refresh matched tracks, and initialise unmatched detections as new tracks.</li>
            </ol>
            <p>Finally, the application draws each active bounding box, writes its face ID near the box, stores the centre point in a short trajectory history, and exports the annotated frames as an MP4 video.</p>

            <div class="rule"></div>
            <h2 id="demonstration">2. Project Demonstration</h2>
            <p>The demonstration section accepts a video file in MP4, MOV, AVI or M4V format. After upload, the original video is previewed. When processing is started, the application reads the video sequentially, displays periodic annotated previews and reports the current frame, active-track count and processing stage. At completion, it presents the processed video and a download control.</p>
            <p>The output annotation contains a coloured rectangular bounding box, a label of the form <code>FACE ID k</code>, and a polyline joining recent centre positions. These annotations are visual summaries of the tracker state; they do not change the underlying detection or association calculations.</p>

            <div class="rule"></div>
            <h2 id="pipeline">3. Pipeline Architecture</h2>
            <p>The following diagram shows the full data flow implemented by the application. The upper path is the per-frame tracking path. The periodic detection path enters at frame 1 and then every eighth frame, and its detections are associated with the current track set.</p>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="diagram-wrap">
            <svg viewBox="0 0 1120 650" width="100%" role="img" aria-label="FaceTrack processing architecture">
              <defs>
                <marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#547786"/></marker>
                <style>
                  .box{fill:#f5f9fa;stroke:#547786;stroke-width:1.8;rx:10}
                  .det{fill:#f1f6f2;stroke:#6b927c;stroke-width:1.8;rx:10}
                  .out{fill:#f8f5ee;stroke:#aa8b58;stroke-width:1.8;rx:10}
                  .ttl{font: bold 16px Arial; fill:#29465b}
                  .txt{font: 13px Arial; fill:#405765}
                  .arr{stroke:#547786;stroke-width:2;fill:none;marker-end:url(#arr)}
                  .dash{stroke:#8a9fa8;stroke-width:1.8;stroke-dasharray:6 5;fill:none;marker-end:url(#arr)}
                </style>
              </defs>
              <rect class="box" x="25" y="35" width="190" height="86"/>
              <text class="ttl" x="120" y="66" text-anchor="middle">Video Input</text>
              <text class="txt" x="120" y="89" text-anchor="middle">OpenCV VideoCapture</text>
              <text class="txt" x="120" y="106" text-anchor="middle">read frame Iₜ</text>

              <rect class="box" x="275" y="35" width="205" height="86"/>
              <text class="ttl" x="377" y="66" text-anchor="middle">Frame Preparation</text>
              <text class="txt" x="377" y="89" text-anchor="middle">BGR → HSV / grayscale</text>
              <text class="txt" x="377" y="106" text-anchor="middle">validate frame dimensions</text>
              <path class="arr" d="M215 78 H275"/>

              <rect class="det" x="540" y="20" width="245" height="116"/>
              <text class="ttl" x="662" y="49" text-anchor="middle">Periodic Face Detection</text>
              <text class="txt" x="662" y="73" text-anchor="middle">Frame 1, then every 8th frame</text>
              <text class="txt" x="662" y="94" text-anchor="middle">grayscale + equalizeHist</text>
              <text class="txt" x="662" y="115" text-anchor="middle">Haar Cascade → boxes</text>
              <path class="arr" d="M480 63 H540"/>

              <rect class="box" x="540" y="205" width="245" height="116"/>
              <text class="ttl" x="662" y="234" text-anchor="middle">Track Prediction</text>
              <text class="txt" x="662" y="258" text-anchor="middle">HSV frame + stored hue histogram</text>
              <text class="txt" x="662" y="279" text-anchor="middle">calcBackProject</text>
              <text class="txt" x="662" y="300" text-anchor="middle">Mean Shift → updated window</text>
              <path class="arr" d="M377 121 V262 H540"/>

              <rect class="det" x="850" y="100" width="240" height="120"/>
              <text class="ttl" x="970" y="130" text-anchor="middle">IoU Association</text>
              <text class="txt" x="970" y="154" text-anchor="middle">compare predicted boxes</text>
              <text class="txt" x="970" y="175" text-anchor="middle">with Haar detections</text>
              <text class="txt" x="970" y="196" text-anchor="middle">greedy one-to-one matching</text>
              <path class="arr" d="M785 78 H815 V160 H850"/>
              <path class="arr" d="M785 262 H815 V190 H850"/>

              <rect class="box" x="850" y="285" width="240" height="105"/>
              <text class="ttl" x="970" y="315" text-anchor="middle">Track State Update</text>
              <text class="txt" x="970" y="339" text-anchor="middle">refresh box and histogram</text>
              <text class="txt" x="970" y="360" text-anchor="middle">new IDs / missed counters</text>
              <text class="txt" x="970" y="379" text-anchor="middle">remove tracks after 16 misses</text>
              <path class="arr" d="M970 220 V285"/>

              <rect class="out" x="540" y="430" width="245" height="112"/>
              <text class="ttl" x="662" y="460" text-anchor="middle">Render Annotations</text>
              <text class="txt" x="662" y="484" text-anchor="middle">bounding box + FACE ID</text>
              <text class="txt" x="662" y="505" text-anchor="middle">append centre to trail</text>
              <text class="txt" x="662" y="526" text-anchor="middle">draw recent trajectory</text>
              <path class="arr" d="M970 390 V485 H785"/>

              <rect class="out" x="275" y="430" width="205" height="112"/>
              <text class="ttl" x="377" y="460" text-anchor="middle">Video Export</text>
              <text class="txt" x="377" y="484" text-anchor="middle">VideoWriter · MP4</text>
              <text class="txt" x="377" y="505" text-anchor="middle">same FPS and resolution</text>
              <text class="txt" x="377" y="526" text-anchor="middle">write rendered frame</text>
              <path class="arr" d="M540 486 H480"/>

              <rect class="out" x="25" y="430" width="190" height="112"/>
              <text class="ttl" x="120" y="460" text-anchor="middle">Application Output</text>
              <text class="txt" x="120" y="484" text-anchor="middle">live preview + statistics</text>
              <text class="txt" x="120" y="505" text-anchor="middle">download tracked video</text>
              <text class="txt" x="120" y="526" text-anchor="middle">temporary files cleaned</text>
              <path class="arr" d="M275 486 H215"/>

              <path class="dash" d="M970 390 V590 H120 V542"/>
              <text class="txt" x="550" y="615" text-anchor="middle">Next frame: repeat prediction → optional detection/association → rendering → export</text>
            </svg>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <h3>Architecture Walk-through Using One Image</h3>
                <p>The bundled example is a fictional, locally stored group photograph. The same frame is passed through the actual OpenCV operations below. The face boxes, pixel values, histogram, back-projection, Mean Shift window and IoU score are computed when the app runs; no image is sent to an external service.</p>
                            <div class="note">The photo is a demonstration input only. It is stored beside this app as <code>facetrack_group_demo.png</code>; keep both files in the same directory when deploying.</div>
                """, unsafe_allow_html=True)
            show_frame_demo("pipeline")
            st.markdown("""
            <h3 id="detection">3.1 Haar Cascade Face Detection — Frame-by-Frame Operation</h3>
            <p>For a selected frame, the detector first converts the BGR image into a single-channel grayscale image. This reduces the input from three colour channels to one intensity channel, which is the representation expected by the Haar Cascade classifier. Histogram equalisation is then applied to improve global contrast before detection.</p>
            """, unsafe_allow_html=True)
            show_frame_demo("detection")
            st.latex(r"I_t^{gray}(x,y)=0.114B_t(x,y)+0.587G_t(x,y)+0.299R_t(x,y)")
            st.markdown("<p class='math-caption'>The standard weighted conversion from BGR intensity values to grayscale intensity.</p>", unsafe_allow_html=True)
            st.latex(r"\widetilde I_t=\operatorname{EqualizeHist}(I_t^{gray})")
            st.markdown("""
            <p>The cascade evaluates image sub-windows at multiple scales. Each stage rejects many non-face windows quickly; windows that pass the cascade are returned as candidate face rectangles. The application uses <code>scaleFactor=1.12</code>, <code>minNeighbors=5</code> and <code>minSize=(28, 28)</code>. The returned detection is represented as:</p>
            """, unsafe_allow_html=True)
            st.latex(r"\mathbf{d}_{t,j}=(x_{t,j},y_{t,j},w_{t,j},h_{t,j})")
            st.markdown("""
            <p>Here, (x, y) is the upper-left corner, w is width and h is height. The set of detections in frame t is D<sub>t</sub> = {d<sub>t,1</sub>, ..., d<sub>t,N</sub>}. The code invokes this detector in frame 1 and whenever the frame index is divisible by 8. Therefore, detection is a periodic correction stage rather than an operation performed on every frame.</p>
            <p>For every accepted detection, the corresponding rectangular image region is extracted. The region is converted to HSV and its hue histogram is calculated. This appearance descriptor initialises a new track or refreshes an already matched track.</p>

            <h3 id="tracking">3.2 HSV Histogram and Mean Shift Tracking — Frame-by-Frame Operation</h3>
            <h4>Step 1: Extract the face region</h4>
            <p>Let the current track window be R<sub>k</sub> = (x, y, w, h). The image crop is I<sub>t</sub>[y:y+h, x:x+w]. Empty crops are rejected. The crop is converted from BGR to HSV because hue provides a compact description of dominant colour, while saturation and value can be used to suppress weakly coloured or very dark pixels.</p>
            <h4>Step 2: Construct the hue histogram</h4>
            <p>The code uses 32 bins over the hue range [0, 180). A pixel contributes only if it satisfies the mask bounds S ≥ 25 and V ≥ 25. If the mask contains no valid pixels, the code falls back to an unmasked histogram.</p>
            """, unsafe_allow_html=True)
            show_frame_demo("tracking")
            st.latex(r"H_k(b)=\sum_{(x,y)\in R_k}M(x,y)\,\mathbb{1}\!\left[\operatorname{bin}(H(x,y))=b\right]")
            st.markdown("""
            <p>In this expression, b ∈ {0, ..., 31}, M(x,y) is the validity mask, and 1[·] is the indicator function. OpenCV normalises this histogram to the range [0, 255] using min-max normalisation. The histogram is stored in the track state and acts as the appearance model for that face.</p>
            <h4>Step 3: Calculate histogram back-projection</h4>
            <p>For the next frame, the whole frame is converted to HSV. Each pixel is assigned a value according to the stored track histogram at that pixel's hue bin. The resulting back-projection image has high values at locations whose hue is well represented in the tracked face model.</p>
            """, unsafe_allow_html=True)
            st.latex(r"B_t(x,y)=H_k\!\left(\operatorname{bin}(H_t(x,y))\right)")
            st.markdown("""
            <p>The back-projection is not itself a face detector. It is a response map that indicates where the current frame resembles the stored colour distribution. The existing bounding box provides the initial search window, restricting the Mean Shift search to a local neighbourhood.</p>
            <h4>Step 4: Move the tracking window using Mean Shift</h4>
            <p>Let W<sub>k</sub> be the current search window and let q<sub>i</sub> be the back-projection response at pixel position x<sub>i</sub>. The response acts as a non-negative weight. The weighted centroid is:</p>
            """, unsafe_allow_html=True)
            st.latex(r"\mathbf{c}_{new}=\frac{\sum_{\mathbf{x}_i\in W_k}q_i\mathbf{x}_i}{\sum_{\mathbf{x}_i\in W_k}q_i}")
            st.markdown("""
            <p>The window is translated toward this centroid. Mean Shift repeats the centroid calculation until convergence or until the iteration limit is reached. In this implementation, OpenCV's termination criteria allow at most 10 iterations and use an epsilon of 1 pixel. The returned window (x', y', w', h') becomes the predicted location for that track in the current frame.</p>
            <p>The application applies an additional displacement gate: the update is accepted only when |x'−x| + |y'−y| &lt; 90. If this condition fails, the track's missed counter is increased rather than accepting a potentially unstable jump. A successful update resets the missed counter to zero.</p>
            <h4>Step 5: Repeat for each active track</h4>
            <p>Every track stores its own histogram and window. Therefore, for each frame, the application independently computes a back-projection and Mean Shift update for every active track. The tracking window is then available for the next detection-association step.</p>

            <h3 id="association">3.3 IoU-Based Track Association — Matching Detections to Existing IDs</h3>
            <p>Mean Shift predicts where an existing face has moved. Periodic Haar detections provide independently detected face regions. The association stage determines which new detection corresponds to which existing track. This is necessary because a detection is only a bounding box; it does not contain a persistent identity.</p>
            <h4>Step 1: Calculate pairwise overlap</h4>
            <p>For an existing track box A and a newly detected box B, the intersection rectangle is obtained from the maximum left/top coordinates and minimum right/bottom coordinates:</p>
            """, unsafe_allow_html=True)
            show_frame_demo("association")
            st.latex(r"x_1=\max(x_A,x_B),\quad y_1=\max(y_A,y_B)")
            st.latex(r"x_2=\min(x_A+w_A,x_B+w_B),\quad y_2=\min(y_A+h_A,y_B+h_B)")
            st.latex(r"A_{\cap B}=\max(0,x_2-x_1)\max(0,y_2-y_1)")
            st.markdown("<p>The union area is the sum of the two box areas minus their intersection area.</p>", unsafe_allow_html=True)
            st.latex(r"\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}")
            st.markdown("""
            <h4>Step 2: Build and sort candidate matches</h4>
            <p>The program computes IoU for every track-detection pair and sorts the pairs in descending order of overlap. It then scans the sorted list. A pair is accepted only if its IoU is at least 0.12 and neither its track nor its detection has already been used. This creates a greedy one-to-one assignment: one detection cannot update two tracks, and one track cannot be assigned two detections in the same association pass.</p>
            <h4>Step 3: Update matched tracks</h4>
            <p>For each accepted pair, the track bounding box is replaced with the detected box, a new hue histogram is calculated from the detected region, and the missed counter is reset. This periodic refresh helps correct tracking drift and adapts the appearance model to moderate changes in the face region.</p>
            <h4>Step 4: Create new tracks for unmatched detections</h4>
            <p>Every detection that was not assigned to an existing track is passed to the track-initialisation function. If a valid histogram can be computed, a new track is created with the next unused integer ID, the detected box, missed = 0 and an empty trail.</p>
            <h4>Step 5: Remove stale tracks</h4>
            <p>After tracking and association, tracks with missed &gt; 16 are removed. This allows a face to be temporarily lost for a short interval without immediately deleting its ID, while preventing stale tracks from remaining indefinitely.</p>

            <div class="rule"></div>
            <h2 id="mathematics">4. Mathematical Formulation</h2>
            <h3 id="video-frame">4.1 Frame Representation and Bounding-Box Coordinates</h3>
            <p>A colour video frame is a three-dimensional discrete array. For height H, width W and three colour channels:</p>
            """, unsafe_allow_html=True)
            st.latex(r"I_t\in\{0,1,\ldots,255\}^{H\times W\times 3}")
            st.markdown("<p>A bounding box is parameterised by its top-left coordinate and its dimensions. Its centre is useful for drawing the movement trail.</p>", unsafe_allow_html=True)
            st.latex(r"\mathbf{b}_t=(x_t,y_t,w_t,h_t),\qquad \mathbf{p}_t=\left(x_t+\frac{w_t}{2},y_t+\frac{h_t}{2}\right)")
            st.markdown('<h3 id="histogram-math">4.2 HSV Histogram</h3>', unsafe_allow_html=True)
            st.latex(r"H_k(b)=\sum_{(x,y)\in R_k}M(x,y)\,\mathbb{1}[\operatorname{bin}(H(x,y))=b]")
            st.latex(r"\widehat H_k(b)=255\,\frac{H_k(b)-\min_jH_k(j)}{\max_jH_k(j)-\min_jH_k(j)}")
            st.markdown('<h3 id="backprojection">4.3 Histogram Back-projection</h3>', unsafe_allow_html=True)
            st.latex(r"B_t(x,y)=\widehat H_k(\operatorname{bin}(H_t(x,y)))")
            st.markdown('<h3 id="meanshift-math">4.4 Mean Shift Window Update</h3>', unsafe_allow_html=True)
            st.latex(r"\mathbf{c}_{k+1}=\frac{\sum_{\mathbf{x}_i\in W_k}B_t(\mathbf{x}_i)\mathbf{x}_i}{\sum_{\mathbf{x}_i\in W_k}B_t(\mathbf{x}_i)}")
            st.latex(r"\|\mathbf{c}_{k+1}-\mathbf{c}_k\|_2<\varepsilon")
            st.markdown('<h3 id="iou-math">4.5 Intersection over Union</h3>', unsafe_allow_html=True)
            st.latex(r"\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}")
            st.markdown("""
            <p class="note">Implementation detail: the code uses OpenCV's <code>meanShift</code> routine with a maximum of 10 iterations and epsilon 1. The IoU association threshold is 0.12. The mathematical expressions describe the operations conceptually; OpenCV performs the corresponding pixel and window computations internally.</p>

            <div class="rule"></div>
            <h2 id="implementation">5. Implementation Details</h2>
            <p>The application is organised into small functions so that detection, appearance modelling, association and video processing remain separate operations:</p>
            <ul>
              <li><strong>get_cascade() / load_cascade():</strong> locate and load OpenCV's frontal-face Haar Cascade XML file. The cached loader avoids repeatedly constructing the classifier.</li>
              <li><strong>detect_faces(frame, cascade):</strong> convert a frame to grayscale, equalise its histogram and return integer bounding boxes from <code>detectMultiScale</code>.</li>
              <li><strong>histogram(frame, box):</strong> crop a candidate face, convert it to HSV, create the saturation/value mask, calculate a 32-bin hue histogram and normalise it.</li>
              <li><strong>make_track(frame, box, track_id):</strong> initialise the state dictionary containing ID, box, histogram, missed counter and trajectory list.</li>
              <li><strong>iou(a, b):</strong> compute the intersection-over-union score used by the association stage.</li>
              <li><strong>process_video(...):</strong> open the input, read frames, predict each active track, run periodic detection, associate detections, remove stale tracks, draw annotations and write each rendered frame.</li>
            </ul>
            <p>The output writer uses the MP4V codec and retains the input video's frame rate and spatial resolution. The preview is refreshed on the first frame and then every fifth frame, while detection is performed on the first frame and every eighth frame. The processing loop is capped at 500 frames to limit execution time in the hosted application.</p>

            <div class="rule"></div>
            <h2 id="results">6. Results, Interpretation and Limitations</h2>
            <p>After successful processing, the application reports the number of processed frames, the number of IDs allocated, the total number of face detections, and the video resolution. The output video contains the visible tracking annotations and can be downloaded for inspection.</p>
            <p>The number of allocated track IDs is not necessarily equal to the number of people in the video. A person who disappears and later reappears may receive a new ID if the old track has expired or if the new detection cannot be associated with the old box. Likewise, two nearby faces may produce ambiguous overlap scores.</p>
            <p>Mean Shift relies on the tracked region's colour distribution. It can drift when the background has similar colours, when illumination changes substantially, or when the face rotates and its visible colour distribution changes. Haar Cascade may miss faces under strong pose changes, occlusion, poor illumination or very small image scale. IoU matching is based on geometric overlap and does not use facial appearance embeddings.</p>
            <p>These limitations are consistent with the project's objective: demonstrate an interpretable classical-computer-vision pipeline with explicit detection, histogram modelling, iterative localisation and geometric association.</p>

            <div class="rule"></div>
            <h2 id="deployment">7. Deployment and Execution</h2>
            <p>Place the application source in a file named <code>app.py</code>. Create and activate a Python virtual environment, install the required packages, and launch Streamlit from the directory containing the file.</p>
            <h3>7.1 Install dependencies</h3>
            """, unsafe_allow_html=True)
            st.code("python3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install --upgrade pip\npip install streamlit opencv-python-headless numpy", language="bash")
            st.markdown("<h3>7.2 Start the application</h3><p>Run the following command from the project directory:</p>", unsafe_allow_html=True)
            st.code("streamlit run app.py", language="bash")
            st.markdown("""
            <div class="rule"></div>
            <h2 id="run-model">8. Run FaceTrack on Your Video</h2>
            <p>Upload a short video to execute the complete pipeline described above. The uploader accepts MP4, MOV, AVI and M4V files. For a responsive first test, use a short clip with clearly visible faces and moderate camera motion.</p>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("""
                <div class="run-panel">
                  <h3 style="margin-top:0">Video processing console</h3>
                  <p>Upload a video to run face detection and tracking. The application will show the live annotated frames, report processing statistics and prepare an MP4 result.</p>
                  <div class="upload-card">
                    <div class="upload-title">Choose your video</div>
                    <div class="upload-description">Drag and drop a video into the area below, or browse your computer. Supported formats: MP4, MOV, AVI and M4V.</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                uploaded = st.file_uploader(
                    "Select a video file",
                    type=["mp4", "mov", "avi", "m4v"],
                    accept_multiple_files=False,
                    key="tracking_input_video",
                    label_visibility="visible",
                    help="Choose one video file. The file is processed by this Streamlit application."
                )
                if uploaded is not None:
                    st.video(uploaded)
                    if st.button("▶  Start FaceTrack processing", type="primary", use_container_width=True):
                        in_path = out_path = None
                        preview, progress, status = st.empty(), st.progress(0, text="Initialising video pipeline…"), st.empty()
                        try:
                            suffix = Path(uploaded.name).suffix or ".mp4"
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                                tmp.write(uploaded.getbuffer())
                                in_path = tmp.name
                            out_path, stats = process_video(in_path, preview, progress, status)
                            st.success("Face detection and tracking completed successfully.")
                            metric_cols = st.columns(4)
                            metric_values = [
                                ("Frames processed", f"{stats['frames']:,}"),
                                ("Track IDs created", str(stats['tracks'])),
                                ("Face detections", f"{stats['detections']:,}"),
                                ("Frame resolution", f"{stats['width']} × {stats['height']}")
                            ]
                            for col, (label, value) in zip(metric_cols, metric_values):
                                with col:
                                    st.metric(label, value)
                            result = Path(out_path).read_bytes()
                            st.video(result)
                            st.download_button("⬇  Download tracked video", result,
                                               file_name="facetrack_output.mp4", mime="video/mp4",
                                               use_container_width=True)
                        except Exception as exc:
                            st.error(f"Video processing failed: {exc}")
                        finally:
                            for temp_path in (in_path, out_path):
                                if temp_path and os.path.exists(temp_path):
                                    try:
                                        os.remove(temp_path)
                                    except OSError:
                                        pass
                else:
                    st.info("No video selected yet. Use the large upload area above to browse for a video or drag and drop one into it.")

        st.markdown('</div>', unsafe_allow_html=True)