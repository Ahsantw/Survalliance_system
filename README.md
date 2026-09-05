# Neura Face — CCTV Surveillance System

A face-recognition-based CCTV surveillance system that detects and identifies people from live/recorded video streams (using AdaFace embeddings), logs their entry/exit events to a database, and provides a Streamlit dashboard for monitoring, searching, and managing enrolled people.

## Overview

The system has two main parts:

1. **Recognition engine** (`inference.py`, `net.py`, `video_stream.py`, `face_alignment/`) — reads a video stream, detects and aligns faces (via MTCNN), computes face embeddings with an **AdaFace** model, matches them against a database of enrolled people, and logs entry/exit events (per camera) to a SQLite database with a time-based de-duplication rule (won't re-log the same person within a short window).
2. **Streamlit web app** (`streamlit_app.py` + `pages/`) — a login-gated dashboard ("Neura Face") for:
   - **Dashboard** — view live entry/exit logs (person ID, name, timestamp, camera).
   - **Add Person** — enroll a new person (capture/upload a face, generate an embedding, and add them to the recognition database) and generate an employee ID card.
   - **Remove Person** — remove an enrolled person from the system.
   - **Search Person** — search logged events by Person ID, Name, Date, or Camera ID.

## Architecture

```
                ┌───────────────────────────┐
Video/RTSP  ──► │  inference.py             │
stream          │  - Cv2FileVideoStream     │
                │  - MTCNN face alignment   │
                │  - AdaFace embedding      │
                │  - similarity matching    │
                └────────────┬──────────────┘
                             │ logs entry/exit
                             ▼
                   cctv_database.db (SQLite)
                    ├─ user       (login credentials)
                    ├─ employee   (enrolled people)
                    └─ cctv       (entry/exit event log)
                             ▲
                             │ reads/writes
                ┌────────────┴──────────────┐
                │  streamlit_app.py         │
                │  pages/                   │
                │   1_streamdash.py         │
                │   2_addperson.py          │
                │   3_removeperson.py       │
                │   4_Searching.py          │
                └───────────────────────────┘
```

## Repository Contents

| Path | Description |
|---|---|
| `streamlit_app.py` | App entry point — login page, then routes to the dashboard on success. |
| `navigation.py` | Shared sidebar navigation ("Neura Face" branding, page links, logout). |
| `pages/1_streamdash.py` | Main dashboard — displays entry/exit logs from the `cctv` table, with pagination. |
| `pages/2_addperson.py` | Enroll a new person: capture/upload a face image, compute and store its embedding. |
| `pages/3_removeperson.py` | Remove an enrolled person from the database. |
| `pages/4_Searching.py` | Search logged entry/exit events by Person ID, Name, Date, or Camera ID. |
| `inference.py` | Core recognition pipeline: reads video, aligns faces, extracts AdaFace embeddings, matches against `database.pt`, and logs matches to SQLite. |
| `net.py` | AdaFace/IR-based network architecture definition, used to build and load the pretrained recognition model. |
| `video_stream.py` | Threaded/queued video capture wrapper (`Cv2FileVideoStream`) for reading frames from a file or RTSP stream. |
| `face_alignment/` | MTCNN-based face detection and alignment utilities (adapted from a PyTorch MTCNN implementation), used to crop and align faces before embedding. |
| `database.py` | Database helper utilities. |
| `database.pt` | Serialized tensor of known face embeddings (the enrollment "database" used for matching). |
| `database.txt` | List of enrolled person image filenames/IDs, indexed in the same order as `database.pt`. |
| `cctv_database.db` | SQLite database containing `user` (login), `employee` (enrolled people), and `cctv` (entry/exit log) tables. |
| `cards/`, `images/` | Generated employee ID cards and reference face images. |
| `requirements.txt` | Python dependencies. |

## Requirements

- Python 3.10 (per the original README)
- A CUDA-capable GPU (the recognition pipeline moves the model and inputs to `.cuda()`)
- Packages from `requirements.txt`:
  - `numpy`
  - `opencv-python`
  - `requests`
  - `streamlit`
  - `streamlit-extras`
  - `tabulate`
  - `natsort`
  - `tqdm`
  - `ultralytics`
- Additionally required (used in the code but not listed in `requirements.txt`):
  - `torch` (PyTorch, with CUDA support)
  - `pillow`
  - `pandas`
  - `streamlit-js-eval`
- A pretrained AdaFace checkpoint at `pretrained/adaface_ir50_ms1mv2.ckpt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install torch pandas pillow streamlit-js-eval
   ```
2. Place the pretrained AdaFace model checkpoint at `pretrained/adaface_ir50_ms1mv2.ckpt`.
3. Ensure `cctv_database.db` exists with the expected schema (`user`, `employee`, `cctv` tables). A default login is seeded as `username: admin`, `password: admin`.
4. Enroll people (via the **Add Person** page, or by populating `database.pt` / `database.txt` directly) before running recognition.
5. Update the video source in `inference.py` (currently hardcoded to a local file, `imran.mp4`) to your camera/RTSP stream, e.g.:
   ```python
   vid_stream = Cv2FileVideoStream('rtsp://<user>:<password>@<camera-ip>:554/streaming/channels/101')
   ```

## Usage

**Run the web dashboard:**
```bash
streamlit run streamlit_app.py
```
Log in with the seeded credentials (`admin` / `admin`), then use the sidebar to navigate between **Dashboard**, **Add Person**, **Remove Person**, and **Search Person**.

**Run the recognition/logging engine:**
```bash
python inference.py
```
This starts reading from the configured video stream, detects and matches faces against the enrolled database, and logs entry/exit events (with camera ID) to `cctv_database.db`.

## Notes

- Recognition uses a similarity threshold of `0.4` against the AdaFace embedding database — matches below this are ignored.
- A 10-second de-duplication window prevents the same person from being logged repeatedly by the same camera in quick succession; a different camera will still log a new event.
- Camera IDs are mapped to `"Entry"` (camera 1) or `"Exit"` (any other camera ID) in the log.
- Several paths (video file, database file, model checkpoint) are currently hardcoded and should be adapted to your deployment environment.
- An external API endpoint (`http://127.0.0.1:5000/api/recognize`) is referenced but not used directly in the current `inference.py` flow — this may be a remnant of a planned/alternate architecture.

## License

No license file is currently included in this repository. Contact the repository owner for usage terms. Note that the `face_alignment/mtcnn_pytorch/` subdirectory includes its own bundled `LICENSE`.
