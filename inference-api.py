from fastapi import FastAPI

inference = FastAPI()

# Define a root `/` endpoint
@inference.get('/')
def index():
    return {'ok': True}