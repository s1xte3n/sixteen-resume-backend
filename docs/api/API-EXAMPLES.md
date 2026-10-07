# API Examples

## Success

```bash
curl -i http://localhost:7071/api/visitors
```

Expected HTTP 200 with a body such as:

```json
{"count":1}
```

The response also contains an `X-Request-ID` UUID v4 header.

## Valid request ID

```bash
curl -i -H "X-Request-ID: 550e8400-e29b-41d4-a716-446655440000" http://localhost:7071/api/visitors
```

The same UUID v4 is returned in the response header and `error.requestId` when an error occurs.

## Invalid request ID

```bash
curl -i -H "X-Request-ID: not-a-uuid" http://localhost:7071/api/visitors
```

Expected HTTP 400 with `BAD_REQUEST` and no counter increment.

## Unsupported query

```bash
curl -i "http://localhost:7071/api/visitors?foo=bar"
```

Expected HTTP 400 with `BAD_REQUEST` and no counter increment.

## Unsupported body

```bash
curl -i -X GET -H "Content-Type: application/json" --data '{}' http://localhost:7071/api/visitors
```

Expected HTTP 400 with `BAD_REQUEST` and no counter increment.

## Unsupported method

```bash
curl -i -X POST http://localhost:7071/api/visitors
```

Expected HTTP 405 with `METHOD_NOT_ALLOWED` and no counter increment.
