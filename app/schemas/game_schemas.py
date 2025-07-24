# from pydantic import BaseModel, EmailStr, Field, validator
# from typing import Optional, List, Dict, Any
# from datetime import datetime
# from enum import Enum



# class GameStateResponse(BaseModel):
#     current_node: StoryNodeResponse
#     available_choices: List[ChoiceResponse]
#     progress: UserProgressResponse
#     story_info: StoryResponse

# class MakeChoiceRequest(BaseModel):
#     progress_id: int
#     choice_id: int

# class MakeChoiceResponse(BaseModel):
#     success: bool
#     message: str
#     new_node: Optional[StoryNodeResponse] = None
#     available_choices: Optional[List[ChoiceResponse]] = None
#     is_story_completed: bool = False