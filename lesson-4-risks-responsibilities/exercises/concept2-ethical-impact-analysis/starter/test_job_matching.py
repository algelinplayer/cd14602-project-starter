"""
Test suite for Job Matching and Candidate Scoring System
========================================================

These tests demonstrate the algorithmic behavior and may reveal
bias patterns in scoring and recommendation logic.
"""

import pytest
from job_matching import CandidateScorer, JobRecommendationEngine, create_sample_data


class TestCandidateScoring:
    """Test cases for candidate scoring algorithms."""
    
    @pytest.fixture
    def scorer(self):
        return CandidateScorer()
    
    def test_basic_scoring_functionality(self, scorer):
        """Test that scoring produces reasonable results."""
        candidate = {
            'age': 30,
            'education_level': 'bachelors',
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'San Francisco',
            'native_english_speaker': True
        }
        
        result = scorer.calculate_final_score(candidate)
        
        assert 'final_score' in result
        assert 0 <= result['final_score'] <= 100
        assert 'score_breakdown' in result
    
    def test_education_level_impact(self, scorer):
        """Test how education level affects scoring."""
        base_candidate = {
            'age': 30,
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'San Francisco',
            'native_english_speaker': True
        }
        
        # Test different education levels
        phd_candidate = {**base_candidate, 'education_level': 'phd'}
        bachelors_candidate = {**base_candidate, 'education_level': 'bachelors'}
        high_school_candidate = {**base_candidate, 'education_level': 'high_school'}
        bootcamp_candidate = {**base_candidate, 'education_level': 'bootcamp'}
        
        phd_score = scorer.calculate_final_score(phd_candidate)['final_score']
        bachelors_score = scorer.calculate_final_score(bachelors_candidate)['final_score']
        high_school_score = scorer.calculate_final_score(high_school_candidate)['final_score']
        bootcamp_score = scorer.calculate_final_score(bootcamp_candidate)['final_score']
        
        # Higher education should generally score higher
        assert phd_score > bachelors_score
        assert bachelors_score > high_school_score
        
        # This test may reveal bias against non-traditional education
        print(f"Education scoring bias test:")
        print(f"PhD: {phd_score}, Bachelors: {bachelors_score}")
        print(f"High School: {high_school_score}, Bootcamp: {bootcamp_score}")
    
    def test_age_bias_detection(self, scorer):
        """Test for age-related bias in scoring."""
        base_candidate = {
            'education_level': 'bachelors',
            'years_experience': 8,
            'previous_salary': 75000,
            'location': 'San Francisco',
            'native_english_speaker': True
        }
        
        # Test candidates of different ages with same qualifications
        ages_and_scores = []
        for age in [22, 28, 35, 42, 50, 58]:
            candidate = {**base_candidate, 'age': age}
            score = scorer.calculate_final_score(candidate)['final_score']
            ages_and_scores.append((age, score))
            print(f"Age {age}: Score {score}")
        
        # Analyze age bias patterns
        scores = [score for age, score in ages_and_scores]
        max_score = max(scores)
        min_score = min(scores)
        
        # This test may reveal age discrimination
        assert max_score - min_score < 30, "Significant age bias detected"
    
    def test_gender_proxy_bias(self, scorer):
        """Test for potential gender bias through proxy variables."""
        # Create profiles that might correlate with gender
        
        # Profile potentially correlating with female candidates
        profile_a = {
            'age': 35,
            'education_level': 'masters',
            'years_experience': 8,
            'previous_salary': 65000,  # Potentially lower due to wage gap
            'location': 'Atlanta',
            'previous_industry': 'education',
            'native_english_speaker': True,
            'previous_roles': ['teacher', 'curriculum developer']
        }
        
        # Profile potentially correlating with male candidates
        profile_b = {
            'age': 35,
            'education_level': 'bachelors',
            'years_experience': 8,
            'previous_salary': 85000,
            'location': 'San Francisco',
            'previous_industry': 'technology',
            'native_english_speaker': True,
            'previous_roles': ['software engineer', 'team lead']
        }
        
        score_a = scorer.calculate_final_score(profile_a)['final_score']
        score_b = scorer.calculate_final_score(profile_b)['final_score']
        
        print(f"Profile A (education background): {score_a}")
        print(f"Profile B (tech background): {score_b}")
        
        # Should we be concerned about this difference?
        # This test highlights potential indirect gender bias
    
    def test_location_bias(self, scorer):
        """Test for geographic/location bias."""
        base_candidate = {
            'age': 30,
            'education_level': 'bachelors',
            'years_experience': 5,
            'previous_salary': 75000,
            'native_english_speaker': True
        }
        
        locations_and_scores = []
        locations = ['San Francisco', 'New York', 'Austin', 'Detroit', 'rural_areas']
        
        for location in locations:
            candidate = {**base_candidate, 'location': location}
            score = scorer.calculate_final_score(candidate)['final_score']
            locations_and_scores.append((location, score))
            print(f"Location {location}: Score {score}")
        
        # This test may reveal location bias favoring expensive cities
        scores = [score for location, score in locations_and_scores]
        max_score = max(scores)
        min_score = min(scores)
        
        print(f"Location scoring range: {min_score} to {max_score}")
    
    def test_language_bias(self, scorer):
        """Test for bias against non-native English speakers."""
        base_candidate = {
            'age': 30,
            'education_level': 'masters',
            'years_experience': 8,
            'previous_salary': 75000,
            'location': 'Austin',
            'previous_roles': ['software engineer']
        }
        
        native_speaker = {**base_candidate, 'native_english_speaker': True}
        non_native_speaker = {**base_candidate, 'native_english_speaker': False}
        
        native_score = scorer.calculate_final_score(native_speaker)['final_score']
        non_native_score = scorer.calculate_final_score(non_native_speaker)['final_score']
        
        print(f"Native English speaker: {native_score}")
        print(f"Non-native English speaker: {non_native_score}")
        
        # This test may reveal language bias
        score_difference = native_score - non_native_score
        print(f"Score difference: {score_difference}")


