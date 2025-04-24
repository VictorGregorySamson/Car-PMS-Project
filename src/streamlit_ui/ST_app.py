import streamlit as st


class Chatbot:
    def chatbot_ui(self):
        st.title("Car File Uploader")

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

            # Optional: save to disk
            with open(f"uploads/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.info("Saved file to /uploads/")

            # 📂 Slideout-like panel with contents
            with st.expander("📖 View File Contents"):
                if uploaded_file.type == "text/plain":
                    content = uploaded_file.read().decode("utf-8")
                    st.text_area("File Contents", content, height=300)
                else:
                    st.write("Preview not supported for this file type.")
