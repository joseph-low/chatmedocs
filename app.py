import os
import ui
import openai
import fitz
import tempfile
import streamlit as st
import streamlit_float as stfloat


from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import PyMuPDFReader




@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing - hang tight!"):
        # documents = SimpleDirectoryReader(input_files=uploaded_file).load_data()
        documents = PyMuPDFReader().load_data(file_path=temp_file_path)
        index = VectorStoreIndex.from_documents(documents=documents)
        return index




# env setup
openai.api_key = st.secrets["OPENAI_API_KEY"]

Settings.llm = OpenAI(model='gpt-3.5-turbo', temperature=0.1)
Settings.embed_model = OpenAIEmbedding(embed_batch_size=50)




ui.page_config()
uploaded_file = ui.sidebar()


col1, col2 = st.columns(spec=2, gap='medium')
stfloat.float_init(theme=True, include_unstable_primary=False)



# Display PDF on the left column
with col1:

    if uploaded_file is None:
        st.info(body="Upload a file to begin")

    if uploaded_file is not None:
        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory()
        # Save the uploaded file to the temporary directory
        temp_file_path = os.path.join(temp_dir.name, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.read())
        # st.success("File saved to temporary location: {}".format(temp_file_path))
        ui.displayPDF(temp_file_path)


# Display chat inputs / outputs on the right column
with col2:

    if uploaded_file is not None:

        index = load_data()

        # initialize chat message history
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [
                {"role": "assistant", "content": "Ahoy there, how can I help on my gibberjabber docs?!"}
            ]

        # user query and save to chat history
        with st.container():
            query = st.chat_input(placeholder="Ask a document related question")
            # st.chat_input(key='content', on_submit=chat_content) 
            button_css = stfloat.float_css_helper(width="2.2rem", bottom="1rem", transition=0)
            stfloat.float_parent(css=button_css)
            if query:
                st.session_state.messages.append({"role": "user", "content": query})


        # display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])                

        # initialize query engine
        if "chat_engine" not in st.session_state.keys():
            st.session_state.chat_engine = index.as_chat_engine(chat_mode='condense_question', streaming=True, verbose=True)

        # if last msg not from bot, generate new response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner(text="Thinking..."):
                    response = st.session_state.chat_engine.chat(message=query)
                    st.write(response.response)
                    answer = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(answer)








# def chat_content():
#     st.session_state['contents'].append(st.session_state.content)


# with col1:
#     st.info(body="left column")


# with col2:
#     if 'contents' not in st.session_state:
#         st.session_state['contents'] = []

#     with st.container():
#         st.chat_input(key='content', on_submit=chat_content) 
#         button_css = stfloat.float_css_helper(width="2.2rem", bottom="1rem", transition=0)
#         stfloat.float_parent(css=button_css)
#     if content:=st.session_state.content:
#         with st.chat_message(name='Bot'):
#             for c in st.session_state.contents:
#                 st.write(c)


        



        











