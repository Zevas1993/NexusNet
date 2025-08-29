from .retriever import Retriever
class Indexer:
    def __init__(self, retriever: Retriever): self.retriever=retriever
    def add_documents(self, docs): self.retriever.add_documents(docs)
