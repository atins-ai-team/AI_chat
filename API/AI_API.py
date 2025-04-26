try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
  print("An exception occurred")
import os
import main_program
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from get_embedding_function import get_embedding_function

from flask import Flask, request, Response,  stream_with_context

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from duckduckgo_search import DDGS

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

CHROMA_PATH = "chroma"
HISTORY_SIZE = 12
ALLOWED_IPS=["10.90.30.45","10.90.14.76"]
MAX_SESSION_TIME = 43200

db = None
model = None
fast_model = None
history_aware_retriever = None


def getWebDocs( input:str ):
    document =[]
    try:
        results = DDGS(verify=False).text(input, max_results=3)
        for x in results:
            document.append( Document( page_content= json.dumps(x)))
    except:
        print("Can not download web data")

    return document


def clean_sesions():
    current_time = time.time() 
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    root = 'sessions/'
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if(os.path.isfile(full_path)):
                file_time = os.stat(full_path).st_mtime 
                if(file_time < current_time - MAX_SESSION_TIME): 
                    print(f" Delete : {full_path}") 
                    os.remove(full_path) 
    
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not os.listdir(full_path): 
                print(f" Delete : {full_path}") 
                os.rmdir(full_path)


def get_history(ip, user, id, size: int ):
    try:
        with open(f"sessions/{ip}/{user}/{id}", "r") as f:
            allHistory = json.loads(f.read())
            return allHistory[size:]
    except:
        return []


def save_history(ip, user, id, history):
    if not os.path.exists(f"sessions/{ip}/{user}"): 
        os.makedirs(f"sessions/{ip}/{user}")
    with open(f"sessions/{ip}/{user}/{id}", "w+") as f:
        f.write(json.dumps(history))


def delete_history(ip, user, id):

    if os.path.exists(f"sessions/{ip}/{user}/{id}"):
        os.remove(f"sessions/{ip}/{user}/{id}")

    root = 'sessions/'
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not os.listdir(full_path): 
                print(f" Delete : {full_path}") 
                os.rmdir(full_path)


def add_initial_system_message(messages_list):
    messages_list.insert(0,SystemMessage( """
    Answer only in English. 
    You are an employee in the dean's office. You provide information about the University named 'Akademia Techniczno-Informatyczna w Naukach Stosowanych (ATINS)' in Wroclaw.
   .
    """))
# Always remind humans to ask as detailed questions as possible, using complete sentences

def add_user_ai_messages(messages_list, history_json):
    for who, text in history_json:
        if who == 'HumanMessage':
            messages_list.append(HumanMessage(text))

        elif who == "AIMessage":
            messages_list.append(AIMessage(text))
        
        elif who == "SystemMessage":
            messages_list.append(SystemMessage(text))


def add_RAG_message(messages_list, rag_message, index = -1):

    pre_message = """
    Answer only in English!
    Answer the next question based only on the following context and your knowledge:

    """
    messages_list.insert(index, SystemMessage(pre_message + rag_message))


def add_user_message(messages_list, message):
    messages_list.append(HumanMessage(message))

def add_system_message(messages_list, message):
    messages_list.append(SystemMessage(message))
        

def query_rag(query_text: str, ip, user, id):
    output_parser = StrOutputParser()
    messages=[]
    context_text = ""

    # Get history
    history = get_history(ip, user, id, -1*HISTORY_SIZE)
    add_initial_system_message(messages)
    add_user_ai_messages(messages, history)
    
    # Search Web
    #web_data= history_aware_retriever_web.invoke({"input": query_text, "chat_history": messages })
    #context_text += "\n[WEB DATA - requery]\n" + "\n---\n".join([ doc.page_content for doc in web_data])
    #print(web_data)

    #Search WEB
    #try:
        #results = DDGS(verify=False).text(query_text, max_results=3)
       # context_text += "\n[WEB DATA]\n"+"\n---\n".join(f"{item}" for item in results)
        #print(results)
    #except:
       # print("Can not download web data")


    # Search DB and change include history
    RAG_data= history_aware_retriever.invoke({"input": query_text, "chat_history": messages })
    context_text += "\n[INTERNAL DATA - requery]\n" + "\n---\n".join([ doc.page_content for doc in RAG_data])
       
    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=3)
    context_text += "\n[INTERNAL DATA]\n"+"\n---\n".join([ doc.page_content for doc, _score in results])
    
    
    add_RAG_message(messages, context_text, len(messages))
    add_user_message(messages, query_text)

    #print(messages)
   
   
    # Send to model

    chain = model | output_parser
    response_text = chain.invoke(messages)
    #response_text = model.invoke(messages)
    

    # Save history
    history.append(("HumanMessage", query_text))
    history.append(("AIMessage", response_text))

    save_history(ip, user, id, history)
    
    return response_text





