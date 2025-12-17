"""Skill memory for long-term learning through post-run reflection."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillEntry:
    """Represents a learned skill or pattern."""
    
    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        context: str,
        pattern: Dict[str, Any],
        success_rate: float = 1.0,
        usage_count: int = 1,
        created_at: Optional[str] = None
    ):
        """Initialize skill entry.
        
        Args:
            skill_id: Unique skill identifier
            name: Skill name
            description: Description of the skill
            context: Context where skill is applicable
            pattern: Pattern or template for applying the skill
            success_rate: Success rate of the skill (0-1)
            usage_count: Number of times skill has been used
            created_at: Creation timestamp
        """
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.context = context
        self.pattern = pattern
        self.success_rate = success_rate
        self.usage_count = usage_count
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'context': self.context,
            'pattern': self.pattern,
            'success_rate': self.success_rate,
            'usage_count': self.usage_count,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillEntry':
        """Create from dictionary."""
        return cls(
            skill_id=data['skill_id'],
            name=data['name'],
            description=data['description'],
            context=data['context'],
            pattern=data['pattern'],
            success_rate=data.get('success_rate', 1.0),
            usage_count=data.get('usage_count', 1),
            created_at=data.get('created_at')
        )


class SkillMemory:
    """Long-term skill memory through post-run reflection."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize skill memory.
        
        Args:
            storage_path: Path to store skill memory
        """
        self.storage_path = storage_path
        self.skills: Dict[str, SkillEntry] = {}
        
        if storage_path and storage_path.exists():
            self.load()
    
    def add_skill(self, skill: SkillEntry) -> None:
        """Add or update a skill.
        
        Args:
            skill: Skill entry to add
        """
        if skill.skill_id in self.skills:
            # Update existing skill
            existing = self.skills[skill.skill_id]
            existing.usage_count += 1
            
            # Update success rate (weighted average)
            total = existing.usage_count
            existing.success_rate = (
                (existing.success_rate * (total - 1) + skill.success_rate) / total
            )
            
            logger.info(f"Updated skill: {skill.name}")
        else:
            # Add new skill
            self.skills[skill.skill_id] = skill
            logger.info(f"Added new skill: {skill.name}")
    
    def get_skill(self, skill_id: str) -> Optional[SkillEntry]:
        """Get a skill by ID.
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Skill entry or None
        """
        return self.skills.get(skill_id)
    
    def search_skills(
        self,
        query: str,
        context: Optional[str] = None,
        min_success_rate: float = 0.5
    ) -> List[SkillEntry]:
        """Search for relevant skills.
        
        Args:
            query: Search query
            context: Optional context filter
            min_success_rate: Minimum success rate
            
        Returns:
            List of matching skills
        """
        results = []
        query_lower = query.lower()
        
        for skill in self.skills.values():
            # Filter by success rate
            if skill.success_rate < min_success_rate:
                continue
            
            # Filter by context if provided
            if context and context.lower() not in skill.context.lower():
                continue
            
            # Check if query matches name or description
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower()):
                results.append(skill)
        
        # Sort by success rate and usage count
        results.sort(
            key=lambda s: (s.success_rate, s.usage_count),
            reverse=True
        )
        
        return results
    
    def reflect_on_run(
        self,
        run_id: str,
        outcome: Dict[str, Any],
        pipeline_artifacts: Dict[str, Any]
    ) -> List[SkillEntry]:
        """Perform post-run reflection to extract learnings.
        
        Args:
            run_id: Run identifier
            outcome: Run outcome and metrics
            pipeline_artifacts: Artifacts from the pipeline
            
        Returns:
            List of extracted skills
        """
        extracted_skills = []
        
        # Analyze successful patterns
        if outcome.get('success', False):
            # Extract successful code patterns
            if 'code_files' in pipeline_artifacts:
                skill = self._extract_code_pattern_skill(
                    run_id,
                    pipeline_artifacts['code_files']
                )
                if skill:
                    extracted_skills.append(skill)
            
            # Extract successful planning patterns
            if 'blueprint' in pipeline_artifacts:
                skill = self._extract_planning_skill(
                    run_id,
                    pipeline_artifacts['blueprint']
                )
                if skill:
                    extracted_skills.append(skill)
        
        # Add extracted skills to memory
        for skill in extracted_skills:
            self.add_skill(skill)
        
        logger.info(f"Reflected on run {run_id}, extracted {len(extracted_skills)} skills")
        
        return extracted_skills
    
    def _extract_code_pattern_skill(
        self,
        run_id: str,
        code_files: List[Dict[str, Any]]
    ) -> Optional[SkillEntry]:
        """Extract code pattern skill from successful run.
        
        Args:
            run_id: Run identifier
            code_files: Generated code files
            
        Returns:
            Extracted skill or None
        """
        # Simple pattern extraction (can be enhanced)
        if not code_files:
            return None
        
        return SkillEntry(
            skill_id=f"code_pattern_{run_id}",
            name="Code Generation Pattern",
            description=f"Successful code pattern from run {run_id}",
            context="code_generation",
            pattern={
                'num_files': len(code_files),
                'file_types': list(set(f.get('type', 'unknown') for f in code_files))
            },
            success_rate=1.0
        )
    
    def _extract_planning_skill(
        self,
        run_id: str,
        blueprint: Dict[str, Any]
    ) -> Optional[SkillEntry]:
        """Extract planning skill from successful run.
        
        Args:
            run_id: Run identifier
            blueprint: Blueprint artifact
            
        Returns:
            Extracted skill or None
        """
        if not blueprint:
            return None
        
        return SkillEntry(
            skill_id=f"planning_pattern_{run_id}",
            name="Planning Pattern",
            description=f"Successful planning pattern from run {run_id}",
            context="blueprint_generation",
            pattern={
                'num_components': len(blueprint.get('component_specification', {}).get('components', [])),
                'build_order_size': len(blueprint.get('build_order', []))
            },
            success_rate=1.0
        )
    
    def get_top_skills(
        self,
        n: int = 10,
        context: Optional[str] = None
    ) -> List[SkillEntry]:
        """Get top-performing skills.
        
        Args:
            n: Number of skills to return
            context: Optional context filter
            
        Returns:
            List of top skills
        """
        filtered_skills = list(self.skills.values())
        
        if context:
            filtered_skills = [
                s for s in filtered_skills
                if context.lower() in s.context.lower()
            ]
        
        # Sort by success rate and usage
        filtered_skills.sort(
            key=lambda s: (s.success_rate, s.usage_count),
            reverse=True
        )
        
        return filtered_skills[:n]
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save skill memory to file.
        
        Args:
            path: Optional path to save to
        """
        save_path = path or self.storage_path
        
        if not save_path:
            raise ValueError("No storage path specified")
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'skills': {
                skill_id: skill.to_dict()
                for skill_id, skill in self.skills.items()
            }
        }
        
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved skill memory to: {save_path}")
    
    def load(self, path: Optional[Path] = None) -> None:
        """Load skill memory from file.
        
        Args:
            path: Optional path to load from
        """
        load_path = path or self.storage_path
        
        if not load_path or not load_path.exists():
            logger.warning("No skill memory file to load")
            return
        
        with open(load_path, 'r') as f:
            data = json.load(f)
        
        self.skills = {
            skill_id: SkillEntry.from_dict(skill_data)
            for skill_id, skill_data in data.get('skills', {}).items()
        }
        
        logger.info(f"Loaded {len(self.skills)} skills from: {load_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get skill memory statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.skills:
            return {
                'total_skills': 0,
                'avg_success_rate': 0.0,
                'total_usage': 0
            }
        
        return {
            'total_skills': len(self.skills),
            'avg_success_rate': sum(s.success_rate for s in self.skills.values()) / len(self.skills),
            'total_usage': sum(s.usage_count for s in self.skills.values()),
            'contexts': list(set(s.context for s in self.skills.values()))
        }
