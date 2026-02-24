from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user():
    pass

@router.post("/login")
async def login_user():
    pass

@router.get("/me")
async def get_current_user_profile():
    pass

@router.post("/logout")
async def logout_user():
    pass

@router.get("/github")
async def github_oauth_redirect():
    pass

@router.get("/github/callback")
async def github_oauth_callback():
    pass
