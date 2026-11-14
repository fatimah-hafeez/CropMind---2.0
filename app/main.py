import streamlit as st

st.set_page_config(page_title="CropMind 2.0", layout="centered")

# Temporary switch for this static screen only. Removed in a later step.
SHOW_SAMPLE_ERROR = False

st.title("CropMind 2.0")
st.write("Preliminary assessment of crop disease for wheat, cotton and sugarcane.")

# Element 1: input mode selector
mode = st.radio("Input mode", ["Image diagnosis", "Text diagnosis"], horizontal=True)

# Element 2: crop selector
crop = st.selectbox("Crop", ["Wheat", "Cotton", "Sugarcane"])

# Elements 3 and 4: input area and supported formats note
if mode == "Image diagnosis":
    st.file_uploader("Photo of the crop or leaf")
    st.caption("Supported formats: JPEG and PNG, up to 10 MB.")
else:
    st.text_area("Describe the symptoms you see", height=150)

# Element 5: submit button
st.button("Submit")

# Element 6: status area (placeholder text for now)
st.subheader("Status")
st.write("Placeholder status message.")

# Element 7: result area (placeholder text for now)
st.subheader("Result")
st.write("Source: placeholder")
st.write(f"Crop: {crop}")
st.write("Outcome: placeholder")
if mode == "Image diagnosis":
    st.write("Confidence: placeholder")
else:
    st.write("Explanation: placeholder")

# Element 8: error message area (appears only when something goes wrong)
if SHOW_SAMPLE_ERROR:
    st.error("Placeholder error message.")

# Element 9: start new assessment button
st.button("Start new assessment")