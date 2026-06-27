"""Start uvicorn server inline for debugging."""
import uvicorn
import os
os.environ['DATABASE_URL'] = 'sqlite:///./local_fallback.db'
import logging
logging.basicConfig(level=logging.DEBUG, filename='uvicorn_inline.log', filemode='w')

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, log_level='debug')
