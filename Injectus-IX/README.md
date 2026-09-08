# Injectus IX Face Recognition v3

Production face-auth stack for the airlock.
**INTERNAL — DO NOT REDISTRIBUTE.**

## Files in this bundle

- `face_recognition_v3.safetensors`   – template embeddings
- `face_recognition_v3.metadata.json` – roster sidecar (id, name, rank in row order)
- `legacy_manifest.png`               – unrelated archival scan, kept for retention

## Operations

- **On-call:** `#faceauth-prod` (paged via Substation OpsBot)
- **Last sync:** 2147-03-14, 9 templates
- **Source:** `tryhaulme/airlock-faceauth` (internal repo, not in this bundle)

## Change log

- v3 (current): switched to safetensors + JSON sidecar; dropped legacy framing.
- v2: raised matcher threshold after the Cypheron adversarial-input incident.
- v1: initial deploy.
