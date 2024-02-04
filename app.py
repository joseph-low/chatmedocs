import openai
import streamlit as st
from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding

# setup
st.set_page_config(
    page_title="Chat with your docs", 
    page_icon="💬", 
    layout="centered", 
    initial_sidebar_state="auto", 
    menu_items=None
)
st.header("Chat with the gibberjabber docs 🦝")
st.info(body="page info blablah -  [this is a page link](https://www.google.com/)", icon="👹")

openai.api_key = st.secrets["OPENAI_API_KEY"]
llm = OpenAI(model='gpt-3.5-turbo', temperature=0.1)
embed_model = OpenAIEmbedding(embed_batch_size=50)
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

# initialize chat message history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Ahoy there, how can I help on my gibberjabber docs?!"}
    ]

@st.cache_resource(show_spinner=True)
def load_data():
    with st.spinner(text="Loading and indexing the gibberjabber docs - hang tight!"):
        documents = SimpleDirectoryReader(input_dir='./data').load_data()
        index = VectorStoreIndex.from_documents(documents=documents, service_context=service_context)
        return index

index = load_data()

# initialize query engine
if "chat_engine" not in st.session_state.keys():
    st.session_state.chat_engine = index.as_chat_engine(chat_mode='condense_question', streaming=True, verbose=True)

# user input and save to chat history
prompt = st.chat_input("Enter your question..")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

# display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# if last msg not from bot, generate new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner(text="Thinking..."):
            response = st.session_state.chat_engine.chat(message=prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)




