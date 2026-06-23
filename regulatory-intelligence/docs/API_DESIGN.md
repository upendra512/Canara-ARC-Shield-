# API Design

FastAPI routes should be thin.

Routes should:

- validate requests
- call graph entry points
- return response models

Routes should not:

- hide business logic
- call external APIs
- directly implement node behavior

## Endpoint Skeletons

`POST /documents/intake`

Purpose:
Submit a new offline document intake request.

`GET /documents/{document_id}`

Purpose:
Fetch a stored document.

`POST /intelligence/{document_id}/run`

Purpose:
Run Layer 1 regulatory intelligence.

`POST /compliance/{document_id}/run`

Purpose:
Run Layer 2 compliance intelligence.

`GET /review/queue`

Purpose:
List items pending human review.

`POST /review/{item_id}/decision`

Purpose:
Submit approval, rejection, or requested changes.

See `api/routes.py` for code skeletons.
