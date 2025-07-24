from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NodeResponse(BaseModel):
    node_id : int
    node_title : str
    content : str
    is_starting_node : bool
    is_ending_node : bool
    node_type: str
    choices:List[Dict[str,Any]] = []

class ChoiceRequest(BaseModel):
    current_node_id: int
    choice_id: int
    user_id: Optional[int] = None



class ChoiceResponse(BaseModel):
    success: bool
    next_node: NodeResponse
    consequences: Optional[str] = None
    is_ending: bool
    progress_saved: bool

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str] = []
    total_nodes: int
    total_choices: int
    unreachable_nodes: List[int] = []
    dead_ends: List[int] = []   

