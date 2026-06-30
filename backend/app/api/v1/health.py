from fastapi import APIRouter
from starlette.status import HTTP_200_OK

router = APIRouter()

@router.get('/health', status_code=HTTP_200_OK)
async def health_check():
    return {'status': 'ok'}
