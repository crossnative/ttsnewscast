# ttsnewscast

## Backend

Start the backend: `python api.py`

Test:

```
curl -X POST http://localhost:8000/extract \                                                                                                                 rell@MBCXDL4Y4V0WMT
  -H "Content-Type: application/json" \
  -d '{"url": "https://knightcolumbia.org/content/ai-as-normal-technology"}'
  ```

### Docker

`docker build -t ttsnewscast:0.1.0 .`

`docker run -p 8000:8000 ttsnewscast:0.1.0`