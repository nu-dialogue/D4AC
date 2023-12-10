from typing import Optional, Dict,Union
from fastapi import FastAPI
from pydantic import BaseModel


class SystemUtterance(BaseModel):
    expression: str
    utterance: str


class SystemMessage(BaseModel):
    systemUtterance: SystemUtterance
    talkend: bool
    sessionId: Union[str,None] = None
    timestamp: str


app = FastAPI()


@app.post('/dummyResponse/')
def dummy_response(request: SystemMessage):
    print(str(request))
    return request


