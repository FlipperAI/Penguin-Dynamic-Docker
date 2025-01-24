from fastapi import APIRouter
from .submissions import get_submissions_router

class submissions_router:
    def get_submissions_router(self):
        return get_submissions_router()

submissions_router = submissions_router()
router = APIRouter()
router.include_router(submissions_router.get_submissions_router())
submissions_router = router