class TestJobRecommendations:
    """Test cases for job recommendation algorithms."""
    
    @pytest.fixture
    def recommender(self):
        return JobRecommendationEngine()
    
    @pytest.fixture
    def sample_data(self):
        return create_sample_data()
    
    def test_recommendation_functionality(self, recommender, sample_data):
        """Test basic recommendation functionality."""
        candidates, jobs = sample_data
        candidate = candidates[0]
        
        recommendations = recommender.generate_recommendations(candidate, jobs)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= len(jobs)
        
        for rec in recommendations:
            assert 'job' in rec
            assert 'combined_score' in rec
            assert 'recommendation_reasons' in rec
    
    def test_salary_bias_in_recommendations(self, recommender, sample_data):
        """Test if recommendations are biased toward higher salaries."""
        candidates, jobs = sample_data
        
        # Create jobs with different salary levels
        high_salary_job = {
            'id': 10,
            'title': 'High Pay Job',
            'salary': 150000,
            'location': 'San Francisco',
            'industry': 'technology',
            'company_size': 'large',
            'seniority_level': 'senior'
        }
        
        medium_salary_job = {
            'id': 11,
            'title': 'Medium Pay Job',
            'salary': 80000,
            'location': 'San Francisco',
            'industry': 'technology',
            'company_size': 'medium',
            'seniority_level': 'mid'
        }
        
        test_jobs = [high_salary_job, medium_salary_job]
        
        for candidate in candidates:
            recommendations = recommender.generate_recommendations(candidate, test_jobs)
            
            print(f"\nRecommendations for {candidate.get('name', 'candidate')}:")
            for rec in recommendations:
                job = rec['job']
                print(f"  {job['title']}: Salary ${job['salary']:,}, Score: {rec['combined_score']:.1f}")
            
            # Check if higher salary always ranks higher
            if len(recommendations) >= 2:
                high_sal_rec = next((r for r in recommendations if r['job']['id'] == 10), None)
                med_sal_rec = next((r for r in recommendations if r['job']['id'] == 11), None)
                
                if high_sal_rec and med_sal_rec:
                    print(f"  High salary score: {high_sal_rec['combined_score']}")
                    print(f"  Medium salary score: {med_sal_rec['combined_score']}")
    
    def test_demographic_recommendation_differences(self, recommender, sample_data):
        """Test if similar candidates from different demographics get different recommendations."""
        candidates, jobs = sample_data
        
        # Compare recommendations for candidates with similar qualifications but different demographics
        young_candidate = candidates[2]  # Kevin Wang, 24, bootcamp
        experienced_candidate = candidates[1]  # Maria Garcia, 45, masters
        
        young_recs = recommender.generate_recommendations(young_candidate, jobs)
        experienced_recs = recommender.generate_recommendations(experienced_candidate, jobs)
        
        print(f"\nYoung candidate ({young_candidate['name']}) recommendations:")
        for rec in young_recs:
            print(f"  {rec['job']['title']}: Score {rec['combined_score']:.1f}")
            print(f"    Reasons: {rec['recommendation_reasons']}")
        
        print(f"\nExperienced candidate ({experienced_candidate['name']}) recommendations:")
        for rec in experienced_recs:
            print(f"  {rec['job']['title']}: Score {rec['combined_score']:.1f}")
            print(f"    Reasons: {rec['recommendation_reasons']}")
        
        # Analyze if there are systematic differences
        young_avg_score = sum(r['combined_score'] for r in young_recs) / len(young_recs) if young_recs else 0
        exp_avg_score = sum(r['combined_score'] for r in experienced_recs) / len(experienced_recs) if experienced_recs else 0
        
        print(f"\nAverage scores - Young: {young_avg_score:.1f}, Experienced: {exp_avg_score:.1f}")
    
    def test_transparency_and_explainability(self, recommender, sample_data):
        """Test the quality and fairness of recommendation explanations."""
        candidates, jobs = sample_data
        candidate = candidates[0]
        
        recommendations = recommender.generate_recommendations(candidate, jobs)
        
        print(f"\nRecommendation explanations for {candidate['name']}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['job']['title']}")
            print(f"   Reasons: {rec['recommendation_reasons']}")
            
            # Check if reasons are meaningful and non-discriminatory
            reasons = rec['recommendation_reasons']
            
            # Flag potentially problematic reasons
            problematic_keywords = ['age', 'young', 'older', 'native speaker', 'cultural fit']
            for reason in reasons:
                for keyword in problematic_keywords:
                    if keyword.lower() in reason.lower():
                        print(f"   ⚠️  Potentially problematic reason: '{reason}'")


