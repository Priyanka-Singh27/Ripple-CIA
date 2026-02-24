from fastapi import APIRouter

router = APIRouter(tags=["users_and_notifications"])

@router.get("/notifications")
async def list_notifications():
    pass

@router.post("/notifications/mark-read")
async def mark_notifications_read():
    pass

@router.post("/invites")
async def create_invite():
    pass

@router.post("/invites/{invite_id}/accept")
async def accept_invite(invite_id: str):
    pass

@router.post("/invites/{invite_id}/decline")
async def decline_invite(invite_id: str):
    pass

@router.get("/users/collaborators")
async def list_collaborators():
    pass

@router.get("/users/search")
async def search_users(q: str):
    pass
