from fastapi import FastAPI
import wireup
import wireup.integration.fastapi

from composition.di.container import create_container
from presentation.routes.session import router as session_router
from presentation.routes.exercise import router as exercise_router
from presentation.routes.evaluate import router as evaluate_router

app = FastAPI()
app.include_router(session_router)
app.include_router(exercise_router)
app.include_router(evaluate_router)

container = create_container()

wireup.integration.fastapi.setup(container, app)
