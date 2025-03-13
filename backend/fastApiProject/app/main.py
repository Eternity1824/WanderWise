from fastapi import FastAPI
from routers import posts
app = FastAPI()


app.include_router(posts.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
for route in app.routes:
    print(f"Route: {route.path}, Methods: {route.methods}")