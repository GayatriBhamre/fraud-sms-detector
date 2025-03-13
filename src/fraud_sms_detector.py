import cv2
import pytesseract
import re
import numpy as np
import pandas as pd
from io import BytesIO
from PIL import Image
import ipywidgets as widgets
from IPython.display import display, clear_output
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def read_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='latin-1', usecols=[0, 1], names=["label", "message"], skiprows=1)
        df["label"] = df["label"].map({"ham": 0, "spam": 1})
        return df["message"].astype(str).tolist(), df["label"].tolist()
    except:
        return [], []

def extract_text_from_image(image_data):
    image = Image.open(BytesIO(image_data) if isinstance(image_data, bytes) else image_data)
    image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
    return pytesseract.image_to_string(image).strip()

clean_text = lambda text: re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

file_path = r"C:\Users\hp\Downloads\archive (1)\spam.csv"
texts, labels = read_csv(file_path)

if texts and labels:
    texts += ["Your account is locked! Click here: http://phishing.com", "Claim your free iPhone now: http://scam.com",
              "URGENT: Call +1234567890 for verification", "Meet me at 5 PM", "Reminder: Your bill is due on 5th March"]
    labels += [1, 1, 1, 0, 0]

    vectorizer, classifier = TfidfVectorizer(), LogisticRegression()
    classifier.fit(vectorizer.fit_transform([clean_text(t) for t in texts]), labels)

def is_fraud_sms(text):
    prob = classifier.predict_proba(vectorizer.transform([clean_text(text)]))[0][1]
    return {"result": "Fraud" if prob >= 0.6 else "Not Fraud", "confidence": float(prob)}

input_type = widgets.RadioButtons(options=["Enter SMS Text", "Upload Screenshot"])
sms_text, upload_widget = widgets.Textarea(placeholder="Type SMS here...", layout=widgets.Layout(width="80%", height="100px")), widgets.FileUpload(accept="image/*")
output, process_button = widgets.Output(), widgets.Button(description="Process")

def process_input(_):
    with output:
        clear_output()
        result = "Enter a message!" if input_type.value == "Enter SMS Text" and not sms_text.value.strip() else None
        if not result:
            if input_type.value == "Enter SMS Text":
                result = is_fraud_sms(sms_text.value)
            else:
                uploaded_file = next(iter(upload_widget.value.values()), None)
                result = "Upload an image!" if not uploaded_file else is_fraud_sms(extract_text_from_image(uploaded_file["content"]))
        print("Detection Result:", result)

process_button.on_click(process_input)
display(widgets.VBox([input_type, sms_text, upload_widget, process_button, output]))
