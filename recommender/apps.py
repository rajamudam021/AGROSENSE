from django.apps import AppConfig


class RecommenderConfig(AppConfig):
    name = 'recommender'

    def ready(self):
        # Warm up the ML model at startup so the first prediction request is instant
        try:
            from .ml.loader import load_bundle
            load_bundle()
        except Exception:
            pass  # Don't crash startup if model is missing
