"""Journalist Newsworthiness Agent

Evaluates press releases for likelihood of journalist interest and coverage
in Singapore mainstream and alternative platforms.
"""

import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import os
from openai import OpenAI


class NewsworthinessTier(Enum):
    """Tier of newsworthiness."""
    HIGHLY_NEWSWORTHY = "highly_newsworthy"
    NEWSWORTHY = "newsworthy"
    MODERATELY_NEWSWORTHY = "moderately_newsworthy"
    LOW_NEWSWORTHINESS = "low_newsworthiness"
    NOT_NEWSWORTHY = "not_newsworthy"


class PlatformType(Enum):
    """Types of media platforms."""
    MAINSTREAM = "mainstream"
    TECH_MEDIA = "tech_media"
    BUSINESS = "business"
    INDUSTRY_SPECIFIC = "industry_specific"
    ALTERNATIVE = "alternative"


@dataclass
class ScoringCriteria:
    """Scoring criteria for newsworthiness evaluation."""
    timeliness: float
    impact: float
    novelty: float
    controversy: float
    sg_relevance: float
    human_interest: float
    credibility: float
    clarity: float

    def calculate_weighted_score(self) -> float:
        """Calculate weighted overall score."""
        weights = {
            'timeliness': 0.15,
            'impact': 0.20,
            'novelty': 0.15,
            'controversy': 0.10,
            'sg_relevance': 0.20,
            'human_interest': 0.10,
            'credibility': 0.05,
            'clarity': 0.05
        }
        
        score = (
            self.timeliness * weights['timeliness'] +
            self.impact * weights['impact'] +
            self.novelty * weights['novelty'] +
            self.controversy * weights['controversy'] +
            self.sg_relevance * weights['sg_relevance'] +
            self.human_interest * weights['human_interest'] +
            self.credibility * weights['credibility'] +
            self.clarity * weights['clarity']
        )
        return round(score, 2)


@dataclass
class ImprovementSuggestion:
    """Suggestion for improving press release."""
    category: str
    current_score: float
    recommendation: str
    example: str
    priority: str


@dataclass
class NewsworthinessReport:
    """Complete newsworthiness evaluation report."""
    overall_score: float
    tier: NewsworthinessTier
    primary_platforms: List[PlatformType]
    secondary_platforms: List[PlatformType]
    scoring_breakdown: ScoringCriteria
    improvements: List[ImprovementSuggestion]
    journalist_targeting: Dict[str, List[str]]
    key_angles: List[str]
    estimated_reach: Dict[str, str]
    summary: str


class JournalistNewsworthinessAgent:
    """AI agent for evaluating press release newsworthiness for Singapore media."""

    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo"

    def evaluate_press_release(self, press_release_content: str) -> NewsworthinessReport:
        """Evaluate a press release for newsworthiness."""
        
        extraction_prompt = self._build_extraction_prompt(press_release_content)
        extraction_response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        extracted_data = json.loads(extraction_response.choices[0].message.content)
        scoring_criteria = self._score_criteria(press_release_content, extracted_data)
        platforms = self._identify_platforms(extracted_data, scoring_criteria)
        improvements = self._generate_improvements(scoring_criteria, extracted_data)
        journalist_targeting = self._generate_journalist_targeting(platforms, extracted_data)
        key_angles = self._extract_angles(extracted_data)
        reach_estimates = self._estimate_reach(platforms)
        
        overall_score = scoring_criteria.calculate_weighted_score()
        tier = self._score_to_tier(overall_score)
        
        return NewsworthinessReport(
            overall_score=overall_score,
            tier=tier,
            primary_platforms=platforms['primary'],
            secondary_platforms=platforms['secondary'],
            scoring_breakdown=scoring_criteria,
            improvements=improvements,
            journalist_targeting=journalist_targeting,
            key_angles=key_angles,
            estimated_reach=reach_estimates,
            summary=self._generate_summary(overall_score, tier, improvements)
        )

    def _build_extraction_prompt(self, content: str) -> str:
        """Build prompt for extracting key information."""
        return f"""Analyze this press release and extract key information in JSON format:

Press Release:
{content}

Extract and return as JSON:
{{
  "headline": "main topic",
  "company_or_organization": "who is issuing this",
  "key_announcements": ["announcement 1", "announcement 2"],
  "business_sector": "industry/sector",
  "singapore_connection": "how is it connected to Singapore",
  "affected_stakeholders": ["who is affected"],
  "numbers_impact": "quantifiable impact if any",
  "is_first_mover": true/false,
  "partnership_or_collaboration": "any partnerships mentioned",
  "regulatory_implications": "any regulatory angle"
}}

Return only valid JSON."""

    def _score_criteria(self, content: str, extracted: Dict) -> ScoringCriteria:
        """Score the press release against newsworthiness criteria."""
        
        prompt = f"""Score this press release on a 0-10 scale for Singapore journalists.

Content: {content[:1000]}...
Extracted data: {json.dumps(extracted)}

Score and return as JSON:
{{
  "timeliness": score (0-10),
  "impact": score (0-10),
  "novelty": score (0-10),
  "controversy": score (0-10),
  "sg_relevance": score (0-10),
  "human_interest": score (0-10),
  "credibility": score (0-10),
  "clarity": score (0-10)
}}

Return only valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        scores = json.loads(response.choices[0].message.content)
        
        return ScoringCriteria(
            timeliness=float(scores['timeliness']),
            impact=float(scores['impact']),
            novelty=float(scores['novelty']),
            controversy=float(scores['controversy']),
            sg_relevance=float(scores['sg_relevance']),
            human_interest=float(scores['human_interest']),
            credibility=float(scores['credibility']),
            clarity=float(scores['clarity'])
        )

    def _identify_platforms(self, extracted: Dict, scores: ScoringCriteria) -> Dict:
        """Identify which platforms would be most interested."""
        
        prompt = f"""Based on this press release profile, which Singapore media platforms would be most interested?

