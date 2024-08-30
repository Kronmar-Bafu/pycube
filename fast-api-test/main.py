from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from py_cube import get_observations, get_cube
import io

app = FastAPI()


@app.get("/lindas-cubes/observations/{env}-{identifier}-{version}")
async def observations(identifier: str, version: str, env: str):
    df = get_observations(identifier=identifier, version=version, endpoint=env)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response


@app.get("/lindas-cubes/uri/{env}-{identifier}-{version}")
async def get_uri(env: str, identifier: str, version: str):
    uris = get_cube(endpoint=env, identifier=identifier, version=version)
    return {"URI": uris}