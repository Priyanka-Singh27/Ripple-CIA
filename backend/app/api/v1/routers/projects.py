from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("")
async def create_project():
    pass

@router.get("")
async def list_projects():
    pass

@router.get("/{project_id}")
async def get_project(project_id: str):
    pass

@router.patch("/{project_id}")
async def update_project(project_id: str):
    pass

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    pass

@router.post("/{project_id}/confirm")
async def confirm_project_setup(project_id: str):
    pass
