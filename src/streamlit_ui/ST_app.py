import streamlit as st
import os
import PyPDF2
import base64

class Chatbot:
    def chatbot_ui(self):
        st.title("Car File Uploader with Chatbot 🤖")

        uploaded_file = st.file_uploader(
            "Upload your owner's manual or maintenance record",
            type=["pdf", "jpg", "png", "txt"]
        )

        if uploaded_file is not None:
            st.success("File uploaded successfully!")

            # Show file details
            st.write("**Filename:**", uploaded_file.name)
            st.write("**File type:**", uploaded_file.type)
            st.write("**File size (bytes):**", uploaded_file.size)

            # Make sure the uploads directory exists
            os.makedirs("uploads", exist_ok=True)

            # Save the uploaded file
            save_path = f"uploads/{uploaded_file.name}"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.info(f"Saved file to {save_path}")

            file_text = ""

            # 📂 Slideout-like panel with contents
            with st.expander("📖 View File Contents"):
                if uploaded_file.type == "text/plain":
                    file_text = uploaded_file.read().decode("utf-8")
                    st.text_area("File Contents", file_text, height=300)
                elif uploaded_file.type == "application/pdf":
                    # Read and display PDF
                    with open(save_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

                    # Also extract text for chatbot
                    reader = PyPDF2.PdfReader(save_path)
                    for page in reader.pages:
                        file_text += page.extract_text()
                else:
                    st.write("Preview not supported for this file type.")

            # 💬 Chatbot Section
            st.subheader("Ask Questions About Your File")

            if file_text.strip() != "":
                user_question = st.text_input("Enter your question:")

                if user_question:
                    # Very basic QA: check if any sentence matches
                    lower_text = file_text.lower()
                    lower_question = user_question.lower()

                    if lower_question in lower_text:
                        st.success("✅ I found something related in your document!")
                    else:
                        st.error("❌ Sorry, I couldn't find an exact match. Try asking differently!")

                    # (Later you could connect this to a real LLM or better search)
            else:
                st.warning("File text not available for questions yet.")
