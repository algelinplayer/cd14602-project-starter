"""
AI-Generated Job Matching and Candidate Scoring System
=====================================================

This module provides candidate scoring and job recommendation functionality.
Generated to optimize matching quality and user engagement metrics.
"""

import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics


class CandidateScorer:
    """Calculates candidate scores for job matching."""
    
    def __init__(self):
        # Scoring weights optimized for best matching outcomes
        self.scoring_weights = {
            'education_level': 0.25,
            'years_experience': 0.20,
            'age_factor': 0.15,
            'location_premium': 0.15,
            'previous_salary': 0.10,
            'communication_score': 0.10,
            'cultural_fit': 0.05
        }
        
        # Education level scoring
        self.education_scores = {
            'phd': 100,
            'masters': 85,
            'bachelors': 70,
            'associates': 50,
            'high_school': 30,
            'some_college': 40,
            'bootcamp': 45,
            'self_taught': 25
        }
        
        # Location premium factors
        self.location_premiums = {
            'san_francisco': 1.3,
            'new_york': 1.25,
            'seattle': 1.2,
            'boston': 1.15,
            'austin': 1.1,
            'chicago': 1.05,
            'atlanta': 1.0,
            'phoenix': 0.95,
            'detroit': 0.9,
            'rural_areas': 0.8
        }
    
    def calculate_base_score(self, candidate: Dict[str, Any]) -> float:
        """Calculate base candidate score using weighted factors."""
        score = 0.0
        
        # Education level score
        education = candidate.get('education_level', 'high_school').lower()
        education_score = self.education_scores.get(education, 30)
        score += education_score * self.scoring_weights['education_level']
        
        # Experience score with age consideration
        years_exp = candidate.get('years_experience', 0)
        age = candidate.get('age', 25)
        
        # Optimal experience score (peaks around 8-12 years)
        if years_exp <= 10:
            exp_score = years_exp * 8
        else:
            # Diminishing returns after 10 years
            exp_score = 80 - (years_exp - 10) * 2
        
        score += max(0, exp_score) * self.scoring_weights['years_experience']
        
        # Age factor (optimal range 25-40)
        if 25 <= age <= 35:
            age_score = 100
        elif 36 <= age <= 45:
            age_score = 85
        elif 22 <= age <= 24:
            age_score = 75
        elif 46 <= age <= 55:
            age_score = 70
        else:
            age_score = 50  # Very young or older candidates
        
        score += age_score * self.scoring_weights['age_factor']
        
        # Location premium
        location = candidate.get('location', 'other').lower().replace(' ', '_')
        location_multiplier = self.location_premiums.get(location, 1.0)
        location_score = 80 * location_multiplier
        score += location_score * self.scoring_weights['location_premium']
        
        # Previous salary indicator (higher salary = higher perceived value)
        prev_salary = candidate.get('previous_salary', 50000)
        salary_score = min(100, (prev_salary / 150000) * 100)
        score += salary_score * self.scoring_weights['previous_salary']
        
        return score
    
    def assess_communication_skills(self, candidate: Dict[str, Any]) -> float:
        """Assess communication skills based on profile data."""
        score = 50  # Base score
        
        # Native English speaker bonus
        if candidate.get('native_english_speaker', False):
            score += 20
        
        # Education level affects communication score
        education = candidate.get('education_level', 'high_school').lower()
        if education in ['phd', 'masters', 'bachelors']:
            score += 15
        
        # Previous roles in customer-facing positions
        previous_roles = candidate.get('previous_roles', [])
        customer_facing_roles = ['sales', 'customer service', 'marketing', 'consultant']
        
        for role in previous_roles:
            if any(cf_role in role.lower() for cf_role in customer_facing_roles):
                score += 10
                break
        
        # Writing samples quality (if available)
        writing_quality = candidate.get('writing_sample_score', None)
        if writing_quality:
            score += writing_quality * 0.3
        
        return min(100, score)
    
    def evaluate_cultural_fit(self, candidate: Dict[str, Any], company_culture: Dict[str, Any]) -> float:
        """Evaluate how well candidate fits company culture."""
        fit_score = 50  # Base score
        
        # Age and culture fit (younger teams prefer younger candidates)
        candidate_age = candidate.get('age', 30)
        team_avg_age = company_culture.get('average_team_age', 32)
        
        age_diff = abs(candidate_age - team_avg_age)
        if age_diff <= 5:
            fit_score += 20
        elif age_diff <= 10:
            fit_score += 10
        else:
            fit_score -= 10
        
        # Education background similarity
        candidate_education = candidate.get('education_level', '').lower()
        team_education_preference = company_culture.get('education_preference', 'bachelors').lower()
        
        if candidate_education == team_education_preference:
            fit_score += 15
        elif candidate_education in ['phd', 'masters'] and team_education_preference in ['bachelors', 'masters']:
            fit_score += 10
        
        # Industry background alignment
        candidate_industry = candidate.get('previous_industry', '').lower()
        company_industry = company_culture.get('industry', '').lower()
        
        if candidate_industry == company_industry:
            fit_score += 20
        
        # Work style preferences
        candidate_remote_pref = candidate.get('prefers_remote_work', False)
        company_remote_friendly = company_culture.get('remote_friendly', True)
        
        if candidate_remote_pref == company_remote_friendly:
            fit_score += 10
        
        return min(100, max(0, fit_score))
    
    def calculate_final_score(self, candidate: Dict[str, Any], 
                             company_culture: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate final candidate score with all factors."""
        base_score = self.calculate_base_score(candidate)
        
        # Communication assessment
        comm_score = self.assess_communication_skills(candidate)
        final_score = base_score + (comm_score * self.scoring_weights['communication_score'])
        
        # Cultural fit assessment
        if company_culture:
            culture_score = self.evaluate_cultural_fit(candidate, company_culture)
            final_score += culture_score * self.scoring_weights['cultural_fit']
        
        # Normalize to 0-100 scale
        final_score = min(100, max(0, final_score))
        
        return {
            'final_score': round(final_score, 2),
            'base_score': round(base_score, 2),
            'communication_score': round(comm_score, 2),
            'cultural_fit_score': round(culture_score, 2) if company_culture else None,
            'score_breakdown': {
                'education': round(self.education_scores.get(
                    candidate.get('education_level', 'high_school').lower(), 30
                ) * self.scoring_weights['education_level'], 2),
                'experience': round(base_score * 0.2, 2),  # Approximate
                'age_factor': round(base_score * 0.15, 2),  # Approximate
                'location': round(base_score * 0.15, 2),   # Approximate
                'salary_history': round(base_score * 0.1, 2)  # Approximate
            }
        }


class JobRecommendationEngine:
    """Generates personalized job recommendations for candidates."""
    
    def __init__(self):
        self.scorer = CandidateScorer()
        
        # Engagement optimization factors
        self.engagement_weights = {
            'salary_appeal': 0.3,
            'location_convenience': 0.25,
            'career_progression': 0.2,
            'company_prestige': 0.15,
            'job_security': 0.1
        }
    
    def analyze_user_preferences(self, candidate: Dict[str, Any], 
                               interaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user behavior to infer preferences."""
        preferences = {
            'preferred_salary_range': None,
            'location_flexibility': 'low',
            'industry_preferences': [],
            'company_size_preference': None,
            'remote_work_interest': False
        }
        
        # Infer salary expectations from profile and interactions
        current_salary = candidate.get('previous_salary', 50000)
        
        # Assume people want 10-30% salary increase
        min_expected = current_salary * 1.1
        max_expected = current_salary * 1.5
        
        # Adjust based on age and experience
        age = candidate.get('age', 30)
        if age < 30:
            max_expected = current_salary * 1.8  # Young people expect bigger jumps
        elif age > 45:
            max_expected = current_salary * 1.2  # Older workers more conservative
        
        preferences['preferred_salary_range'] = (min_expected, max_expected)
        
        # Analyze clicked jobs to infer preferences
        if interaction_history:
            clicked_companies = []
            clicked_locations = []
            clicked_industries = []
            
            for interaction in interaction_history:
                if interaction.get('action') in ['click', 'apply', 'save']:
                    job = interaction.get('job_data', {})
                    clicked_companies.append(job.get('company_size', 'medium'))
                    clicked_locations.append(job.get('location', ''))
                    clicked_industries.append(job.get('industry', ''))
            
            # Determine company size preference
            if clicked_companies:
                size_counts = {}
                for size in clicked_companies:
                    size_counts[size] = size_counts.get(size, 0) + 1
                preferences['company_size_preference'] = max(size_counts, key=size_counts.get)
            
            # Industry preferences
            if clicked_industries:
                industry_counts = {}
                for industry in clicked_industries:
                    industry_counts[industry] = industry_counts.get(industry, 0) + 1
                
                # Top 3 industries
                sorted_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)
                preferences['industry_preferences'] = [ind[0] for ind in sorted_industries[:3]]
        
        return preferences
    
    def score_job_appeal(self, job: Dict[str, Any], candidate: Dict[str, Any], 
                        preferences: Dict[str, Any]) -> float:
        """Score how appealing a job is to a specific candidate."""
        appeal_score = 0.0
        
        # Salary appeal
        job_salary = job.get('salary', 75000)
        preferred_range = preferences.get('preferred_salary_range', (50000, 100000))
        
        if preferred_range[0] <= job_salary <= preferred_range[1]:
            salary_appeal = 100
        elif job_salary > preferred_range[1]:
            salary_appeal = 80  # Higher is still appealing
        else:
            # Below expectations
            salary_ratio = job_salary / preferred_range[0]
            salary_appeal = salary_ratio * 60
        
        appeal_score += salary_appeal * self.engagement_weights['salary_appeal']
        
        # Location convenience
        candidate_location = candidate.get('location', '').lower()
        job_location = job.get('location', '').lower()
        
        if candidate_location == job_location:
            location_score = 100
        elif job.get('remote_work_available', False):
            location_score = 90
        else:
            # Different location penalty
            location_score = 40
        
        appeal_score += location_score * self.engagement_weights['location_convenience']
        
        # Career progression appeal
        candidate_exp = candidate.get('years_experience', 0)
        job_level = job.get('seniority_level', 'mid')
        
        progression_score = 50
        if job_level == 'senior' and candidate_exp >= 5:
            progression_score = 90
        elif job_level == 'mid' and 2 <= candidate_exp <= 8:
            progression_score = 85
        elif job_level == 'junior' and candidate_exp <= 3:
            progression_score = 80
        elif job_level == 'executive' and candidate_exp >= 10:
            progression_score = 95
        
        appeal_score += progression_score * self.engagement_weights['career_progression']
        
        # Company prestige (based on size and industry)
        company_size = job.get('company_size', 'medium')
        industry = job.get('industry', '')
        
        prestige_score = 50
        if company_size == 'large':
            prestige_score += 20
        if industry.lower() in ['technology', 'finance', 'consulting']:
            prestige_score += 20
        
        appeal_score += prestige_score * self.engagement_weights['company_prestige']
        
        # Job security assessment
        industry_stability = {
            'technology': 85,
            'healthcare': 90,
            'education': 95,
            'government': 100,
            'retail': 60,
            'hospitality': 50
        }
        
        security_score = industry_stability.get(industry.lower(), 70)
        appeal_score += security_score * self.engagement_weights['job_security']
        
        return min(100, appeal_score)
    
    def generate_recommendations(self, candidate: Dict[str, Any], 
                               available_jobs: List[Dict[str, Any]],
                               interaction_history: List[Dict[str, Any]] = None,
                               num_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Generate personalized job recommendations."""
        if not interaction_history:
            interaction_history = []
        
        # Analyze user preferences
        preferences = self.analyze_user_preferences(candidate, interaction_history)
        
        # Score and rank jobs
        job_scores = []
        for job in available_jobs:
            # Calculate candidate fit for this job
            fit_score = self.scorer.calculate_final_score(
                candidate, 
                job.get('company_culture', {})
            )['final_score']
            
            # Calculate job appeal
            appeal_score = self.score_job_appeal(job, candidate, preferences)
            
            # Combined score (60% fit, 40% appeal for engagement)
            combined_score = (fit_score * 0.6) + (appeal_score * 0.4)
            
            job_scores.append({
                'job': job,
                'fit_score': fit_score,
                'appeal_score': appeal_score,
                'combined_score': combined_score,
                'recommendation_reasons': self._generate_reasons(
                    job, candidate, fit_score, appeal_score
                )
            })
        
        # Sort by combined score
        job_scores.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Apply diversity and fairness filters
        filtered_recommendations = self._apply_engagement_filters(
            job_scores[:num_recommendations * 2], candidate
        )
        
        return filtered_recommendations[:num_recommendations]
    
    def _generate_reasons(self, job: Dict[str, Any], candidate: Dict[str, Any], 
                         fit_score: float, appeal_score: float) -> List[str]:
        """Generate explanation for why this job was recommended."""
        reasons = []
        
        # Salary-based reasons
        job_salary = job.get('salary', 0)
        current_salary = candidate.get('previous_salary', 0)
        
        if job_salary > current_salary * 1.2:
            reasons.append(f"Significant salary increase potential ({job_salary:,})")
        elif job_salary > current_salary:
            reasons.append(f"Competitive salary offer ({job_salary:,})")
        
        # Experience match
        candidate_exp = candidate.get('years_experience', 0)
        if 'senior' in job.get('title', '').lower() and candidate_exp >= 5:
            reasons.append("Your experience qualifies you for senior roles")
        
        # Location benefits
        if job.get('remote_work_available', False):
            reasons.append("Remote work available")
        
        # Company appeal
        if job.get('company_size') == 'large':
            reasons.append("Established company with career growth opportunities")
        
        # Industry match
        candidate_industry = candidate.get('previous_industry', '').lower()
        job_industry = job.get('industry', '').lower()
        if candidate_industry == job_industry:
            reasons.append("Matches your industry background")
        
        return reasons[:3]  # Limit to top 3 reasons
    
    def _apply_engagement_filters(self, recommendations: List[Dict[str, Any]], 
                                candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to maximize user engagement."""
        filtered = []
        
        # Prioritize higher-paying jobs for engagement
        high_salary_jobs = [r for r in recommendations if r['job'].get('salary', 0) > 80000]
        medium_salary_jobs = [r for r in recommendations if 50000 <= r['job'].get('salary', 0) <= 80000]
        
        # Mix high and medium salary jobs for better engagement
        filtered.extend(high_salary_jobs[:7])
        filtered.extend(medium_salary_jobs[:3])
        
        # If not enough, add from remaining
        if len(filtered) < len(recommendations):
            remaining = [r for r in recommendations if r not in filtered]
            filtered.extend(remaining[:len(recommendations) - len(filtered)])
        
        return filtered


# Demo data and usage example
def create_sample_data():
    """Create sample candidate and job data for demonstration."""
    
    candidates = [
        {
            'id': 1,
            'name': 'John Smith',
            'age': 28,
            'education_level': 'bachelors',
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'San Francisco',
            'previous_industry': 'technology',
            'native_english_speaker': True,
            'previous_roles': ['software engineer', 'developer'],
            'prefers_remote_work': False
        },
        {
            'id': 2,
            'name': 'Maria Garcia',
            'age': 45,
            'education_level': 'masters',
            'years_experience': 15,
            'previous_salary': 95000,
            'location': 'Phoenix',
            'previous_industry': 'education',
            'native_english_speaker': False,
            'previous_roles': ['teacher', 'curriculum developer'],
            'prefers_remote_work': True
        },
        {
            'id': 3,
            'name': 'Kevin Wang',
            'age': 24,
            'education_level': 'bootcamp',
            'years_experience': 2,
            'previous_salary': 55000,
            'location': 'Austin',
            'previous_industry': 'technology',
            'native_english_speaker': True,
            'previous_roles': ['junior developer', 'intern'],
            'prefers_remote_work': True
        }
    ]
    
    jobs = [
        {
            'id': 1,
            'title': 'Senior Software Engineer',
            'company': 'TechCorp',
            'salary': 120000,
            'location': 'San Francisco',
            'industry': 'technology',
            'company_size': 'large',
            'seniority_level': 'senior',
            'remote_work_available': False,
            'company_culture': {
                'average_team_age': 30,
                'education_preference': 'bachelors',
                'industry': 'technology',
                'remote_friendly': False
            }
        },
        {
            'id': 2,
            'title': 'Product Manager',
            'company': 'StartupInc',
            'salary': 110000,
            'location': 'Austin',
            'industry': 'technology',
            'company_size': 'medium',
            'seniority_level': 'mid',
            'remote_work_available': True,
            'company_culture': {
                'average_team_age': 28,
                'education_preference': 'masters',
                'industry': 'technology',
                'remote_friendly': True
            }
        }
    ]
    
    return candidates, jobs


if __name__ == "__main__":
    # Demonstration of the system
    candidates, jobs = create_sample_data()
    
    scorer = CandidateScorer()
    recommender = JobRecommendationEngine()
    
    print("=== Candidate Scoring Demo ===")
    for candidate in candidates:
        score_result = scorer.calculate_final_score(candidate)
        print(f"\nCandidate: {candidate['name']}")
        print(f"Final Score: {score_result['final_score']}")
        print(f"Score Breakdown: {score_result['score_breakdown']}")
    
    print("\n=== Job Recommendation Demo ===")
    for candidate in candidates[:1]:  # Just first candidate for demo
        recommendations = recommender.generate_recommendations(candidate, jobs)
        print(f"\nRecommendations for {candidate['name']}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['job']['title']} at {rec['job']['company']}")
            print(f"   Combined Score: {rec['combined_score']:.1f}")
            print(f"   Reasons: {', '.join(rec['recommendation_reasons'])}")