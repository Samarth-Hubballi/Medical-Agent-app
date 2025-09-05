import os
from PIL import Image as PILImage
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.media import Image as AgnoImage
import streamlit as st
import time

# --- Splash Screen Logic ---#
# # --- Animated Splash Screen Logic ---
# --- Animated Splash Screen Logic ---
splash_container = st.empty()

with splash_container.container():
    st.markdown("""
        <style>
        .splash-title {
            font-size: 2.0rem;
            color: #4e73df;
            text-align: center;
            animation: colorchange 2s infinite alternate;
        }
        .logo {
                 width: 80px; height: 80px; margin-bottom: 0; margin-right: 16px;
             border-radius: 50%; background: #fff; display: flex;
             justify-content: center;
             align-items: center;
             font-size: 15px; color: black; font-weight: bold;
             box-shadow: 0 4px 24px rgba(0,0,0,0.15);
             animation: blink 1s infinite;
             /* margin-bottom removed for horizontal alignment */
        }
            .logo-title-row {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: center;
                margin-bottom: 25px;
            }
        @keyframes colorchange {
            0% { color: #4e73df; }
            50% { color: #1f77b4; }
            100% { color: #2ecc71; }
            }
            @keyframes blink {
                0% { opacity: 1; }
                50% { opacity: 0.1; }
                100% { opacity: 1; }
        }
        .splash-info {
            font-size: 1.2rem;
            color: #2ecc71;
            text-align: center;
            animation: blink 1s infinite;
            
        }
        .emoji-vertical {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 2.5rem;
            margin-top: 1rem;
        }
        </style>
        <div class="logo-title-row">
            <div class="logo">Sam AI</div>
            <div class="splash-title">...Loading Medical Image Analysis Tool...</div>
        </div>
        <div class="splash-info">Please wait a moment while the app prepares.<br> Developed by Sam</div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    medical_emojis = ["👩‍⚕️","👩‍⚕️"]
    emoji_display = ""
    steps = len(medical_emojis)
    for i in range(steps):
        progress = int((i+1)/steps*100)
        progress_bar.progress(progress)
        emoji_display += f"<div>{medical_emojis[i]}</div>"
        st.markdown(f"<div class='emoji-vertical'>{emoji_display}</div>", unsafe_allow_html=True)
        time.sleep(0.50)
    st.success("Ready!")
    time.sleep(1)

splash_container.empty()
# --- End of Animated Splash Screen Logic ---

# Set your API Key (Replace with your actual key)
GOOGLE_API_KEY = "AIzaSyBEs3cc0bJKjNRHTlKL8dwXRTRc79yMwyI"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Ensure API Key is provided
if not GOOGLE_API_KEY:
    raise ValueError("⚠️ Please set your Google API Key in GOOGLE_API_KEY")

# Initialize the Medical Agent
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGoTools()],
    markdown=True
)

# Medical Analysis Query
query = """
    '<span style="color: blue;">Your output text here</span>',
    unsafe_allow_html=True
)
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the medical image and structure your response as follows:

### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.).
- Specify anatomical region and positioning.
- Evaluate image quality and technical adequacy.

### 2. Key Findings
- Highlight primary observations systematically.
- Identify potential abnormalities with detailed descriptions.
- Include measurements and densities where relevant.

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level.
- List differential diagnoses ranked by likelihood.
- Support each diagnosis with observed evidence.
- Highlight critical/urgent findings.

### 4. Patient-Friendly Explanation
- Simplify findings in clear, non-technical language.
- Avoid medical jargon or provide easy definitions.
- Include relatable visual analogies.

### 5. Research Context
- Use DuckDuckGo search to find recent medical literature.
- Search for standard treatment protocols.
- Provide 2-3 key references supporting the analysis.

Ensure a structured and medically accurate response using clear markdown formatting.
"""

# Function to analyze medical image
def analyze_medical_image(image_path):
    """Processes and analyzes a medical image using AI."""
    
    # Open and resize image
    image = PILImage.open(image_path) 
    width, height = image.size
    aspect_ratio = width / height
    new_width = 500
    new_height = int(new_width / aspect_ratio)
    resized_image = image.resize((new_width, new_height))

    # Save resized image
    temp_path = "temp_resized_image.png"
    resized_image.save(temp_path)

    # Create AgnoImage object
    agno_image = AgnoImage(filepath=temp_path)

    # Run AI analysis
    try:
        response = medical_agent.run(query, images=[agno_image])
        return response.content
    except Exception as e:
        return f"⚠️ Analysis error: {e}"
    finally:
        # Clean up temporary file
        os.remove(temp_path)

# Streamlit UI setup
st.markdown(
    '<h1 style="color: #1f77b4;">Medical Image Analysis</h1>',
    unsafe_allow_html=True
)
st.markdown(
'<h2 style="color:white">🩺 Medical Image Analysis Tool 🔬</h2>',
    unsafe_allow_html=True
)
st.markdown(
    """
    '<span style="color: white; font-size:18px;">
    Welcome to the **Medical Image Analysis** tool! 📸
    Upload a medical image (X-ray, MRI, CT, Ultrasound,ecg,etc.), and our AI-powered system will analyze it, providing detailed findings, diagnosis, and research insights.
    Let's get started!
    </span>'
    """,
   unsafe_allow_html=True   
)

# Upload image section
st.sidebar.header("Upload Your Medical Image:")
uploaded_file = st.sidebar.file_uploader("Choose a medical image file", type=["jpg", "jpeg", "png", "bmp", "gif"])

# Button to trigger analysis
if uploaded_file is not None:
    # Display the uploaded image in Streamlit
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    if st.sidebar.button("Analyze Image"):
        with st.spinner("🔍 Analyzing the image... Please wait."):
            # Save the uploaded image to a temporary file
            image_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Run analysis on the uploaded image
            report = analyze_medical_image(image_path)
            
            # Display the report
            st.subheader("📋 Analysis Report")
            st.markdown(report, unsafe_allow_html=True)
            
            # Clean up the saved image file
            os.remove(image_path)
else:
    st.warning("⚠️ Please upload a medical image to begin analysis.And this is for educational purposes only and developed by Sam with AI assistance." )
    
    st.warning("⚠️ Ensure the image is clear and of good quality for accurate results. Please note that this tool is for educational purposes and not a substitute for professional medical advice.")
page_bg_img = """
<style>
    .st-emotion-cache-4rsbii{
        background-image: url("https://wallpaperaccess.com/full/6890234.jpg");
        background-size: cover;
        background-position: center;
        background-opacity: 0.01;
    }
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