class TestFairnessAndBias:
    """Specific tests for fairness and bias detection."""
    
    @pytest.fixture
    def scorer(self):
        return CandidateScorer()
    
    def test_education_discrimination(self, scorer):
        """Test for discrimination against non-traditional education paths."""
        traditional_candidate = {
            'age': 28,
            'education_level': 'bachelors',
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'Austin',
            'native_english_speaker': True
        }
        
        bootcamp_candidate = {
            'age': 28,
            'education_level': 'bootcamp',
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'Austin',
            'native_english_speaker': True
        }
        
        self_taught_candidate = {
            'age': 28,
            'education_level': 'self_taught',
            'years_experience': 5,
            'previous_salary': 75000,
            'location': 'Austin',
            'native_english_speaker': True
        }
        
        traditional_score = scorer.calculate_final_score(traditional_candidate)['final_score']
        bootcamp_score = scorer.calculate_final_score(bootcamp_candidate)['final_score']
        self_taught_score = scorer.calculate_final_score(self_taught_candidate)['final_score']
        
        print(f"Traditional education: {traditional_score}")
        print(f"Bootcamp education: {bootcamp_score}")
        print(f"Self-taught: {self_taught_score}")
        
        # This test reveals the scoring bias against non-traditional education
        assert traditional_score > bootcamp_score
        assert traditional_score > self_taught_score
        
        # The question is: Is this fair and legally defensible?
    
    def test_salary_history_bias(self, scorer):
        """Test how previous salary affects scoring (potential source of pay gap perpetuation)."""
        base_candidate = {
            'age': 30,
            'education_level': 'bachelors',
            'years_experience': 6,
            'location': 'Austin',
            'native_english_speaker': True
        }
        
        high_salary_candidate = {**base_candidate, 'previous_salary': 100000}
        low_salary_candidate = {**base_candidate, 'previous_salary': 50000}
        
        high_score = scorer.calculate_final_score(high_salary_candidate)['final_score']
        low_score = scorer.calculate_final_score(low_salary_candidate)['final_score']
        
        print(f"High previous salary: {high_score}")
        print(f"Low previous salary: {low_score}")
        
        # This test reveals how salary history affects scoring
        # Could perpetuate existing pay gaps
        score_difference = high_score - low_score
        print(f"Salary bias impact: {score_difference} points")
    
    def test_intersectional_bias(self, scorer):
        """Test for intersectional bias affecting multiple protected characteristics."""
        
        # Candidate with multiple potentially disadvantaged characteristics
        intersectional_candidate = {
            'age': 50,  # Older worker
            'education_level': 'high_school',  # Lower education
            'years_experience': 20,  # High experience but older
            'previous_salary': 45000,  # Lower salary
            'location': 'Detroit',  # Lower-premium location
            'native_english_speaker': False,  # Language minority
            'previous_industry': 'retail'  # Lower-prestige industry
        }
        
        # Candidate with advantaged characteristics
        privileged_candidate = {
            'age': 28,  # Optimal age range
            'education_level': 'masters',  # High education
            'years_experience': 5,  # Good experience for age
            'previous_salary': 95000,  # High salary
            'location': 'San Francisco',  # Premium location
            'native_english_speaker': True,  # Native speaker
            'previous_industry': 'technology'  # High-prestige industry
        }
        
        intersectional_score = scorer.calculate_final_score(intersectional_candidate)['final_score']
        privileged_score = scorer.calculate_final_score(privileged_candidate)['final_score']
        
        print(f"Intersectional candidate score: {intersectional_score}")
        print(f"Privileged candidate score: {privileged_score}")
        print(f"Score gap: {privileged_score - intersectional_score}")
        
        # This test reveals the cumulative impact of multiple bias factors
        # The large score gap suggests systemic bias in the algorithm


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])