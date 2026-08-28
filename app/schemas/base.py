from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar("T")

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class CommonQueryParams(BaseSchema):
    search:         Optional[str] = None
    sort_by:        Optional[str] = None
    sort_order:     Optional[str] = None
    offset:         Optional[int] = 0
    limit:          Optional[int] = 10
    allow_deleted:  Optional[bool] = None

    def build_queries(self, exclude_fields: List[str] = []) -> Dict[str, Any]:
        data = self.model_dump(mode='json')
        common_fields = {"search", "sort_by", "sort_order", "offset", "limit", "allow_deleted"}
        
        filters = {
            k: [v] if not isinstance(v, list) else v 
            for k, v in data.items() 
            if k not in common_fields and v is not None and k not in exclude_fields
        }
        
        result = {k: v for k, v in data.items() if k in common_fields}
        result["filters"] = filters
        return result

class PaginationMeta(BaseSchema):
    total:  int
    offset: int
    limit:  int
    next:   bool = False

    @model_validator(mode="after")
    def calculate_next(self) -> "PaginationMeta":
        self.next = self.offset + self.limit < self.total
        return self

class DataListResponse(BaseSchema, Generic[T]):
    items: List[T]
    meta:  PaginationMeta