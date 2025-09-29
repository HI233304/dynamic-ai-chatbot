import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
USE_REDIS = False
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
