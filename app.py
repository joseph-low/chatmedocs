import os
import re
import fitz
import openai
import tempfile
import streamlit as st
import streamlit_float as stfloat


from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import PyMuPDFReader


@st.cache_resource(ttl=3600, show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing - hang tight!"):
        documents = PyMuPDFReader().load_data(file_path=temp_file_path)
        index = VectorStoreIndex.from_documents(documents=documents)
        return index


def extract_source_numbers(response_text=str):
    sources = re.findall(r'\[(\d+)\]', response_text)
    raw_source_nums = [int(num) for num in sources] 
    source_nums = [] # deal with repeated numbers
    for number in raw_source_nums:
        if number not in source_nums:
            source_nums.append(number)
    return source_nums


def extract_source_texts(source_numbers=list):
    source_texts = []
    for i in source_numbers:
        try:
            text = response.source_nodes[i-1].text
            l_stripped_text = text.split('\n', 1)[1]
            r_stripped_text = l_stripped_text.rsplit('\n', 1)[0]
            source_texts.append(r_stripped_text)
        except:
            continue
    return source_texts


def citation_snapshot(source_texts=list):
    pdf_document = fitz.open(stream=uploaded_file.getvalue())
    pdf_page_nums = []
    snapshots = []
    for source in source_texts:
        # iterate through each page to find the phrase
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text = page.get_text()
            if source in text:
                pdf_page_nums.append(page_number + 1)
                # highlight the phrase
                text_instance = page.search_for(source)
                page.add_highlight_annot(text_instance)
                image = page.get_pixmap(dpi=120).tobytes()
                snapshots.append(image)
    pdf_document.close()
    return pdf_page_nums, snapshots







# streamlit page config
st.set_page_config(
    page_title="Chat With Your Docs", 
    page_icon=None, 
    layout='wide', 
    menu_items=None
)
st.header("💬 Chat With Your Docs")
with st.sidebar:
    uploaded_file = st.sidebar.file_uploader(
                label="Upload pdf file",
                accept_multiple_files=False,
                type=['pdf'],
                help="Only PDF files are supported"
    )


# env setup
openai.api_key = st.secrets["OPENAI_API_KEY"]


Settings.llm = OpenAI(model='gpt-3.5-turbo', temperature=0.1)
Settings.embed_model = OpenAIEmbedding(embed_batch_size=50)


# create temp file path for uploaded file
if uploaded_file is not None:
    temp_dir = tempfile.TemporaryDirectory()
    temp_file_path = os.path.join(temp_dir.name, uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.read())
    # st.success("File saved to temporary location: {}".format(temp_file_path))


# clear cache on new file upload
if uploaded_file is None:
    st.cache_resource.clear()
    for messages in st.session_state.keys():
        del st.session_state[messages]
    for citations in st.session_state.keys():
        del st.session_state[citations]






col1, col2 = st.columns(spec=2, gap='medium')
stfloat.float_init(theme=True, include_unstable_primary=False)


# Display chat on the left column
with col1:
    with st.container(height=650, border=False):

        if uploaded_file is None:
            st.info(body="Upload a file to begin")

        if uploaded_file is not None:
            index = load_data()

            # initialize chat history
            if 'messages' not in st.session_state.keys():
                st.session_state.messages = [
                    {"role": "assistant", "content": "Ahoy there, how can I help on my gibberjabber docs?!"}
                ]

            # user query and save to chat history
            with st.container():
                query = st.chat_input(placeholder="Ask a document related question")
                # st.chat_input(key='content', on_submit=chat_content) 
                button_css = stfloat.float_css_helper(width='2.2rem', bottom='1rem', transition=0)
                stfloat.float_parent(css=button_css)
                if query:
                    st.session_state.messages.append({'role': 'user', 'content': query})

            # display chat history
            for message in st.session_state.messages:
                with st.chat_message(message['role']):
                    st.write(message['content'])

            # initialize query engine
            if 'query_engine' not in st.session_state.keys():
                st.session_state.query_engine = CitationQueryEngine.from_args(
                    index=index,
                    similarity_top_k=3,
                    citation_chunk_size=512,
                    citation_chunk_overlap=20
                )

            # if last msg not from bot, generate new response
            if st.session_state.messages[-1]['role'] != 'assistant':
                with st.chat_message('assistant'):
                    with st.spinner(text="Thinking..."):
                        response = st.session_state.query_engine.query(query)
                        st.write(response.response)
                        answer = {'role': 'assistant', 'content': response.response}
                        st.session_state.messages.append(answer)
                        print(f"Query: {query}")
                        print(f"Response: {response.response}")

                        # get citations
                        source_nums = extract_source_numbers(response.response)
                        source_texts = extract_source_texts(source_nums)
                        pdf_page_nums, snapshots = citation_snapshot(source_texts)
                        st.session_state.citations.append({'page': pdf_page_nums, 'image': snapshots, 'source_number': source_nums})



# Display PDF source on the right column
with col2:
    with st.container(height=700, border=False):
        if uploaded_file is not None:
            pdf_document = fitz.open(stream=uploaded_file.getvalue())

            # initialize citations history
            if 'citations' not in st.session_state.keys():
                st.session_state.citations = [
                    {'page': [1], 'image': [pdf_document[0].get_pixmap(dpi=120).tobytes()], 'source_number': [0]}
                ]
        
            # Retrieve the latest page number and image
            latest_page_number = st.session_state.citations[-1]['page']
            latest_image = st.session_state.citations[-1]['image']
            latest_source_num = st.session_state.citations[-1]['source_number']

            # Display the latest page number and image
            for i in range(len(latest_page_number)):
                st.image(image=latest_image[i], caption=f"[{latest_source_num[i]}] - Snapshot of Page {latest_page_number[i]}", use_column_width=True)

            pdf_document.close()









