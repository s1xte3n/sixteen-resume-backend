# API Schemas

## VisitorSuccess

```json
{"type":"object","required":["count"],"properties":{"count":{"type":"integer","minimum":1}},"additionalProperties":false}
```

## ErrorEnvelope

```json
{"type":"object","required":["error"],"properties":{"error":{"type":"object","required":["code","message","requestId"],"properties":{"code":{"type":"string"},"message":{"type":"string"},"requestId":{"type":"string","format":"uuid"}},"additionalProperties":false}},"additionalProperties":false}
```
