import os
class main_prog(object):
    @staticmethod
    def get_ollama_url():
        return os.getenv('ollama_url', 'http://localhost:11434')