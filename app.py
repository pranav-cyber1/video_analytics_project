import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
import streamlit_analytics2 as streamlit_analytics

with streamlit_analytics.track(unsafe_password="12345"):
    st.set_page_config(page_title="FaceTrack", page_icon="◉", layout="wide", initial_sidebar_state="expanded")

    # Replace this URL with your own YouTube project-demo link whenever it is ready.
    WALKTHROUGH_YOUTUBE_URL = "https://www.youtube.com/watch?v=Lif1jCNxze0&list=RDLif1jCNxze0&start_radio=1"

    CSS = """
    <style>
    .block-container {max-width: 1240px; padding-top: 1.35rem; padding-bottom: 3rem;}
    .brand {font-size: 1.3rem; font-weight: 800; margin: .4rem 0 1.2rem;}
    .hero-panel {position:relative; overflow:hidden; padding:2.2rem 2.2rem 1.8rem; border-radius:24px; color:white; background:linear-gradient(125deg,#101d3b 0%,#253d72 52%,#5146a5 100%); margin:.4rem 0 1.5rem; box-shadow:0 14px 36px rgba(35,48,95,.18);}
    .hero-panel:after {content:""; position:absolute; width:260px;height:260px;right:-65px;top:-115px;border-radius:50%;border:1px solid rgba(255,255,255,.25);box-shadow:0 0 0 28px rgba(255,255,255,.05),0 0 0 58px rgba(255,255,255,.035);}
    .hero-kicker {font-size:.76rem; letter-spacing:.16em; text-transform:uppercase; font-weight:800; color:#b9d6ff; margin-bottom:.7rem;}
    .hero-title {font-size:clamp(2.2rem,5vw,3.7rem); line-height:1.04; letter-spacing:-.045em; font-weight:850; margin:0 0 .75rem;}
    .hero-copy {max-width:700px; font-size:1.04rem; color:#e2eaff; line-height:1.7; margin:0;}
    .hero-pills {display:flex;gap:.55rem;flex-wrap:wrap;margin-top:1.25rem;}
    .hero-pill {font-size:.78rem;font-weight:650;border:1px solid rgba(255,255,255,.26);background:rgba(255,255,255,.09);padding:.42rem .72rem;border-radius:999px;color:#f5f8ff;}
    .section-intro {color:#65748b;margin-top:-.45rem;margin-bottom:1.1rem;}
    .workflow {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.75rem;margin:1rem 0 1.8rem;position:relative;}
    .flow-card {position:relative;min-height:145px;padding:1rem .9rem;border:1px solid #e2e8f0;border-radius:17px;background:linear-gradient(160deg,#fff,#f7f9ff);box-shadow:0 5px 18px rgba(29,48,82,.045);transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease;animation:rise-in .55s both, soft-pulse 3.2s ease-in-out infinite;}
    .flow-card:hover {transform:translateY(-5px);box-shadow:0 13px 25px rgba(46,65,110,.12);border-color:#b8c7f6;}
    .flow-card:nth-child(2){animation-delay:.07s, .4s}.flow-card:nth-child(3){animation-delay:.14s, .8s}.flow-card:nth-child(4){animation-delay:.21s, 1.2s}.flow-card:nth-child(5){animation-delay:.28s, 1.6s}
    .flow-num {font-size:.72rem;font-weight:850;letter-spacing:.08em;color:#635bdb;margin-bottom:.55rem;}
    .flow-icon {font-size:1.35rem;margin-bottom:.35rem;}
    .flow-title {font-size:.94rem;font-weight:800;color:#18243b;margin-bottom:.35rem;}
    .flow-copy {font-size:.79rem;line-height:1.5;color:#68758a;}
    @keyframes rise-in {from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
    @keyframes soft-pulse {0%,100%{box-shadow:0 5px 18px rgba(29,48,82,.045)}50%{box-shadow:0 9px 24px rgba(85,98,190,.13)}}
    .flow-card:after {content:"→";position:absolute;right:-.65rem;top:45%;z-index:2;color:#8179e8;font-size:1.15rem;font-weight:800;}
    .flow-card:last-child:after {content:""}
    @media(max-width:850px){.workflow{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-panel{padding:1.5rem}}
    @media(prefers-reduced-motion:reduce){.flow-card{animation:none;transition:none}.flow-card:after{display:none}}
    .math-section {padding: .25rem 0 1rem 0; margin-bottom: .5rem;}
    .math-note {font-size: .95rem; line-height: 1.65;}
    .upload-panel {padding:1.2rem;border:1px dashed #aab8d0;border-radius:18px;background:linear-gradient(135deg,#f8faff,#fff);}
    .metric {padding:1rem 1.1rem;border:1px solid #e4eaf2;border-radius:16px;background:linear-gradient(145deg,#fff,#f7f9fd);box-shadow:0 4px 15px rgba(20,40,75,.045);}
    .metric small {display:block;color:#738198;font-size:.78rem;margin-bottom:.35rem}.metric strong{font-size:1.4rem;color:#18243b}
    </style>
    """
    st.markdown(CSS, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    with st.sidebar:
        st.markdown('<div class="brand">◉ <span>Face</span>Track</div>', unsafe_allow_html=True)
        if st.button("⌂  Home", use_container_width=True):
            st.session_state.page = "Home"
        if st.button("{ }  Code", use_container_width=True):
            st.session_state.page = "Code"
        st.markdown("<div style='position:fixed;bottom:22px;color:#708196;font-size:.75rem'>OpenCV · Classical vision</div>", unsafe_allow_html=True)


    def get_cascade():
        if not hasattr(cv2, "CascadeClassifier"):
            raise RuntimeError("OpenCV loaded without CascadeClassifier. Remove conflicting OpenCV packages, install opencv-python-headless, then reboot the app.")
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        if not cascade_path.is_file():
            raise RuntimeError("The Haar Cascade file is missing. Reinstall opencv-python-headless and reboot the app.")
        cascade = cv2.CascadeClassifier(str(cascade_path))
        if cascade.empty():
            raise RuntimeError("OpenCV could not load the Haar Cascade file.")
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


    if st.session_state.page == "Code":
        st.markdown('<div class="hero"><div class="eyebrow">Under the hood</div><h1>Source code</h1><p>The app detects faces, updates tracking windows, periodically redetects faces, and associates detections with existing track IDs.</p></div>', unsafe_allow_html=True)
        try:
            source = Path(__file__).read_text(encoding="utf-8")
            st.code(source, language="python", line_numbers=True)
            st.download_button("Download app.py", source, file_name="app.py", mime="text/x-python")
        except Exception as exc:
            st.error(f"Could not read the source file: {exc}")
    else:
        st.markdown(
            '<section class="hero-panel"><div class="hero-kicker">Computer vision · Video analytics</div>'
            '<div class="hero-title">FaceTrack<span style="color:#a9c8ff">.</span></div>'
            '<p class="hero-copy">Detect, follow, and maintain identities of multiple faces across video frames with a clean classical-computer-vision pipeline.</p>'
            '<div class="hero-pills"><span class="hero-pill">OpenCV</span><span class="hero-pill">Haar Cascade</span><span class="hero-pill">Mean Shift</span><span class="hero-pill">IoU association</span></div></section>',
            unsafe_allow_html=True,
        )
        st.header("Project workflow")
        st.markdown('<p class="section-intro">From an input video to a downloadable video with face IDs and tracking trails.</p>', unsafe_allow_html=True)
        st.markdown(
            '<div class="workflow">'
            '<div class="flow-card"><div class="flow-num">STEP 01</div><div class="flow-icon">🎞️</div><div class="flow-title">Video input</div><div class="flow-copy">Read the uploaded clip frame by frame.</div></div>'
            '<div class="flow-card"><div class="flow-num">STEP 02</div><div class="flow-icon">▣</div><div class="flow-title">Face detection</div><div class="flow-copy">Haar Cascade finds candidate face regions.</div></div>'
            '<div class="flow-card"><div class="flow-num">STEP 03</div><div class="flow-icon">◎</div><div class="flow-title">Track movement</div><div class="flow-copy">Mean Shift updates each face window.</div></div>'
            '<div class="flow-card"><div class="flow-num">STEP 04</div><div class="flow-icon">⇄</div><div class="flow-title">Match identities</div><div class="flow-copy">IoU associates new detections with tracks.</div></div>'
            '<div class="flow-card"><div class="flow-num">STEP 05</div><div class="flow-icon">✓</div><div class="flow-title">Export result</div><div class="flow-copy">Render face IDs and trails into a video.</div></div>'
            '</div>', unsafe_allow_html=True
        )

        st.header("Mathematical formulation")

        st.subheader("1. Video frame")
        st.latex(r"I_t \in \{0,1,\ldots,255\}^{H\times W\times 3}")
        st.caption(r"$I_t$ denotes the colour image at time $t$, with height $H$ and width $W$.")

        st.subheader("2. Face detection")
        st.latex(r"\mathcal{D}_t = \{\mathbf{b}_{t,i}\}_{i=1}^{N_t}")
        st.latex(r"\mathbf{b}_{t,i} = (x_{t,i},\,y_{t,i},\,w_{t,i},\,h_{t,i})")
        st.caption("The detector returns a set of face bounding boxes for each frame.")

        st.subheader("3. Mean Shift tracking")
        st.latex(r"\mathbf{c}_{k+1}=\frac{\sum_{\mathbf{x}_i\in W_k} w_i\,\mathbf{x}_i}{\sum_{\mathbf{x}_i\in W_k} w_i}")
        st.latex(r"\lVert\mathbf{c}_{k+1}-\mathbf{c}_k\rVert_2 < \varepsilon")
        st.caption("The tracking window moves toward the weighted centre until its movement is below the convergence tolerance $\\varepsilon$.")

        st.subheader("4. Detection-to-track association")
        st.latex(r"\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}")
        st.caption("IoU measures overlap between a tracked bounding box and a newly detected box.")

        st.subheader("5. Track update and output")
        st.latex(r"\mathcal{T}_t=\operatorname{Update}(\mathcal{T}_{t-1},\mathcal{D}_t)")
        st.latex(r"O_t=\operatorname{Draw}(I_t,\mathcal{T}_t)")
        st.caption("The tracker updates existing identities, creates tracks for new detections, and draws the tracked faces on the output frame.")

        st.header("Project Walkthrough")
        with st.container(border=True):
            st.video(WALKTHROUGH_YOUTUBE_URL)

        st.markdown("## Try your own video")
        st.markdown('<p class="section-intro">Upload a clip to detect and track faces, then preview and download the result.</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Drop a video here", type=["mp4", "mov", "avi", "m4v"], label_visibility="collapsed", key="tracking_input_video")
        if uploaded is not None:
            st.video(uploaded)
            if st.button("▶  Detect and track faces", type="primary", use_container_width=True):
                in_path = out_path = None
                preview, progress, status = st.empty(), st.progress(0, text="Starting detection…"), st.empty()
                try:
                    suffix = Path(uploaded.name).suffix or ".mp4"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded.getbuffer()); in_path = tmp.name
                    out_path, stats = process_video(in_path, preview, progress, status)
                    st.success("Tracking complete")
                    cols = st.columns(4)
                    for col, label, value in zip(cols, ["Frames", "Track IDs", "Detections", "Resolution"], [f"{stats['frames']:,}", str(stats['tracks']), f"{stats['detections']:,}", f"{stats['width']} × {stats['height']}"]):
                        with col:
                            st.markdown(f'<div class="metric"><small>{label}</small><strong>{value}</strong></div>', unsafe_allow_html=True)
                    result = Path(out_path).read_bytes()
                    st.video(result)
                    st.download_button("Download tracked video", result, file_name="facetrack_output.mp4", mime="video/mp4", use_container_width=True)
                except Exception as exc:
                    st.error(f"Video processing failed: {exc}")
                finally:
                    for p in (in_path, out_path):
                        if p and os.path.exists(p):
                            try: os.remove(p)
                            except OSError: pass
        st.markdown('<div style="text-align:center;color:#728398;font-size:.78rem;padding-top:2rem">FaceTrack · OpenCV + NumPy</div>', unsafe_allow_html=True)
