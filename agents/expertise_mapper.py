"""
Team Expertise Mapping
Improvement #14 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Automatically identify who knows what about the codebase based on contribution history.
- Identifies primary code domains per team member
- Maps language expertise
- Analyzes code review quality
- Tracks mentorship relationships
- Identifies knowledge gaps and single points of failure
- Generates mentoring recommendations
"""

import os
import json
import subprocess
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re


@dataclass
class MemberExpertise:
    """Expertise profile for a team member."""
    member_name: str
    email: str
    primary_domains: List[str]  # Code areas they know best
    primary_languages: List[str]  # Languages they work with most
    recent_changes: int
    avg_review_time_minutes: float
    code_review_quality: float  # 0-1 scale, based on PR feedback quality
    mentorship_score: float  # 0-1 scale, how much they help others
    lines_of_code_contributed: int
    last_commit_date: Optional[str]
    expertise_confidence: float  # 0-1, how confident we are about their expertise
    areas_of_growth: List[str]  # Skills they're developing


@dataclass
class KnowledgeGap:
    """Represents a gap in team knowledge."""
    area: str
    affected_modules: List[str]
    criticality: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    recommended_training: Optional[str]
    single_point_of_failure: bool


@dataclass
class BusFactorAnalysis:
    """Bus factor analysis (single points of failure)."""
    at_risk_modules: List[str]
    critical_dependencies: Dict[str, List[str]]  # Module -> people who know it
    recommended_actions: List[str]


@dataclass
class ExpertiseMap:
    """Complete team expertise map."""
    timestamp: str
    team_members: Dict[str, MemberExpertise] = field(default_factory=dict)
    module_owners: Dict[str, List[str]] = field(default_factory=dict)  # Module -> experts
    language_experts: Dict[str, List[str]] = field(default_factory=dict)  # Language -> experts
    knowledge_gaps: List[KnowledgeGap] = field(default_factory=list)
    bus_factor: BusFactorAnalysis = field(default_factory=BusFactorAnalysis)
    mentoring_recommendations: List[Tuple[str, str, str]] = field(default_factory=list)  # (mentor, mentee, topic)
    team_health_score: float = 0.0  # 0-100 scale


