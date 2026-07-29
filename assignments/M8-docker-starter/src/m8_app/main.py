from fastapi import FastAPI


app = FastAPI(title="Контейнерный учебный сервис")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
