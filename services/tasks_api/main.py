from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/api/health-check/")
async def health_check():
    return {"message": "ok"}

handle = Mangum(app)