Extracted data: {json.dumps(extracted)}
Scores: timeliness={scores.timeliness}, impact={scores.impact}, novelty={scores.novelty}, sg_relevance={scores.sg_relevance}

Return JSON:
{{
  "primary_platforms": ["mainstream", "tech_media", etc.],
  "secondary_platforms": ["alternative", "industry_specific", etc.]
}}

Use only these platform types: mainstream, tech_media, business, industry_specific, alternative
Return only valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        platforms_data = json.loads(response.choices[0].message.content)
        
        return {
            'primary': [PlatformType(p) for p in platforms_data['primary_platforms']],
            'secondary': [PlatformType(p) for p in platforms_data['secondary_platforms']]
        }

    def _generate_improvements(self, scores: ScoringCriteria, extracted: Dict) -> List[ImprovementSuggestion]:
        """Generate specific improvement suggestions."""
        
        criteria_scores = [
            ('timeliness', scores.timeliness),
            ('impact', scores.impact),
            ('novelty', scores.novelty),
            ('controversy', scores.controversy),
            ('sg_relevance', scores.sg_relevance),
            ('human_interest', scores.human_interest),
            ('credibility', scores.credibility),
            ('clarity', scores.clarity)
        ]
        
        lowest_criteria = sorted(criteria_scores, key=lambda x: x[1])[:3]
        
        prompt = f"""Generate specific improvement suggestions for this press release.

Lowest scoring areas: {[c[0] for c in lowest_criteria]}
Extracted data: {json.dumps(extracted)}

Return JSON:
{{
  "improvements": [
    {{
      "category": "criterion_name",
      "current_score": score,
      "recommendation": "specific action to take",
      "example": "example of how to implement",
      "priority": "high/medium/low"
    }}
  ]
}}

Return only valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        improvements_data = json.loads(response.choices[0].message.content)
        
        return [ImprovementSuggestion(**imp) for imp in improvements_data['improvements']]

    def _generate_journalist_targeting(self, platforms: Dict, extracted: Dict) -> Dict:
        """Generate journalist targeting recommendations."""
        
        prompt = f"""What types of journalists at Singapore media outlets would be most interested in this story?

Platforms: {[p.value for p in platforms['primary']]}
Story: {json.dumps(extracted)}

Return JSON:
{{
  "mainstream": ["journalist type 1", "journalist type 2"],
  "tech_media": ["journalist type 1"],
  "business": ["journalist type 1"],
  "industry_specific": ["journalist type 1"],
  "alternative": ["journalist type 1"]
}}

Return only valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    def _extract_angles(self, extracted: Dict) -> List[str]:
        """Extract key story angles for journalists."""
        
        prompt = f"""What are the most compelling story angles for journalists in this press release?

Story: {json.dumps(extracted)}

Return JSON:
{{
  "angles": ["angle 1", "angle 2", "angle 3"]
}}

Return only valid JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        angles_data = json.loads(response.choices[0].message.content)
        return angles_data['angles']

    def _estimate_reach(self, platforms: Dict) -> Dict:
        """Estimate potential reach by platform."""
        
        reach_estimates = {
            'mainstream': '500k - 1M readers',
            'tech_media': '50k - 200k readers',
            'business': '100k - 300k readers',
            'industry_specific': '10k - 50k readers',
            'alternative': '50k - 150k readers'
        }
        
        result = {}
        for platform in platforms['primary']:
            result[platform.value] = reach_estimates[platform.value]
        
        return result

    def _score_to_tier(self, score: float) -> NewsworthinessTier:
        """Convert numeric score to tier."""
        if score >= 8.0:
            return NewsworthinessTier.HIGHLY_NEWSWORTHY
        elif score >= 6.5:
            return NewsworthinessTier.NEWSWORTHY
        elif score >= 5.0:
            return NewsworthinessTier.MODERATELY_NEWSWORTHY
        elif score >= 3.0:
            return NewsworthinessTier.LOW_NEWSWORTHINESS
        else:
            return NewsworthinessTier.NOT_NEWSWORTHY

    def _generate_summary(self, score: float, tier: NewsworthinessTier, improvements: List[ImprovementSuggestion]) -> str:
        """Generate executive summary."""
        
        tier_descriptions = {
            NewsworthinessTier.HIGHLY_NEWSWORTHY: "This press release has excellent potential for journalist pickup across multiple platforms. It's ready for distribution.",
            NewsworthinessTier.NEWSWORTHY: "This press release should perform well with journalists. Consider minor refinements.",
            NewsworthinessTier.MODERATELY_NEWSWORTHY: "This press release has merit but needs improvements to increase journalist interest.",
            NewsworthinessTier.LOW_NEWSWORTHINESS: "This press release may have limited appeal to journalists. Significant revisions recommended.",
            NewsworthinessTier.NOT_NEWSWORTHY: "This press release is unlikely to interest journalists in its current form. Major repositioning needed."
        }
        
        summary = f"Score: {score}/10 ({tier.value})\n{tier_descriptions[tier]}\n"
        
        if improvements:
            summary += f"\nTop improvement: {improvements[0].recommendation}"
        
        return summary
