# API Examples

## Success

```bash
curl -i http://localhost:7071/api/visitors
```

Expected response shape: `{"count":1}`

## Valid request ID

```bash
curl -i -H "X-Request-ID: 550e8400-e29b-41d4-a716-446655440000" http://localhost:7071/api/visitors
```

The same UUID v4 is returned.

## Invalid request ID

```bash
curl -i -H "X-Request-ID: not-a-uuid" http://localhost:7071/api/visitors
```

Expected HTTP 400 and `BAD_REQUEST`.

## Unsupported query

```bash
curl -i "http://localhost:7071/api/visitors?foo=bar"
```

Expected HTTP 400 and no counter increment.

## Unsupported method

```bash
curl -i -X POST http://localhost:7071/api/visitors
```

Expected HTTP 405 and no counter increment.
