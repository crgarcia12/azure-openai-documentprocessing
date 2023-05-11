import logging
import azure.functions as func
import json, requests, time, os, logging, re
import openai
from time import sleep
from http.client import HTTPConnection

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        body = json.dumps(req.get_json())
        print(body)
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )

def compose_response(json_data):
    values = json.loads(json_data)['values']

    # Prepare the Output before the loop
    results = {}
    results["values"] = []

    for value in values:
        outputRecord = transform_value(value)
        if outputRecord != None:
            results["values"].append(outputRecord)
    return json.dumps(results, ensure_ascii=False)

def transform_value(value):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('text' in data), "'text' corpus field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "data":{},
            "errors": [ { "message": "Error:" + error.args[0] }   ]
            })

    try:
        result = get_aoai_embeddings(value)
    except:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Could not complete operation for record." }   ]
            })

    return ({
            "recordId": recordId,
            "data": {
                "contentVector": result
                    }
            })


def get_aoai_embeddings (value):
    
    openai.api_key = os.environ["openai.api_key"]
    openai.api_base = os.environ["openai.api_base"]
    openai.api_version = os.environ["openai.api_version"]
    openai.api_type = os.environ["openai.api_type"]

    engine = "text-embedding-ada-002"
    corpus = str(value['data']['text'])

    max_retry = 3
    retry = 0
    # We need to chunk corpus string into equally sized chunks of 6000 characters. In OpenAI 1 token ~= 4 chars. Max token for davinci is ~4k tokens, other models have a 2k limit
    chunks = [corpus[i:i+6000] for i in range(0, len(corpus), 6000)]
    total_embeddings = []
    # loop through the chunks until over

    for chunk in chunks:
        try:
            text = chunk.replace("\n", " ")
            response = openai.Embedding.create(input=[text], engine=engine)
            embeddings = response['data'][0]['embedding']
            #embeddings = re.sub('\s+', ' ', embeddings)
            total_embeddings = total_embeddings + embeddings
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)
        return total_embeddings



