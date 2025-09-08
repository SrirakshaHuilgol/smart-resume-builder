import streamlit as st
import openai
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

# Streamlit Page Config
st.set_page_config(page_title="GenAI Resume Builder", layout="centered")

# Custom background using container
with st.container():
    st.markdown("""
        <style>
            section.main {
                background-color: #eef2f7;
                padding: 20px;
                border-radius: 10px;
            }
        </style>
        """, unsafe_allow_html=True
    )

st.title("🧠 GenAI Resume Builder + OpenAI")
st.markdown("Create a smart, professional resume powered by OpenAI!")

# 🔐 OpenAI Key Input
openai_api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")

# Input Form
with st.form("resume_form"):
    st.subheader("👤 Personal Info")
    name = st.text_input("Full Name", "John Doe")
    designation = st.text_input("Job Title", "Software Developer")
    company = st.text_input("Company", "Tech Solutions")
    email = st.text_input("Email", "john@example.com")
    phone = st.text_input("Phone", "+91 9876543210")
    linkedin = st.text_input("LinkedIn URL", "https://linkedin.com/in/johndoe")
    profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])

    st.subheader("🛠️ Skills")
    skills = st.text_area("Skills (comma-separated)", "Python, Streamlit, AI")

    st.subheader("📁 Projects")
    projects = st.text_area("Projects", "- Resume Builder\n- Chatbot")

    st.subheader("🎓 Education")
    education = st.text_area("Education", "B.Tech in CSE, XYZ University")

    # Button to trigger objective generation
    generate_objective = st.form_submit_button("✨ Generate Objective using GenAI")

    if generate_objective and openai_api_key:
        try:
            openai.api_key = openai_api_key
            with st.spinner("Generating objective..."):
                prompt = f"Write a professional career objective for a {designation} skilled in {skills}."
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=100
                )
                objective = response.choices[0].message.content.strip()
                st.success("✅ Objective generated!")
        except Exception as e:
            st.error(f"OpenAI Error: {e}")
            objective = "To obtain a challenging role in a growth-oriented organization."
    else:
        objective = st.text_area("🎯 Career Objective", "To obtain a challenging position in a reputable organization.")

    final_submit = st.form_submit_button("📄 Generate Resume PDF")

# PDF Generator
def generate_pdf(buffer, profile_image=None):
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y = height - 50
    lh = 20

    if profile_image:
        c.drawImage(ImageReader(profile_image), width - 120, height - 120, 60, 60)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, name)
    y -= lh
    c.setFont("Helvetica", 13)
    c.drawString(50, y, f"{designation} at {company}")
    y -= lh * 2

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Email: {email}")
    y -= lh
    c.drawString(50, y, f"Phone: {phone}")
    y -= lh
    c.drawString(50, y, f"LinkedIn: {linkedin}")
    y -= lh * 2

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "🎯 Objective")
    y -= lh
    c.setFont("Helvetica", 11)
    for line in objective.split('\n'):
        c.drawString(50, y, line)
        y -= lh

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "🛠️ Skills")
    y -= lh
    for skill in skills.split(','):
        c.drawString(50, y, f"- {skill.strip()}")
        y -= lh

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "📁 Projects")
    y -= lh
    for proj in projects.split('\n'):
        c.drawString(50, y, proj)
        y -= lh

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "🎓 Education")
    y -= lh
    for edu in education.split('\n'):
        c.drawString(50, y, edu)
        y -= lh

    c.showPage()
    c.save()

# Handle PDF Generation
if final_submit:
    buffer = BytesIO()
    image_data = None

    if profile_pic:
        image = Image.open(profile_pic)
        image = image.resize((60, 60))
        image_data = BytesIO()
        image.save(image_data, format="PNG")
        image_data.seek(0)

    generate_pdf(buffer, image_data)
    buffer.seek(0)
    st.success("🎉 Resume PDF ready!")
    st.download_button("📥 Download Resume", buffer, "resume.pdf", "application/pdf")
