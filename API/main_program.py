import os
class main_prog(object):
    @staticmethod
    def get_ollama_url():
        return os.getenv('ollama_url', 'http://localhost:11434')
    
    @staticmethod
    def get_model_main():
        return os.getenv('MODEL_MAIN', 'llama3.2')
    
    @staticmethod
    def get_model_embedding():
        return os.getenv('MODEL_EMBEDDING', 'nomic-embed-text')