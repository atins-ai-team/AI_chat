#from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
import main_program
#from langchain_community.embeddings.bedrock import BedrockEmbeddings


def get_embedding_function():
    #embeddings = BedrockEmbeddings(
    #    credentials_profile_name="default", region_name="us-east-1"
    #)
    print(main_program.main_prog.get_ollama_url()  )
    embeddings = OllamaEmbeddings(model="nomic-embed-text",base_url =  main_program.main_prog.get_ollama_url() )
    return embeddings
