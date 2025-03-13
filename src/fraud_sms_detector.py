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

# Load dataset
def read_csv(file_path):
    df = pd.read_csv(file_path, encoding='latin-1', usecols=[0, 1], names=["label", "message"], skiprows=1)
    df["label"] = df["label"].map({"ham": 0, "spam": 1})
    return df["message"].astype(str).tolist(), df["label"].tolist()

# Image to text conversion
def extract_text_from_image(image_path):
    pil_image = Image.open(image_path)
    return pytesseract.image_to_string(pil_image.convert("L")).strip()

# Clean text
clean_text = lambda text: re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

# Train Model
file_path = "../data/spam.csv"
texts, labels = read_csv(file_path)

if texts and labels:
    texts += ["Click here: http://scam.com", "Reminder: Your bill is due"]
    labels += [1, 0]

    vectorizer, classifier = TfidfVectorizer(), LogisticRegression()
    X_train = vectorizer.fit_transform([clean_text(t) for t in texts])
    classifier.fit(X_train, labels)

# Predict Fraud
def is_fraud_sms(text):
    prob = classifier.predict_proba(vectorizer.transform([clean_text(text)]))[0][1]
    return {"result": "Fraud" if prob >= 0.6 else "Not Fraud", "confidence": float(prob)}

# UI Elements
input_type = widgets.RadioButtons(options=["Enter SMS Text", "Upload Image"], description="Input Type:")
sms_text = widgets.Textarea(placeholder="Type SMS here...", layout=widgets.Layout(width="80%", height="100px"))
upload_widget = widgets.FileUpload(accept="image/*", description="Upload Image")
output, process_button = widgets.Output(), widgets.Button(description="Process")

def process_input(_):
    with output:
        clear_output()
        if input_type.value == "Enter SMS Text":
            result = is_fraud_sms(sms_text.value) if sms_text.value.strip() else "Enter a message!"
        else:
            uploaded_file = next(iter(upload_widget.value.values()), None)
            if uploaded_file:
                text = extract_text_from_image(BytesIO(uploaded_file["content"]))
                result = is_fraud_sms(text) if text else "No text detected!"
            else:
                result = "Upload an image!"
        print("Detection Result:", result)

process_button.on_click(process_input)
display(widgets.VBox([input_type, sms_text, upload_widget, process_button, output]))
