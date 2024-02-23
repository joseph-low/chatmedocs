from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter, SemanticSplitterNodeParser















# tries to keep sentences and paragraphs together - best for generic blobs of text
def sentence_splitter_parser(documents):
    sentence_parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=200
    )
    nodes = sentence_parser.get_nodes_from_documents(documents, show_progress=True)
    print(f"Total nodes created: {len(nodes)}\n")

 
# splits into sentences then adds before/after sentences - best for accuracy
# best used with MetadataReplacementNodePostProcessor
def sentence_window_parser(documents):
    sentence_window_parser = SentenceWindowNodeParser.from_defaults(
        window_size=5,
        window_metadata_key='window', 
        original_text_metadata_key='original_text'
    )
    nodes = sentence_window_parser.get_nodes_from_documents(documents, show_progress=True)
    print(f"Total nodes created: {len(nodes)}\n")

 
# chunk contains sentences that are semantically related to each other - best for semantic search?
# more expensive and latency
def semantic_parser(documents):
    semantic_parser = SemanticSplitterNodeParser(
        buffer_size=1,
        embed_model=OpenAIEmbedding()
    )
    nodes = semantic_parser.get_nodes_from_documents(documents, show_progress=True)
    print(f"Total nodes created: {len(nodes)}\n")
