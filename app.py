from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import json
from es_gpt import ESGPT

# Create an instance of the ESGPT class
es = ESGPT(index_name="papers")

# Create a FastAPI app
app = FastAPI()

# Define the search route


@app.get("/search")
async def search(q: str):
    # Perform a search for the query
    results = es.search(q)

    # Stream the search results to the client
    async def stream_response():
        for hit in results:
            yield "data: " + json.dumps(hit) + "\n\n"
        yield "[DONE]"

    return StreamingResponse(stream_response(), media_type="text/event-stream")

# Define the summary route


@app.post("/summary")
async def summary(request: Request):

    payload = await request.json()
    q = payload["q"]
    text_results = payload.get("text_results", "")

    if text_results:
        # Generate summaries of the search results
        resp = es.gpt_answer(q, text_results=text_results)
    else:
        es_results = es.search(q)

        if es_results:
            # Generate summaries of the search results
            resp = es.gpt_answer(q, es_results=es_results)
        else:
            resp = es.gpt_answer(q, text_results="No results found")

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)

    return StreamingResponse(resp.iter_content(1),
                             media_type="text/event-stream")

## 추가를 해보았는데 막상 제대로 동작하지 않는 것 같아서 우선은 사용하지 않습니다.
@app.post("/question-suggestion")
async def question_suggestion(request: Request):
    payload = await request.json()
    text_results = payload.get("text_results", "")

    if text_results is not None:
        # Generate further question by first relevent abstract text
        resp = es.gpt_question_generator(text_results=text_results)

        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        else:
            return StreamingResponse(resp.iter_content(1), media_type="text/event-stream")
    else:
        raise HTTPException(400, "Unexpected Error")

@app.post("/question")
async def question(request: Request):
    payload = await request.json()
    q = payload.get("q", "")

    if q:
        resp = es.gpt_direct_answer(q)
    else:
        raise HTTPException(400, "Unexpected Error")

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)

    return StreamingResponse(resp.iter_content(1),
                             media_type="text/event-stream")

# Define the static files route
# Need to set html=True to serve index.html
# Need to put at the end of the routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")