@app.route('/query_AI', methods=['GET', 'POST'])
def query_AI():
    #if  request.remote_addr in ALLOWED_IPS:
        # query = request.json["query"]
        # id = request.json["id"]
        # user = request.json["user"]
        
        # response = query_rag(query, request.remote_addr, user, id)

        # print ("*******************************************")
        # print ("["+request.remote_addr+"_"+str(id)+"]")
        # print (query)
        # print ("")
        # print (response)
        # print ("*******************************************")
        # return response

    """
    Obsługuje zarówno tradycyjny (blokujący) request,
    jak i streaming SSE jeśli w payload pojawi się "stream": true.
    """
    data = request.get_json()
    query = data["query"]
    session_id = data["id"]
    user = data["user"]
    do_stream = data.get("stream", False)

    # Przygotuj historię i wiadomości dla modelu
    history = get_history(request.remote_addr, user, session_id, -HISTORY_SIZE)
    messages = []
    add_initial_system_message(messages)
    add_user_ai_messages(messages, history)
    add_user_message(messages, query)

    if not do_stream:
        # tryb blokujący: zwróć pełną odpowiedź na raz
        response_text = (model | StrOutputParser()).invoke(messages)
        history.append(("HumanMessage", query))
        history.append(("AIMessage", response_text))
        save_history(request.remote_addr, user, session_id, history)
        return response_text

    # streaming mode: SSE token-po-tokenie
    def generate():
        # Generator tokenów z Twojego LLM-a
        stream = model.invoke_stream(messages, streaming=True)
        full_resp = []
        for token in stream:
            # token może być stringiem lub obiektem z .text
            part = token if isinstance(token, str) else token.text
            full_resp.append(part)
            yield f"data: {part}\n\n"
        # po zakończeniu streamu zapisz całość do historii
        history.append(("HumanMessage", query))
        history.append(("AIMessage", "".join(full_resp)))
        save_history(request.remote_addr, user, session_id, history)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )


    #else:
     #   return "Your IP is not in allowed list!", 403

@app.route('/get_history_AI', methods=['GET', 'POST'])
def get_history_AI():
    #if  request.remote_addr in ALLOWED_IPS:
        id = request.json["id"]
        user = request.json["user"]
        history = get_history(request.remote_addr, user, id, -1*HISTORY_SIZE)
        #history = get_history("10.90.30.45", user, id, -1*HISTORY_SIZE)
        return history
   # else:
       # return "Your IP is not in allowed list!", 403

@app.route('/delete_history_AI', methods=['GET', 'POST'])
def delete():
   # if  request.remote_addr in ALLOWED_IPS:
        id = request.json["id"]
        user = request.json["user"]
        delete_history(request.remote_addr, user, id)
        #delete_history("10.90.30.45", user, id)
        return ""
    #else:
    #    return "Your IP is not in allowed list!", 403



if __name__ == "__main__":

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=clean_sesions, trigger="interval", seconds=3600)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    # Initialize DB
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)


    #Initialize model
    model = OllamaLLM(model= main_program.main_prog.get_model_main(), base_url =  main_program.main_prog.get_ollama_url())

    ####
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
        verbose=True, 
    )



    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )

    # Create a prompt template for contextualizing questions
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    # Create a history-aware retriever
    # This uses the LLM to help reformulate the question based on chat history
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt, 
    )

    # Create a history-aware web retriever
    history_aware_retriever_web = create_history_aware_retriever(
        model,  RunnableLambda(lambda x: getWebDocs(x)), contextualize_q_prompt, 
    )

    # Answer question prompt
    # This system prompt helps the AI understand that it should provide concise answers
    # based on the retrieved context and indicates what to do if the answer is unknown
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following pieces of retrieved context to answer the "
        "question. If you don't know the answer, just say that you "
        "don't know. Use ONE sentences maximum and keep the answer "
        "concise."
        "\n\n"
        "{context}"
    )

    # Create a prompt template for answering questions
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )


    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    rag_chain = create_retrieval_chain( history_aware_retriever, question_answer_chain)
    rag_chain_web = create_retrieval_chain( history_aware_retriever_web, question_answer_chain)






    #Run API
    app.run(host="0.0.0.0", port=8001, debug=True, threaded=True)
    
