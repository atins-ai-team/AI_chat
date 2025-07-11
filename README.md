# AI Chatbot ATINS

Projekt interaktywnego asystenta dziekanatu uczelni **Akademia Techniczno-Informatyczna w Naukach Stosowanych (ATINS)**, umożliwiającego uzyskiwanie informacji w języku angielskim dzięki integracji z dużym modelem językowym (LLM).

---

## 📌 Cele projektu

- Automatyzacja odpowiedzi na pytania studentów.
- Obsługa zapytań z kontekstem (RAG - Retrieval-Augmented Generation).
- Integracja PDF-ów z informacjami uczelni jako baza wiedzy.
- Interfejs webowy z responsywnym i prostym UI.

---

## 🧠 Architektura systemu

```
[ Użytkownik ]
     │
     ▼
[ Frontend (React + Tailwind) ]
     │ POST /query_AI
     ▼
[ Flask API + LangChain ]
     ├── ChromaDB (embeddings)
     └── Ollama (LLM)
     ▼
[ Odpowiedź strumieniowa SSE ]
```

---

## 🧩 Komponenty

### Frontend

- React + TypeScript + TailwindCSS
- React Hook Form + Zod (formularze)
- Obsługa strumieniowania odpowiedzi
- Motyw jasny/ciemny

### Backend

- Flask + LangChain + Chroma
- Endpointy:
  - `POST /query_AI`
  - `POST /get_history_AI`
  - `POST /delete_history_AI`
- Zapisywanie historii sesji użytkownika
- Scheduler czyszczący stare sesje

### LLM (Ollama)

- `llama3` – model główny
- `nomic-embed-text` – embeddingi
- Serwowany lokalnie przez `ollama serve`
- Automatyczne pobieranie modeli (`entrypoint.sh`)

---

## 🔁 Historia sesji

- Pliki `sessions/<ip>/<user>/<id>`
- Przechowuje ostatnie 12 wiadomości
- Obsługa czyszczenia i usuwania przez API

---

## 📚 Retrieval-Augmented Generation (RAG)

1. Wczytanie PDF-ów (`data/`)
2. Podział na fragmenty (1000 znaków, overlap 80)
3. Embedding + wektorowe wyszukiwanie (Chroma)
4. LLM generuje odpowiedź na bazie kontekstu

---

## 🔌 API

### POST `/query_AI`

```json
{
  "id": "1",
  "user": "2",
  "query": "What are the specialities?",
  "stream": true
}
```

- `id`, `user` – identyfikatory sesji i użytkownika
- `query` – treść pytania
- `stream` – czy odpowiedź ma być wysyłana liniami

📤 Odpowiedź:
```text
data: The dean's office is located in building A, room 105.
```

---

## 🌐 Wyszukiwanie w sieci (opcjonalne)

- Funkcja `getWebDocs()` wykorzystuje DuckDuckGo Search
- Domyślnie wyłączona – możliwa do aktywacji w kodzie

---

## 🚀 Uruchomienie projektu (Docker Compose)

### 1. Wymagania

- Docker + Docker Compose

### 2. Start

```bash
docker compose up 
```

### 3. Porty

| Komponent   | Adres                  |
|-------------|------------------------|
| Frontend    | http://localhost:8080  |
| Backend API | http://localhost:8001  |
| Ollama      | http://localhost:11434 |

---

💡 **Uwaga:** Jeśli na komputerze nie ma zainstalowanego sterownika NVIDIA lub nie posiadasz karty graficznej obsługiwanej przez Docker + GPU, możesz **zakomentować** poniższy fragment w pliku `compose.yaml`  — dzięki temu aplikacja uruchomi się na procesorze (CPU):

```yaml
    deploy:
       resources:
         reservations:
           devices:
             - driver: nvidia
               count: all
               capabilities:
                 - gpu
```
## 🧪 Test zapytania

```bash
curl -X POST http://localhost:8001/query_AI \
 -H "Content-Type: application/json" \
 -d '{"id":"1","user":"2","query":"Where is the dean's office located?"}'
```

---

## 🛠️ Pliki projektu

- `API/AI_API.py` – backend Flask
- `API/populate_database.py` – przetwarzanie PDF-ów
- `Front/` – frontend aplikacji
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh` – konfiguracja kontenerów

---

## 🔮 Możliwości rozwoju

- Autoryzacja użytkowników
- Interfejs administratora
- Wsparcie dla wielu języków
- OCR dla zeskanowanych dokumentów
- Rozbudowana analiza zapytań

---

## 📄 Licencja

Projekt edukacyjny dla celów wewnętrznych uczelni ATINS.

> Autorzy: [Ernest Torz, Jakub Krawiec, Mateusz Plewa]

