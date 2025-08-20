# app.py - Streamlit UI (fully improved)
import streamlit as st
import os
import json
from dotenv import load_dotenv
from PIL import Image
from src.ingestion.reader import extract_text_from_pdf, extract_text_from_image
from src.routing.classifier import classify_doc
from src.extraction.extractor import extract_fields_for_type
from src.confidence.scorer import overall_confidence, flag_low_confidence
from src.validation.validator import validate_and_fix

load_dotenv()

st.set_page_config(page_title="Universal Document Intelligence Agent", layout="wide")
st.title("📄 Universal Document Intelligence Agent")

# -------------------------------
# 1️⃣ File uploader (single or multiple)
# -------------------------------
uploaded_files = st.file_uploader(
    "Upload PDF or Image files",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("Please upload at least one PDF or image file to start processing.")
else:
    tmp_dir = "temp"
    os.makedirs(tmp_dir, exist_ok=True)

    for uploaded in uploaded_files:
        try:
            file_path = os.path.join(tmp_dir, uploaded.name)
            with open(file_path, "wb") as f:
                f.write(uploaded.read())

            st.markdown(f"### 🖼️ Processing: `{uploaded.name}`")

            # -------------------------------
            # 2️⃣ Show preview for images
            # -------------------------------
            if uploaded.type.startswith("image/"):
                img = Image.open(file_path)
                st.image(img, caption="Uploaded image", use_column_width=True)
            elif uploaded.type == "application/pdf":
                st.info("PDF uploaded — OCR will be performed on all pages.")

            # -------------------------------
            # 3️⃣ OCR -> raw text
            # -------------------------------
            ext = file_path.lower().split('.')[-1]
            if ext == "pdf":
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_image(file_path)

            if not text.strip():
                st.warning("OCR returned empty text. Please upload a clearer image.")
                continue  # Skip to next file

            st.subheader("📜 Extracted text (preview)")
            st.text_area("Raw OCR text", text[:2000], height=200)

            # -------------------------------
            # 4️⃣ Document type detection
            # -------------------------------
            doc_type = classify_doc(text)
            st.subheader("📂 Document type")
            st.success(f"Detected: {doc_type}")

            # -------------------------------
            # 5️⃣ Field extraction
            # -------------------------------
            results = extract_fields_for_type(doc_type, text)
            fixed_results = validate_and_fix(results)

            # -------------------------------
            # 6️⃣ Confidence
            # -------------------------------
            flagged = flag_low_confidence(fixed_results)
            overall = overall_confidence(fixed_results)

            st.subheader("🔍 Extracted fields (value + confidence)")
            for field, info in flagged.items():
                badge = "🔴" if info.get("flag") else "🟢"
                col1, col2 = st.columns([3,1])
                col1.write(f"{badge} **{field}**: {info.get('value')}")
                col2.progress(info.get("confidence"))

            st.metric("Overall confidence", f"{overall*100:.1f}%")

            # -------------------------------
            # 7️⃣ Download JSON
            # -------------------------------
            st.subheader("📥 Download result")
            st.download_button(
                "Download JSON",
                json.dumps(fixed_results, indent=2),
                file_name=f"{uploaded.name}_extracted.json"
            )

        except Exception as e:
            st.error(f"Error processing {uploaded.name}: {e}")

        finally:
            # Cleanup temp file
            try:
                os.remove(file_path)
            except Exception:
                pass
