import os
import sys

from django.apps import AppConfig


class MovieConfig(AppConfig):
    name = 'movie'

    def ready(self):
        # Solo al servir la app: precarga el modelo de embeddings en segundo plano para que
        # el primer POST a /recommend/ no se quede cargando mientras se importa torch.
        # Con autoreload solo el proceso hijo (RUN_MAIN=true) atiende requests.
        serving = "runserver" in sys.argv and (
            os.environ.get("RUN_MAIN") == "true" or "--noreload" in sys.argv
        )
        if serving:
            from .ai_utils import preload_embedding_model

            preload_embedding_model()
