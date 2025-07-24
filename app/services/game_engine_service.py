from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, List, Optional, Set
from app.models.story import Story, StoryNode
from app.models.choice import Choice
from app.models.user_progress import UserProgress
from app.models.user import User, UserStats
from app.schemas.engine_schemas import (
    NodeResponse, ChoiceRequest, ChoiceResponse as GameChoiceResponse, 
    ValidationResult
)
from fastapi import HTTPException

class GameEngine:
    def __init__(self,db):
        self.db = db

    def start_story(self,story_id:int,user_id:Optional[int] = None) -> NodeResponse:
        """Start a new story session"""

        story = self.db.query(Story).filter(Story.story_id == story_id).first()

        if not story:
            raise HTTPException(
                status_code=404,
                detail="Story not found"
            )
        
        if not story.is_published:
            raise HTTPException(status_code=400, detail="Story is not published")
        
        #find starting node
        starting_node = self.db.query(StoryNode).filter(
            and_(
                StoryNode.story_id == story_id,
                StoryNode.is_starting_node == True
            )
        ).first()

        if not starting_node:
            raise HTTPException(status_code=400, detail="Story has no starting node")
        
        # Create or update user progress if user is logged in

        if user_id:
            self._create_or_update_progress(user_id,story_id,starting_node.node_id)

        return self._create_node_response(starting_node)
    
    def make_choice(self,choice_request:ChoiceRequest) -> GameChoiceResponse:
        """Process a player's choice and return the next node"""
        # Validate the choice
        choice = self.db.query(Choice).filter(
            Choice.choice_id == choice_request.choice_id
        ).first()

        if not choice:
            raise HTTPException(status_code=404, detail="Choice not found")

        # Verify the choice is valid from current node
        if choice.from_node_id != choice_request.current_node_id:
            raise HTTPException(
                status_code=400, 
                detail="Invalid choice for current node"
        )

        #Get the destination node
        next_node = self.db.query(StoryNode).filter(StoryNode.node_id == choice.to_node_id).first()

        if not next_node:
            raise HTTPException(status_code=404,detail="Destination node not found")
        
        # Update user progress if user is logged in
        progress_saved = False
        if choice_request.user_id:
            progress_saved = self._update_user_progress(
                choice_request.user_id,
                next_node.story_id,
                next_node.node_id,
                choice.choice_id,
                next_node.is_ending_node
            )

        return GameChoiceResponse(
            success=True,
            next_node=self._create_node_response(next_node),
            consequences=choice.consequences,
            is_ending=next_node.is_ending_node,
            progress_saved=progress_saved
        )

    def get_current_node(self,story_id:int,user_id : int) -> NodeResponse:
        """Get the current node for a user's story progress"""
        progress = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.story_id == story_id,
                UserProgress.is_completed == False
            )
        ).first()

        if not progress:
            # Return starting node if no progress exists
            return self.start_story(story_id,user_id)
        
        current_node = self.db.query(StoryNode).filter(StoryNode.node_id == progress.current_node_id).first()

        if not current_node:
            raise HTTPException(status_code=404, detail="Current node not found")
        
        return self._create_node_respones(current_node)
    
    def validate_story(self,story_id:int) -> ValidationResult:
        """Validate story structure for completeness and logic"""
        issues = []

        # Get all nodes and choices for the story
        nodes = self.db.query(StoryNode).filter(StoryNode.story_id == story_id).all()
        all_choices = self.db.query(Choice).join(
            StoryNode,Choice.from_node_id == StoryNode.node_id
        ).filter(StoryNode.story_id == story_id).all()

        if not nodes:
            issues.append("Story has no nodes")
            return ValidationResult(
                is_valid = False,
                issues = issues,
                total_nodes=0,
                total_choices=0
            )

        
        # Check for starting node
        starting_nodes = [n for n in nodes if n.is_starting_node]
        if len(starting_nodes) == 0:
            issues.append("Story has no starting node")
        elif len(starting_nodes) > 1:
            issues.append("Story has multiple starting nodes")
        
        # Check for ending nodes
        ending_nodes = [n for n in nodes if n.is_ending_node]
        if len(ending_nodes) == 0:
            issues.append("Story has no ending nodes")
        
        # Find unreachable nodes and dead ends
        reachable_nodes = self._find_reachable_nodes(nodes, all_choices)
        unreachable_nodes = [n.node_id for n in nodes if n.node_id not in reachable_nodes]
        
        dead_ends = self._find_dead_ends(nodes, all_choices)
        
        if unreachable_nodes:
            issues.append(f"Unreachable nodes found: {unreachable_nodes}")
        
        if dead_ends:
            issues.append(f"Dead end nodes found: {dead_ends}")
        
        # Check for choice letter conflicts
        choice_conflicts = self._find_choice_conflicts(all_choices)
        if choice_conflicts:
            issues.extend(choice_conflicts)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            total_nodes=len(nodes),
            total_choices=len(all_choices),
            unreachable_nodes=unreachable_nodes,
            dead_ends=dead_ends
        )

    def _create_node_response(self, node: StoryNode) -> NodeResponse:
        """Create a NodeResponse with choices"""
        choices = self.db.query(Choice).filter(
            Choice.from_node_id == node.node_id
        ).order_by(Choice.choice_letter).all()
        
        choices_data = [
            {
                "choice_id": choice.choice_id,
                "choice_text": choice.choice_text,
                "choice_letter": choice.choice_letter,
                "consequences": choice.consequences
            }
            for choice in choices
        ]
        
        return NodeResponse(
            node_id=node.node_id,
            node_title=node.node_title,
            content=node.content,
            is_starting_node=node.is_starting_node,
            is_ending_node=node.is_ending_node,
            node_type=node.node_type,
            choices=choices_data
        )

    def _create_or_update_progress(self, user_id: int, story_id: int, node_id: int):
        """Create or update user progress"""
        existing_progress = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.story_id == story_id
            )).first()
        
        if existing_progress:
            existing_progress.current_node_id = node_id
            existing_progress.is_completed = False
        else:
            new_progress = UserProgress(
                user_id=user_id,
                story_id=story_id,
                current_node_id=node_id,
                choice_node={},
                is_completed=False
            )
            self.db.add(new_progress)
        
        self.db.commit()

    def _update_user_progress(
        self, 
        user_id: int, 
        story_id: int, 
        node_id: int, 
        choice_id: int,
        is_completed: bool
    ) -> bool:
        """Update user progress with new choice"""
        try:
            progress = self.db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.story_id == story_id
                )
            ).first()
            
            if not progress:
                return False
            
            # Update progress
            progress.current_node_id = node_id
            progress.is_completed = is_completed
            
            # Update choice history
            if not progress.choice_node:
                progress.choice_node = {}
            
            progress.choice_node[str(progress.current_node_id)] = choice_id
            
            # Update user stats if story is completed
            if is_completed:
                self._update_user_stats(user_id, story_id)
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def _update_user_stats(self, user_id: int, story_id: int):
        """Update user statistics when story is completed"""
        stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)

        stats.stories_completed += 1

        #Update favorite category
        story = self.db.query(Story).filter(Story.story_id == story_id).first()
        if story not in story.category:
            stats.favorite_category = story.category

        self.db.commit()

    def _find_reachable_nodes(self,nodes:List[StoryNode],choices:List[Choice]) -> set[int]:
        """Find all nodes reachable from starting node"""
        starting_nodes = [n for n in nodes if n.is_starting_node]
        if not starting_nodes:
            return set()

        reachable = set()
        to_visit = [starting_nodes[0].node_id]

        #Build adjacency map
        adjacency = {}
        for choice in choices:
            if choice.from_node_id not in adjacency:
                adjacency[choice.from_node_id] = []
            adjacency[choice.from_node_id].append(choice.to_node_id)

        # BFS to find reachable nodes
        while to_visit:
            current = to_visit.pop(0)
            if current in reachable:
                continue

            reachable.add(current)
            if current in adjacency:
                to_visit.extend(adjacency[current])
        
        return reachable
    
    def _find_dead_ends(self, nodes: List[StoryNode], choices: List[Choice]) -> List[int]:
        """Find nodes with no outgoing choices (except ending nodes)"""
        nodes_with_choices = set(choice.from_node_id for choice in choices)
        ending_nodes = set(n.node_id for n in nodes if n.is_ending_node)
        
        dead_ends = []
        for node in nodes:
            if (node.node_id not in nodes_with_choices and 
                node.node_id not in ending_nodes):
                dead_ends.append(node.node_id)
        
        return dead_ends

    def _find_choice_conflicts(self,choices:List[Choice]) -> List[str]:
        """Find choice letter conflicts within same nodes"""

        conflicts =[]
        node_choices = {}

        for choice in choices:
            if choice.from_node_id not in node_choices:
                node_choices[choice.from_node_id] = {}

            letter = choice.choice_letter
            if letter in node_choices[choices.from_node_id]:
                conflicts.append(
                    f"Node {choice.from_node_id} has duplicate choice letter '{letter}'"
                )
            else:
                node_choices[choice.from_node_id][letter] = choice.choice_id

        return conflicts

