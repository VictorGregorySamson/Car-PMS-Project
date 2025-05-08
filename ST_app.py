import streamlit as st
import os
import PyPDF2
import base64

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from src.core.embedder import manual_vectorstore  # Your vector store instance

class Chatbot:
    def chatbot_ui(self):
        st.title("🚗 Car Manual Chatbot")

        uploaded_file = st.file_uploader(
            "Upload your car manual (PDF only for now)", type=["pdf"]
        )

        manual_id = None
        file_text = ""

        if uploaded_file is not None:
            manual_id = uploaded_file.name.lower().replace(" ", "_")

            # Check if manual already exists
            existing_manuals = manual_vectorstore.get()["metadatas"]
            already_uploaded = any(manual.get("manual_id") == manual_id for manual in existing_manuals)

            if already_uploaded:
                st.warning(f"⚠️ This manual ({uploaded_file.name}) has already been uploaded!")
                st.info("You can ask questions about it below.")

                with st.expander("📖 View Existing Manual"):
                    existing_chunks = manual_vectorstore.get(where={"manual_id": manual_id})
                    for i, chunk in enumerate(existing_chunks["documents"][:3]):
                        st.markdown(f"**Sample Content {i+1}**")
                        st.code(chunk)
            else:
                st.success("File uploaded successfully!")
                st.write("**Filename:**", uploaded_file.name)
                st.write("**File type:**", uploaded_file.type)
                st.write("**File size (bytes):**", uploaded_file.size)

                os.makedirs("uploads", exist_ok=True)
                save_path = os.path.join("uploads", uploaded_file.name)

                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.expander("📖 View Uploaded PDF"):
                    with open(save_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)

                # Extract text
                reader = PyPDF2.PdfReader(save_path)
                for page in reader.pages:
                    file_text += page.extract_text() or ""

                if file_text.strip() == "":
                    st.error("Failed to extract text from the PDF.")
                    return

                # Vectorize and store with manual_id
                splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                chunks = splitter.split_text(file_text)
                documents = [Document(
                    page_content=chunk,
                    metadata={
                        "source": uploaded_file.name,
                        "manual_id": manual_id
                    }
                ) for chunk in chunks]

                manual_vectorstore.add_documents(documents)
                manual_vectorstore.persist()
                st.toast(f"Manual '{uploaded_file.name}' processed successfully!", icon="✅")

        # Only show chat if we have a manual_id (either newly uploaded or existing)
        if manual_id:
            retriever = manual_vectorstore.as_retriever(
                search_kwargs={
                    "k": 4,
                    "filter": {"manual_id": manual_id}
                }
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
                chain_type="stuff",
                retriever=retriever
            )

            st.subheader("💬 Ask a question about your car manual:")
            question = st.text_input("Your question:")

            if question:
                answer = qa_chain.run(question)
                st.success("🤖 Answer:")
                st.write(answer)
