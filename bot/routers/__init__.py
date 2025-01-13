__all__ = ("router", )

from aiogram import Router

from .users.admin import router as admin_commands_router
from .users.users import router as users_commands_router
from .users.lawyers import router as lawyers_commands_router
from .scripts.registration import router as registration_commands_router

router = Router(name=__name__)

router.include_router(admin_commands_router)
router.include_router(registration_commands_router)
router.include_router(users_commands_router)
router.include_router(lawyers_commands_router)



