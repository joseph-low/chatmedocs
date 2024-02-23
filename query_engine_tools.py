from llama_index import SummaryIndex, VectorStoreIndex, KeywordTableIndex, TreeIndex
from llama_index.tools.query_engine import QueryEngineTool











# for summarization queries
def summary_tool(nodes):
    summary_index = SummaryIndex(nodes, show_progress=True)
    print(f"Indexed {len(summary_index.docstore.docs)} nodes for summary tool")
    summary_query_engine = summary_index.as_query_engine(response_mode='tree_summarize')
    summary_tool = QueryEngineTool.from_defaults(
        query_engine=summary_query_engine,
        description="Useful for summarization questions related to the data source"
    )
    return summary_tool


# for context specific queries (aka semantic search / base / default)
def vector_tool(nodes):
    vector_index = VectorStoreIndex(nodes, show_progress=True)
    print(f"Indexed {len(vector_index.docstore.docs)} nodes for vector tool")

    vector_query_engine = vector_index.as_query_engine()

    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        description="Useful for retrieving specific context related to the data source"
    )
    return vector_tool


# for keyword specific queries
def keyword_tool(nodes):
    keyword_index = KeywordTableIndex(nodes, show_progress=True)
    print(f"Indexed {len(keyword_index.docstore.docs)} nodes for keyword tool")

    keyword_query_engine = keyword_index.as_query_engine()

    keyword_tool = QueryEngineTool.from_defaults(
    query_engine=keyword_query_engine,
    description="Useful for retrieving specific context using keywords related to the data source"
    )
    return keyword_tool


# for hierarchical queries 
def hierarchical_tool(nodes):
    tree_index = TreeIndex(nodes, child_branch_factor=1)
    print(f"Indexed document with {len(tree_index.docstore.docs)} nodes")






