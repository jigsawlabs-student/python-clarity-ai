import json
import requests
import openai

def build_source_text(idx, source):
    return (f"Source [{idx+1}]:\n{source.text}")

def generate_prompt(sources):
    source_texts = [build_source_text(idx, source) for idx, source in enumerate(sources)]
    context = "\n\n".join(source_texts)
    return f'''Provide a 2-3 sentence answer to the query based on the following sources. Be original, concise, accurate, and helpful. Cite sources as [1] or [2] or [3] after each sentence (not just the very end) to back up your answer (Ex: Correct: [1], Correct: [2][3], Incorrect: [1, 2]).

    {context}
    '''

    

def post_answer(prompt, api_key):
    COMPLETIONS_MODEL = "text-davinci-003"
    COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 300,
    "model": COMPLETIONS_MODEL}
    openai.api_key = api_key
    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )
    return response["choices"][0]["text"].strip(" \n")

def extract_source_links(sources):
    return [source.url for source in sources]

def read_chunks(data):
    decoder = json.JSONDecoder()
    reader = decoder.iterdecode(data)
    done = False

    while not done:
        value, done_reading = next(reader), False
        done = done_reading
        chunk_value = decoder.decode(value)
        yield chunk_value

async def handle_stream(query, sources, api_key, on_search, on_answer_update, set_loading):
    try:
        prompt = generate_prompt(sources)

        data = await post_answer(prompt, api_key)
        
        on_search({"query": query, "sourceLinks": extract_source_links(sources)})

        for chunk_value in read_chunks(data):
            on_answer_update(chunk_value)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
