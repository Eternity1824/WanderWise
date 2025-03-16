import uvicorn
from fastapi import FastAPI
from routers import router
app = FastAPI()


app.include_router(router.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
for route in app.routes:
    print(f"Route: {route.path}, Methods: {route.methods}")

# 启动应用
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8083, reload=False)