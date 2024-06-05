from database.request import get_admins


async def admin_check(user_id):
    _ = await get_admins()
    if _:
        if user_id in _:
            return True
        else:
            return False
    else:
        return False
