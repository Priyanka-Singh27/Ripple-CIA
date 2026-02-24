from fastapi import APIRouter

router = APIRouter(tags=["changes"])

@router.post("/projects/{project_id}/changes")
async def submit_change(project_id: str):
    pass

@router.get("/projects/{project_id}/changes")
async def list_project_changes(project_id: str):
    pass

@router.get("/changes/{change_id}/impact")
async def get_change_impact(change_id: str):
    pass

@router.post("/changes/{change_id}/acknowledge")
async def acknowledge_impact(change_id: str):
    pass

@router.post("/changes/{change_id}/approve")
async def approve_change(change_id: str):
    pass

@router.get("/changes")
async def list_global_changes(scope: str = "mine"):
    pass