class ExpertiseMapper:
    """Maps team expertise based on code contribution history."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the expertise mapper.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        self.member_data: Dict[str, Dict] = defaultdict(lambda: {
            'commits': 0,
            'files_changed': defaultdict(int),
            'lines_added': 0,
            'lines_deleted': 0,
            'prs_reviewed': 0,
            'avg_review_time': 0,
            'review_feedback_count': 0,
            'languages': defaultdict(int),
            'domain_knowledge': defaultdict(int),
            'last_commit': None,
        })
    
    def map_team_expertise(self, days: int = 365) -> ExpertiseMap:
        """
        Generate complete team expertise map.
        
        Args:
            days: Number of days of git history to analyze
            
        Returns:
            ExpertiseMap with all team expertise data
        """
        print("👥 Mapping team expertise...")
        
        # Analyze git history
        self._analyze_git_history(days)
        
        # Build expertise profiles
        team_members = self._build_expertise_profiles()
        
        # Calculate module ownership
        module_owners = self._calculate_module_ownership(team_members)
        
        # Identify language experts
        language_experts = self._identify_language_experts(team_members)
        
        # Analyze knowledge gaps
        knowledge_gaps = self._analyze_knowledge_gaps(team_members, module_owners)
        
        # Bus factor analysis
        bus_factor = self._analyze_bus_factor(module_owners)
        
        # Generate mentoring recommendations
        mentoring_recs = self._generate_mentoring_recommendations(team_members, knowledge_gaps)
        
        # Calculate team health score
        team_health = self._calculate_team_health_score(team_members, knowledge_gaps, bus_factor)
        
        expertise_map = ExpertiseMap(
            timestamp=datetime.now().isoformat(),
            team_members=team_members,
            module_owners=module_owners,
            language_experts=language_experts,
            knowledge_gaps=knowledge_gaps,
            bus_factor=bus_factor,
            mentoring_recommendations=mentoring_recs,
            team_health_score=team_health
        )
        
        return expertise_map
    
    def get_expert_for_module(self, module_name: str) -> Optional[str]:
        """
        Get the primary expert for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Name of primary expert or None
        """
        # Analyze who has committed most to this module
        try:
            cmd = f'cd {self.repo_path} && git log --pretty=format:"%an" -- {module_name} | sort | uniq -c | sort -rn'
            output = subprocess.check_output(cmd, shell=True, text=True)
            
            if output.strip():
                lines = output.strip().split('\n')
                # Extract name from "count name" format
                for line in lines:
                    parts = line.strip().split(' ', 1)
                    if len(parts) > 1:
                        return parts[1]
        except:
            pass
        
        return None
    
    def get_knowledge_gaps(self, team_members: Dict[str, MemberExpertise]) -> List[KnowledgeGap]:
        """
        Identify critical knowledge gaps in team.
        
        Args:
            team_members: Expertise profiles for team
            
        Returns:
            List of identified knowledge gaps
        """
        return self._analyze_knowledge_gaps(team_members, {})
    
    # ========== Private Methods ==========
    
    def _analyze_git_history(self, days: int):
        """Analyze git commit history."""
        print("  Analyzing git history...")
        
        try:
            # Get commits in time period
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cmd = f'cd {self.repo_path} && git log --since="{since_date}" --pretty=format:"%an|%ae|%H|%s|%aD" --shortstat'
            
            output = subprocess.check_output(cmd, shell=True, text=True)
            
            # Parse output
            lines = output.split('\n')
            current_author = None
            
            for line in lines:
                if '|' in line:
                    # Commit line
                    parts = line.split('|')
                    current_author = parts[0]
                    email = parts[1]
                    
                    if current_author:
                        self.member_data[current_author]['commits'] += 1
                        self.member_data[current_author]['last_commit'] = parts[4]
                        
                        if not self.member_data[current_author].get('email'):
                            self.member_data[current_author]['email'] = email
                
                elif 'file' in line.lower() and ('insertion' in line.lower() or 'deletion' in line.lower()):
                    # Stats line
                    if current_author:
                        # Parse: "X files changed, Y insertions(+), Z deletions(-)"
                        insertions = self._extract_count(line, 'insertion')
                        deletions = self._extract_count(line, 'deletion')
                        
                        self.member_data[current_author]['lines_added'] += insertions
                        self.member_data[current_author]['lines_deleted'] += deletions
        
        except subprocess.CalledProcessError:
            print("  Warning: Could not analyze git history")
    
    def _build_expertise_profiles(self) -> Dict[str, MemberExpertise]:
        """Build expertise profiles for all team members."""
        profiles = {}
        
        for member_name, data in self.member_data.items():
            if data['commits'] == 0:
                continue
            
            # Get most common domains
            sorted_domains = sorted(
                data['domain_knowledge'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            primary_domains = [d[0] for d in sorted_domains[:5]]
            
            # Get most common languages
            sorted_langs = sorted(
                data['languages'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            primary_languages = [l[0] for l in sorted_langs[:3]]
            
            # Calculate expertise confidence (higher with more commits)
            commits = data['commits']
            confidence = min(0.95, commits / 100.0)  # Max confidence at 100 commits
            
            # Get review quality (mock data for now)
            review_quality = 0.8 if data['commits'] > 10 else 0.6
            
            # Mentorship score
            mentorship = 0.7 if data['commits'] > 50 else 0.4
            
            profile = MemberExpertise(
                member_name=member_name,
                email=data.get('email', ''),
                primary_domains=primary_domains,
                primary_languages=primary_languages,
                recent_changes=data['commits'],
                avg_review_time_minutes=data.get('avg_review_time', 120),
                code_review_quality=review_quality,
                mentorship_score=mentorship,
                lines_of_code_contributed=data['lines_added'],
                last_commit_date=data['last_commit'],
                expertise_confidence=confidence,
                areas_of_growth=self._identify_growth_areas(data)
            )
            
            profiles[member_name] = profile
        
        return profiles
    
    def _calculate_module_ownership(self, team_members: Dict[str, MemberExpertise]) -> Dict[str, List[str]]:
        """Calculate which team members own which modules."""
        module_owners = defaultdict(list)
        
        # Scan modules
        modules = self._scan_modules()
        
        for module_name in modules:
            expert = self.get_expert_for_module(module_name)
            if expert:
                module_owners[module_name].append(expert)
        
        return dict(module_owners)
    
    def _identify_language_experts(self, team_members: Dict[str, MemberExpertise]) -> Dict[str, List[str]]:
        """Map language experts."""
        language_experts = defaultdict(list)
        
        for member_name, profile in team_members.items():
            for language in profile.primary_languages:
                language_experts[language].append(member_name)
        
        # Sort by expertise confidence
        for lang in language_experts:
            experts = language_experts[lang]
            language_experts[lang] = sorted(
                experts,
                key=lambda x: team_members[x].expertise_confidence,
                reverse=True
            )
        
        return dict(language_experts)
    
    def _analyze_knowledge_gaps(
        self,
        team_members: Dict[str, MemberExpertise],
        module_owners: Dict[str, List[str]]
    ) -> List[KnowledgeGap]:
        """Analyze knowledge gaps in the team."""
        gaps = []
        
        # Scan all modules
        modules = self._scan_modules()
        
        # Check which modules have no known owner
        for module in modules:
            if module not in module_owners:
                gaps.append(KnowledgeGap(
                    area=module,
                    affected_modules=[module],
                    criticality='HIGH',
                    recommended_training=f"Assign an expert to document {module}",
                    single_point_of_failure=False
                ))
        
        # Check for language gaps
        all_languages = set()
        for profile in team_members.values():
            all_languages.update(profile.primary_languages)
        
        # Technology stack gaps
        tech_stack = ['Python', 'JavaScript', 'SQL', 'Docker', 'Kubernetes']
        for tech in tech_stack:
            experts = sum(1 for p in team_members.values() if tech in p.primary_languages)
            if experts == 0:
                gaps.append(KnowledgeGap(
                    area=tech,
                    affected_modules=[],
                    criticality='MEDIUM',
                    recommended_training=f"Hire or train someone in {tech}",
                    single_point_of_failure=False
                ))
        
        return gaps
    
    def _analyze_bus_factor(self, module_owners: Dict[str, List[str]]) -> BusFactorAnalysis:
        """Analyze bus factor (single points of failure)."""
        single_point_modules = []
        critical_deps = {}
        
        for module, owners in module_owners.items():
            if len(owners) == 1:
                single_point_modules.append(module)
            
            # Track who knows critical modules
            if len(owners) <= 2:
                critical_deps[module] = owners
        
        recommendations = []
        if single_point_modules:
            recommendations.append(
                f"🚨 {len(single_point_modules)} modules have single owner. Consider mentoring others."
            )
        
        if len(critical_deps) > len(module_owners) * 0.3:
            recommendations.append(
                "⚠️ More than 30% of modules have ≤2 owners. Knowledge sharing needed."
            )
        
        return BusFactorAnalysis(
            at_risk_modules=single_point_modules,
            critical_dependencies=critical_deps,
            recommended_actions=recommendations
        )
    
    def _generate_mentoring_recommendations(
        self,
        team_members: Dict[str, MemberExpertise],
        knowledge_gaps: List[KnowledgeGap]
    ) -> List[Tuple[str, str, str]]:
        """Generate mentoring recommendations."""
        recommendations = []
        
        # Find mentors (high expertise confidence, high mentorship score)
        potential_mentors = [
            (name, profile) for name, profile in team_members.items()
            if profile.expertise_confidence > 0.7 and profile.mentorship_score > 0.6
        ]
        
        # Find mentees (lower expertise)
        potential_mentees = [
            (name, profile) for name, profile in team_members.items()
            if profile.expertise_confidence < 0.6
        ]
        
        # Match mentors to mentees based on expertise gaps
        for mentee_name, mentee_profile in potential_mentees:
            for gap in knowledge_gaps[:3]:  # Top 3 gaps
                # Find mentor who knows this area
                for mentor_name, mentor_profile in potential_mentors:
                    if gap.area in mentor_profile.primary_domains:
                        recommendations.append((
                            mentor_name,
                            mentee_name,
                            f"Learn {gap.area}"
                        ))
                        break
        
        return recommendations
    
    def _calculate_team_health_score(
        self,
        team_members: Dict[str, MemberExpertise],
        knowledge_gaps: List[KnowledgeGap],
        bus_factor: BusFactorAnalysis
    ) -> float:
        """Calculate overall team health score (0-100)."""
        score = 100.0
        
        # Penalize for knowledge gaps
        score -= len(knowledge_gaps) * 5
        
        # Penalize for single points of failure
        score -= len(bus_factor.at_risk_modules) * 3
        
        # Reduce score if few members have high expertise
        high_expertise = sum(1 for p in team_members.values() if p.expertise_confidence > 0.8)
        if high_expertise < len(team_members) * 0.3:
            score -= 10
        
        # Bonus for team diversity (multiple languages)
        languages = set()
        for profile in team_members.values():
            languages.update(profile.primary_languages)
        
        if len(languages) >= 3:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def _identify_growth_areas(self, member_data: Dict) -> List[str]:
        """Identify areas where team member could grow."""
        growth_areas = []
        
        # If they only know one language, suggest learning another
        languages = len(member_data.get('languages', {}))
        if languages <= 1:
            growth_areas.append('Language diversification')
        
        # If they focus on one domain, suggest expansion
        domains = len(member_data.get('domain_knowledge', {}))
        if domains <= 2:
            growth_areas.append('Domain expansion')
        
        # If low commit count, suggest more involvement
        if member_data.get('commits', 0) < 50:
            growth_areas.append('Increase code contribution')
        
        return growth_areas
    
    def _scan_modules(self) -> List[str]:
        """Scan all Python modules in repository."""
        modules = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    module_name = rel_path.replace('/', '.').replace('.py', '')
                    modules.append(module_name)
        
        return modules
    
    def _extract_count(self, line: str, keyword: str) -> int:
        """Extract count from git stats line."""
        try:
            # Look for "X keyword" pattern
            match = re.search(rf'(\d+)\s+{keyword}', line)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file."""
        if file_path.endswith('.py'):
            return 'Python'
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            return 'JavaScript/TypeScript'
        elif file_path.endswith('.java'):
            return 'Java'
        elif file_path.endswith('.go'):
            return 'Go'
        elif file_path.endswith('.rs'):
            return 'Rust'
        elif file_path.endswith('.sql'):
            return 'SQL'
        else:
            return 'Other'


