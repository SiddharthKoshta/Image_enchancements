# streamlit.io
# pip install streamlit
# pip install rembg

# run application using command: streamlit run app.py

import streamlit as st
from PIL import Image
import os
import requests
from io import BytesIO
from rembg import remove

# Set full screen
st.set_page_config(layout="wide")

st.title("Image Background Removal and Replacement with Standard Image")
st.write("Web App")

# Create directories for saving images
os.makedirs('original', exist_ok=True)
os.makedirs('masked', exist_ok=True)

# Function to load image from URL
def load_image_from_url(url, save_path):
    img = Image.open(BytesIO(requests.get(url).content))
    img.save(save_path, format='jpeg')
    return img

# Function to remove background and merge images
def process_images(subject_path, background_path, threshold):
    output_path = os.path.join('masked', os.path.basename(subject_path))
    with open(subject_path, 'rb') as img_file:
        subject_img = img_file.read()
    subject_no_bg = remove(subject_img, alpha_matting=True, alpha_matting_foreground_threshold=threshold)
    with open(output_path, 'wb') as f:
        f.write(subject_no_bg)
    subject_img = Image.open(output_path)
    background_img = Image.open(background_path).resize(subject_img.size)
    background_img.paste(subject_img, (0, 0), subject_img)
    final_img = background_img.convert("RGB")
    final_img.save('masked/background.jpg', format='jpeg')
    return final_img

use_local_image = st.checkbox("Use Local Image", value=False)
cols = st.columns(2)

subject_img, background_img = None, None

if use_local_image:
    subject_file = cols[0].file_uploader("Choose Subject Image...", type=["jpg", 'png', 'jpeg'], key='subject')
    background_file = cols[1].file_uploader("Choose Background Image...", type=["jpg", 'png', 'jpeg'], key='background')

    if subject_file is not None and background_file is not None:
        subject_name = subject_file.name
        background_name = background_file.name
        
        subject_path = os.path.join('original', subject_name)
        background_path = os.path.join('original', background_name)

        with open(subject_path, "wb") as f:
            f.write(subject_file.getbuffer())
        with open(background_path, "wb") as f:
            f.write(background_file.getbuffer())
        
        subject_img = Image.open(subject_path)
        background_img = Image.open(background_path)
else:
    subject_url = cols[0].text_input("Enter Subject Image URL", "https://cdni.autocarindia.com/ExtraImages/20210107114135_Compass_FL_1%20_1_.jpg")
    background_url = cols[1].text_input("Enter Background URL", "https://pbs.twimg.com/ext_tw_video_thumb/1468243059112566797/pu/img/VzpomvIPC3INi3z0.jpg:large")

    subject_name = subject_url.split('/')[-1]
    background_name = background_url.split('/')[-1]

    subject_path = os.path.join('original', subject_name)
    background_path = os.path.join('original', background_name)

    subject_img = load_image_from_url(subject_url, subject_path)
    background_img = load_image_from_url(background_url, background_path)

if subject_img and background_img:
    cols[0].image(subject_img, caption='Subject Image', use_column_width=True)
    cols[1].image(background_img, caption='Background Image', use_column_width=True)

st.title("Removing Background from Subject Image and Replacing it with Background Image")
threshold = st.slider("Background Threshold", 0, 255, value=50, step=5)

if st.button("Generate"):
    if subject_img and background_img:
        final_img = process_images(subject_path, background_path, threshold)
        st.image(final_img, caption='Merged Image', use_column_width=True)
        with open("masked/background.jpg", "rb") as file:
            btn = st.download_button(
                label="Download Merged Image",
                data=file,
                file_name="merged_image.jpg",
                mime="image/jpeg"
            )
