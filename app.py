from flask import Flask, request, jsonify, send_from_directory, render_template
import os, json, uuid, re
from pathlib import Path

# Optional imports
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import docx
except ImportError:
    docx = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    USE_SK = True
except ImportError:
    USE_SK = False

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
RESULTS_PATH = "results.json"

# ---------- HELPER FUNCTIONS ----------

def extract_text(path):
    ext = Path(path).suffix.lower()
    text = ""
    if ext == ".pdf" and PyPDF2:
        try:
            with open(path, "rb") as f:
                pdf = PyPDF2.PdfReader(f)
                text = " ".join([p.extract_text() or "" for p in pdf.pages])
        except Exception:
            pass
    elif ext == ".docx" and docx:
        try:
            d = docx.Document(path)
            text = "\n".join(p.text for p in d.paragraphs)
        except Exception:
            pass
    else:
        try:
            with open(path, "r", errors="ignore") as f:
                text = f.read()
        except Exception:
            pass
    return text

def compute_scores(texts, names, jd, keywords):
    if not texts:
        return []

    tfidf_scores = [0.0] * len(texts)
    if USE_SK:
        try:
            vect = TfidfVectorizer(stop_words="english").fit_transform([jd] + texts)
            sims = cosine_similarity(vect[0:1], vect[1:])[0]
            tfidf_scores = [float(s) for s in sims]
        except Exception:
            pass

    results = []
    for i, name in enumerate(names):
        text = texts[i].lower()

        # --- Experience (0–20 yrs normalized to 0–1) ---
        years = re.findall(r'(\d{1,2})\s*(?:years|yrs|year)', text)
        exp_score = min(20, max([int(y) for y in years], default=0)) / 20.0 if years else 0.0

        # --- Education ---
        if re.search(r'phd|doctorate|ph\.d', text):
            edu_score = 1.0
        elif re.search(r'master|msc|ms', text):
            edu_score = 0.8
        elif re.search(r'bachelor|bsc|ba|b\.tech', text):
            edu_score = 0.6
        else:
            edu_score = 0.4

        # --- Keywords (frequency normalized) ---
        kw_count = sum(text.count(k.lower()) for k in keywords)
        kw_score = min(1.0, kw_count / 10.0)  # 10 hits = 100%

        tfidf_score = tfidf_scores[i] if i < len(tfidf_scores) else 0.0

        # --- Weighted total ---
        total_score = 0.6 * tfidf_score + 0.2 * kw_score + 0.15 * exp_score + 0.05 * edu_score

        results.append({
            "name": name,
            "score": round(total_score * 100, 2),
            "experience": round(exp_score * 100, 2),
            "education": round(edu_score * 100, 2),
            "keywords": round(kw_score * 100, 2),
            "similarity": round(tfidf_score * 100, 2)
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("Project.html") 

@app.route('/uploadResumes.html')
def upload_alias():
    return send_from_directory('templates','uploadResumes.html')

@app.route('/describeJob.html')
def describe_alias():
    return send_from_directory('templates','describeJob.html')

@app.route('/Results.html')
def results_alias():
    return send_from_directory('templates','Results.html')

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/help")
def help_page():
    return render_template("help.html")

@app.route("/signin")
def signin_page():
    return render_template("signin.html") 



# ---------- API ENDPOINTS ----------

@app.route("/api/resume/upload", methods=["POST"])
def upload_api():
    files = request.files.getlist("resumes")
    jd = request.form.get("jd", "")
    keywords = [k.strip() for k in request.form.get("keywords", "").split(",") if k.strip()]
    texts, names = [], []

    for f in files:
        fname = secure_name = f.filename.replace(" ", "_")
        ext = Path(fname).suffix.lower()
        if ext not in [".pdf", ".docx", ".txt"]:
            continue
        save_path = os.path.join(UPLOAD_FOLDER, fname)
        f.save(save_path)
        texts.append(extract_text(save_path))
        names.append(fname)

    results = compute_scores(texts, names, jd, keywords)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f)
    return jsonify({"status": "ok", "results": results})

@app.route("/api/resume/results")
def results_api():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            return jsonify(json.load(f))
    return jsonify([])

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)