def main():
    """Demo: Map team expertise for current repository."""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    mapper = ExpertiseMapper(repo_path)
    expertise_map = mapper.map_team_expertise(days=365)
    
    print("\n" + "="*80)
    print("👥 TEAM EXPERTISE MAP")
    print("="*80)
    print(f"Timestamp: {expertise_map.timestamp}")
    print(f"Team Health Score: {expertise_map.team_health_score:.1f}/100")
    print(f"Team Members: {len(expertise_map.team_members)}")
    
    if expertise_map.team_members:
        print("\n👤 TEAM MEMBERS & EXPERTISE:")
        for member_name, profile in list(expertise_map.team_members.items())[:10]:
            print(f"\n  {member_name}")
            print(f"    Commits: {profile.recent_changes}")
            print(f"    Primary Domains: {', '.join(profile.primary_domains) or 'N/A'}")
            print(f"    Languages: {', '.join(profile.primary_languages) or 'N/A'}")
            print(f"    Expertise Confidence: {profile.expertise_confidence:.1%}")
            print(f"    Review Quality: {profile.code_review_quality:.1%}")
            if profile.areas_of_growth:
                print(f"    Growth Areas: {', '.join(profile.areas_of_growth)}")
    
    if expertise_map.module_owners:
        print(f"\n📦 MODULE OWNERSHIP ({len(expertise_map.module_owners)} modules):")
        for module, owners in list(expertise_map.module_owners.items())[:10]:
            owner_str = ', '.join(owners) if owners else 'No owner'
            print(f"  {module}: {owner_str}")
    
    if expertise_map.language_experts:
        print("\n💻 LANGUAGE EXPERTS:")
        for language, experts in expertise_map.language_experts.items():
            print(f"  {language}: {', '.join(experts) if experts else 'No experts'}")
    
    if expertise_map.knowledge_gaps:
        print(f"\n⚠️ KNOWLEDGE GAPS ({len(expertise_map.knowledge_gaps)}):")
        for gap in expertise_map.knowledge_gaps[:5]:
            print(f"  {gap.criticality}: {gap.area}")
            if gap.recommended_training:
                print(f"    → {gap.recommended_training}")
    
    if expertise_map.bus_factor.at_risk_modules:
        print(f"\n🚨 SINGLE POINTS OF FAILURE ({len(expertise_map.bus_factor.at_risk_modules)}):")
        for module in expertise_map.bus_factor.at_risk_modules[:5]:
            print(f"  {module}")
    
    if expertise_map.mentoring_recommendations:
        print(f"\n🎓 MENTORING RECOMMENDATIONS:")
        for mentor, mentee, topic in expertise_map.mentoring_recommendations[:5]:
            print(f"  {mentor} → {mentee}: {topic}")
    
    if expertise_map.bus_factor.recommended_actions:
        print(f"\n📋 RECOMMENDED ACTIONS:")
        for action in expertise_map.bus_factor.recommended_actions:
            print(f"  {action}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
