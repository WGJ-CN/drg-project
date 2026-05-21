from fastapi import APIRouter, HTTPException, Body
from app.models.schemas import GroupResponse
from app.services.drg_service import drg_service

router = APIRouter()

@router.post("/group/raw", response_model=GroupResponse)
async def group_raw(raw_text: str = Body(..., media_type="text/plain")):
    try:
        result = drg_service.group_from_text(raw_text)
        return GroupResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分组失败: {str(e)}")