# Voice Notes API

MVP backend para aplicativo de voice notes com FastAPI e PostgreSQL.

## Funcionalidades

- ✅ Upload de arquivos de áudio (MP3, MP4, WAV, OGG, M4A)
- ✅ Transcrição automática via AssemblyAI API
- ✅ CRUD completo para voice notes
- ✅ Validação de tipos e tamanhos de arquivo
- ✅ Paginação nas listagens
- ✅ Documentação automática com Swagger

## Configuração

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Configurar PostgreSQL
Criar database e configurar URL no .env:
```
DATABASE_URL=postgresql://user:password@localhost:5432/voicenotes
```

### 4. Configurar AssemblyAI
Obter API key em https://www.assemblyai.com/ e configurar no .env:
```
ASSEMBLYAI_API_KEY=your_api_key_here
```

### 5. Executar migrações
```bash
alembic upgrade head
```

### 6. Executar servidor
```bash
uvicorn main:app --reload
```

## API Endpoints

### Voice Notes
- `POST /api/v1/voice-notes/` - Upload e criar nota
- `GET /api/v1/voice-notes/` - Listar notas (com paginação)
- `GET /api/v1/voice-notes/{id}` - Buscar nota específica
- `PUT /api/v1/voice-notes/{id}` - Atualizar nota
- `DELETE /api/v1/voice-notes/{id}` - Deletar nota
- `GET /api/v1/voice-notes/{id}/transcription` - Buscar transcrição

### Outros
- `GET /` - Status da API
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger

## Estrutura do Projeto

```
app/
├── api/
│   └── routes/
│       └── voice_notes.py    # Endpoints da API
├── core/
│   ├── config.py             # Configurações
│   └── database.py           # Conexão com BD
├── models/
│   └── voice_note.py         # Modelos SQLAlchemy
├── schemas/
│   └── voice_note.py         # Schemas Pydantic
├── services/
│   └── transcription_service.py  # Integração AssemblyAI
└── utils/
    ├── file_handler.py       # Manipulação de arquivos
    └── file_validator.py     # Validação de arquivos
```

## Exemplo de Uso

### Upload de voice note
```bash
curl -X POST "http://localhost:8000/api/v1/voice-notes/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3" \
  -F "title=Minha Nota" \
  -F "description=Descrição opcional"
```

### Listar voice notes
```bash
curl "http://localhost:8000/api/v1/voice-notes/?page=1&per_page=10"
```

### Buscar transcrição
```bash
curl "http://localhost:8000/api/v1/voice-notes/1/transcription"
```