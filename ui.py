import base64
import streamlit as st


def page_config():
    st.set_page_config(
        page_title="Chat With Your Docs", 
        page_icon=None, 
        layout='wide', 
        menu_items=None
    )    
    st.header("💬 Chat With Your Docs")
    # st.info(body="page info blablah -  [this is a page link](https://www.google.com/)", icon="👹")


def sidebar():
    with st.sidebar:
        # st.text_input("Random input here", key="file_qa_api_key", type="password")
        
        uploaded_file = st.file_uploader(
            label="Upload pdf file",
            type=['pdf'],
            help="Only PDF files are supported",
        )
        st.markdown("---")
        st.markdown(
            "# 💡 About\n"
            "Ever had a lengthy document to read?\n\n"
            "This application allows you ask questions on your document and get instant answers\n\n"
            "_*This tool is a work in progress_"
        )
        st.markdown("---")
        st.markdown(
            "# 🔐 Privacy\n"
            "Uploaded data is deleted once you close or refresh the browser tab"
        )
        st.markdown("---")
        st.markdown(
            "# 📭 Feedback\n"
            "Feel free to reach out if you had comments or suggestions\n"
        )
        st.markdown(
            "<a href='mailto:joseph_low_28@hotmail.com'>joseph_low_28@hotmail.com</a>", 
            unsafe_allow_html=True
        )
    return uploaded_file


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)




