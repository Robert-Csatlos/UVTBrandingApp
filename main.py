import uvicorn

if __name__ == "__main__":
    print("Running the server for UVT Branding App...")
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True);