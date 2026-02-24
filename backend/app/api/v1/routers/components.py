from fastapi import APIRouter

router = APIRouter(prefix="/projects/{project_id}/components", tags=["components"])

@router.post("")
async def create_component(project_id: str):
    pass

@router.get("")
async def list_components(project_id: str):
    pass

@router.patch("/{component_id}")
async def update_component(project_id: str, component_id: str):
    pass

@router.delete("/{component_id}")
async def delete_component(project_id: str, component_id: str):
    pass

@router.post("/{component_id}/contributors")
async def add_contributor(project_id: str, component_id: str):
    pass

@router.delete("/{component_id}/contributors/{user_id}")
async def remove_contributor(project_id: str, component_id: str, user_id: str):
    pass
