import os
import uuid
from io import BytesIO
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

from src import aws_pipeline

st.set_page_config(page_title="AWS Image Caption Generator", layout="centered")
st.title("AWS Image Caption Generator")

if "image" not in st.session_state:
    st.session_state.image = None
if "image_id" not in st.session_state:
    st.session_state.image_id = None
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False

def reset_image():
    st.session_state.image = None
    st.session_state.image_id = None
    st.session_state.reset_trigger = not st.session_state.reset_trigger


uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key=st.session_state.reset_trigger)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.session_state.image = img

if st.session_state.image:
    img = st.session_state.image

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Uploaded Image", use_container_width=True)

    with col2:
        if st.button("Generate Caption"):
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            filename = f"{uuid.uuid4()}.jpg"
            st.session_state.image_id = aws_pipeline.upload_to_s3(img_bytes.getvalue(), filename)

            st.success(f"Image uploaded to S3: {st.session_state.image_id}")
            st.info("Waiting for Lambda to generate caption...")

            with st.spinner("Generating caption..."):
                caption = aws_pipeline.get_caption_from_dynamodb(st.session_state.image_id)
                if caption:
                    st.subheader("**Caption:**")
                    st.info(f"{caption}")
                else:
                    st.warning("Caption not available yet. Try again in a few seconds.")
