import os
import concurrent.futures
import google.generativeai as genai
from langchain_core.runnables import Runnable
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


class ChatGemini(Runnable):
    # Fixed paths for PDFs and vectorstore
    PDF_DIRECTORY = "C:\\Data"
    VECTORSTORE_PATH = "C://Chroma_Storage"

    def __init__(self, model_name: str, credentials_path: str, generation_config: dict):
        # Set up Google credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Initialize the Gemini LLM
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )

        # Initialize vectorstore and retriever
        self.vectorstore = None
        self.retriever = None

        # Load or create the vectorstore
        self._initialize_vectorstore()

    @staticmethod
    def load_and_split_pdf(file_path):
        """Load and split a PDF file into smaller chunks."""
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return text_splitter.split_documents(docs)

    def _initialize_vectorstore(self):
        """Create or load a Chroma vectorstore."""
        docs = []

        if not os.path.exists(self.VECTORSTORE_PATH):
            print("Creating vectorstore...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.load_and_split_pdf, os.path.join(self.PDF_DIRECTORY, filename))
                    for filename in os.listdir(self.PDF_DIRECTORY)
                    if filename.endswith(".pdf")
                ]
                for future in concurrent.futures.as_completed(futures):
                    docs.extend(future.result())

            # Create embeddings and save the vectorstore
            embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", timeout=60)
            self.vectorstore = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=self.VECTORSTORE_PATH)
        else:
            print("Loading existing vectorstore...")
            embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", timeout=60)
            self.vectorstore = Chroma(persist_directory=self.VECTORSTORE_PATH, embedding_function=embedding)

        # Set up retriever
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

    def process_query(self, query):
        """Process the user query with the RAG pipeline."""
        # Define the system prompt
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know, say so. Keep the answer concise."
            "\n\n"
            "{context}"
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        # Configure RAG pipeline using self.model
        question_answer_chain = create_stuff_documents_chain(self.model, prompt)
        rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)

        # Process the query and return the response
        response = rag_chain.invoke({"input": query})
        return response.get("answer", "No answer found.")

    def invoke(self, query: str):
        """Invoke the process_query method for user interaction."""
        print("Processing query with RAG...")
        return self.process_query(query)

