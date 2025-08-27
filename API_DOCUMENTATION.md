# Voice Notes API - Documentação para Consumo

Esta documentação explica como consumir a API do backend Voice Notes para salvar transcrições de áudio.

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints Principais

### 1. Upload e Criar Voice Note

**Endpoint:** `POST /voice-notes/`

**Descrição:** Faz upload de um arquivo de áudio e cria uma voice note. A transcrição é processada automaticamente em background.

**Content-Type:** `multipart/form-data`

**Parâmetros:**
- `file` (arquivo, obrigatório): Arquivo de áudio
- `title` (string, obrigatório): Título da nota
- `description` (string, opcional): Descrição da nota

**Formatos suportados:** MP3, MP4, WAV, OGG, M4A

**Tamanho máximo:** 50MB

**Exemplo de Request:**
```http
POST /api/v1/voice-notes/
Content-Type: multipart/form-data

file=@audio.m4a
title=Reunião de equipe
description=Notas da reunião semanal
```

**Exemplo de Response (201):**
```json
{
  "id": 1,
  "title": "Reunião de equipe",
  "description": "Notas da reunião semanal",
  "file_name": "audio.m4a",
  "file_size": 1024000,
  "mime_type": "audio/mp4",
  "duration": null,
  "transcription_text": null,
  "transcription_status": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### 2. Buscar Voice Note Específica

**Endpoint:** `GET /voice-notes/{id}`

**Descrição:** Retorna uma voice note específica com status da transcrição atualizado.

**Exemplo de Request:**
```http
GET /api/v1/voice-notes/1
```

**Exemplo de Response (200):**
```json
{
  "id": 1,
  "title": "Reunião de equipe",
  "description": "Notas da reunião semanal",
  "file_name": "audio.m4a",
  "file_size": 1024000,
  "mime_type": "audio/mp4",
  "duration": null,
  "transcription_text": "Esta é a transcrição do áudio...",
  "transcription_status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 3. Buscar Apenas a Transcrição

**Endpoint:** `GET /voice-notes/{id}/transcription`

**Descrição:** Retorna apenas os dados de transcrição de uma voice note.

**Exemplo de Request:**
```http
GET /api/v1/voice-notes/1/transcription
```

**Exemplo de Response (200):**
```json
{
  "id": 1,
  "transcription_text": "Esta é a transcrição completa do áudio gravado...",
  "transcription_status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 4. Listar Voice Notes

**Endpoint:** `GET /voice-notes/`

**Descrição:** Lista todas as voice notes com paginação.

**Parâmetros de Query:**
- `page` (int, opcional): Número da página (padrão: 1)
- `per_page` (int, opcional): Items por página (padrão: 20, máximo: 100)

**Exemplo de Request:**
```http
GET /api/v1/voice-notes/?page=1&per_page=10
```

**Exemplo de Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Reunião de equipe",
      "description": "Notas da reunião semanal",
      "file_name": "audio.m4a",
      "file_size": 1024000,
      "mime_type": "audio/mp4",
      "duration": null,
      "transcription_text": "Transcrição...",
      "transcription_status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

## Status da Transcrição

A transcrição é processada em background. Os possíveis status são:

- `pending`: Aguardando processamento
- `processing`: Em processamento pela AssemblyAI
- `completed`: Transcrição concluída com sucesso
- `failed`: Falha no processamento

## Fluxo Recomendado para Apps

### 1. Upload Inicial
```
POST /voice-notes/ → Retorna voice note com status "pending"
```

### 2. Polling da Transcrição (opções)

**Opção A - Buscar note completa:**
```
GET /voice-notes/{id} → Verificar transcription_status
```

**Opção B - Buscar apenas transcrição:**
```
GET /voice-notes/{id}/transcription → Verificar transcription_status
```

### 3. Implementar Polling
- Fazer polling a cada 5-10 segundos
- Parar quando status for "completed" ou "failed"
- Implementar timeout (ex: 5 minutos máximo)

## Códigos de Erro

### 400 - Bad Request
```json
{
  "detail": "File extension .txt not allowed. Allowed extensions: ['.mp3', '.mp4', '.wav', '.ogg', '.m4a']"
}
```

### 404 - Not Found
```json
{
  "detail": "Voice note not found"
}
```

### 413 - File Too Large
```json
{
  "detail": "File size 60000000 bytes exceeds maximum allowed size of 50000000 bytes"
}
```

### 500 - Internal Server Error
```json
{
  "detail": "Error creating voice note: [error description]"
}
```

## Exemplo Completo - Flutter/Dart

```dart
// 1. Upload
final request = http.MultipartRequest(
  'POST',
  Uri.parse('http://localhost:8000/api/v1/voice-notes/')
);

request.files.add(await http.MultipartFile.fromPath('file', audioPath));
request.fields['title'] = 'Minha Nota';
request.fields['description'] = 'Descrição opcional';

final response = await request.send();
final voiceNote = await response.stream.bytesToString();

// 2. Polling para transcrição
Timer.periodic(Duration(seconds: 5), (timer) async {
  final transcription = await http.get(
    Uri.parse('http://localhost:8000/api/v1/voice-notes/$id/transcription')
  );
  
  final data = json.decode(transcription.body);
  if (data['transcription_status'] == 'completed') {
    timer.cancel();
    // Usar data['transcription_text']
  }
});
```

## Health Check

Para verificar se a API está funcionando:

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Documentação Interativa

Acesse `http://localhost:8000/docs` para documentação Swagger interativa com possibilidade de testar os endpoints diretamente no browser.