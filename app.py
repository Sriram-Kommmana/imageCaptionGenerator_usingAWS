import os
import uuid
from io import BytesIO
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

from src import aws_pipeline


st.set_page_config(page_title="AWS Image Caption Generator", layout="centered")
st.title("AWS Image Caption Generator")

uploaded = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    if st.button("Upload & Generate Caption"):
        # Convert image to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Generate unique filename
        filename = f"{uuid.uuid4()}.jpg"

        # 1️⃣ Upload to S3 under 'images/' folder
        image_id = aws_pipeline.upload_to_s3(img_bytes.getvalue(), filename)
        st.success(f"Image uploaded to S3: {image_id}")

        # 2️⃣ Poll DynamoDB for caption
        st.info("Waiting for Lambda to generate caption...")
        caption = aws_pipeline.get_caption_from_dynamodb(image_id)

        if caption:
            st.success(f"Caption: {caption}")
        else:
            st.warning("Caption not available yet. Try again in a few seconds.")
