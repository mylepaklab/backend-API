# AI-BIMTranslator API

## Overview
AI-BIMTranslator is a Flask-based API designed for translating simple sentences and matching animation sequences based on input text. It leverages sentence embeddings using the `sentence-transformers` library for semantic similarity and integrates with the Sea-Lion translation API to provide multilingual translations.

## Features
- Match input sentences to predefined animation sequences using semantic search.
- Translate sentences related to height, occupation, or name into Malay, Thai, and Vietnamese.
- Fuzzy matching for known occupations.
- CORS enabled to allow specific frontend clients.

## API Endpoints

### `GET /`
Returns a string with available API routes.

### `GET /health`
Returns a JSON indicating the server is healthy.

```json
{
  "status": "ok"
}
```

### `GET /get_name`
Returns the API name/version.

### `GET /match_animation_sequence`
Matches the input sentence with known animation sequences.
#### Curl Test for Animation Landmark Retrieval
```bash
curl -i -H "Origin: http://localhost:3000" "https://backend-api-fm4g.onrender.com/match_animation_sequence?sentence=apa%2Cnama"
```

### `GET /form_answer`
Translates input text related to height, occupation, or name into multiple languages using Sea-Lion API.
#### Curl Test for Occupation
```bash
curl -i -H "Origin: http://localhost:3000" "https://backend-api-fm4g.onrender.com/form_answer?text_to_translate=DoktorSTOP"
```
#### Curl Test for Name
```bash
curl -i -H "Origin: http://localhost:3000" "https://backend-api-fm4g.onrender.com/form_answer?text_to_translate=AndrewSTOP"
```
#### Curl Test for Height
```bash
curl -i -H "Origin: http://localhost:3000" "https://backend-api-fm4g.onrender.com/form_answer?text_to_translate=117STOP"
```
