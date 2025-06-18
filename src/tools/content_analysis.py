"""
Content analysis tools for readability, SEO, and quality assessment.
"""

import re
from typing import Dict, Any, List
from textstat import flesch_reading_ease, flesch_kincaid_grade


async def analyze_readability(content: str) -> Dict[str, Any]:
    """
    Analyze content readability using standard metrics.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dictionary with readability scores and recommendations
    """
    try:
        flesch_score = flesch_reading_ease(content)
        grade_level = flesch_kincaid_grade(content)
        
        # Determine readability level
        if flesch_score >= 90:
            level = "Very Easy"
            target_audience = "5th grade and below"
        elif flesch_score >= 80:
            level = "Easy"
            target_audience = "6th grade"
        elif flesch_score >= 70:
            level = "Fairly Easy"
            target_audience = "7th grade"
        elif flesch_score >= 60:
            level = "Standard"
            target_audience = "8th-9th grade"
        elif flesch_score >= 50:
            level = "Fairly Difficult"
            target_audience = "10th-12th grade"
        elif flesch_score >= 30:
            level = "Difficult"
            target_audience = "College level"
        else:
            level = "Very Difficult"
            target_audience = "Graduate level"
        
        # Calculate additional metrics
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        avg_sentence_length = words / max(1, sentences)
        
        # Generate recommendations
        recommendations = _get_readability_recommendations(flesch_score, avg_sentence_length)
        
        return {
            "flesch_score": round(flesch_score, 1),
            "grade_level": round(grade_level, 1),
            "readability_level": level,
            "target_audience": target_audience,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "total_words": words,
            "total_sentences": sentences,
            "recommendations": recommendations
        }
        
    except Exception as e:
        # Fallback to simple analysis
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        avg_sentence_length = words / max(1, sentences)
        
        return {
            "flesch_score": 65.0,  # Reasonable default
            "grade_level": 8.0,
            "readability_level": "Standard",
            "target_audience": "8th-9th grade",
            "avg_sentence_length": round(avg_sentence_length, 1),
            "total_words": words,
            "total_sentences": sentences,
            "recommendations": ["Could not perform detailed readability analysis"]
        }


def _get_readability_recommendations(flesch_score: float, avg_sentence_length: float) -> List[str]:
    """Generate readability improvement recommendations."""
    recommendations = []
    
    if flesch_score < 60:
        recommendations.extend([
            "Use shorter sentences to improve readability",
            "Replace complex words with simpler alternatives",
            "Add more transitional phrases between ideas"
        ])
    
    if flesch_score < 40:
        recommendations.extend([
            "Break up long paragraphs into smaller chunks",
            "Use bullet points for complex information",
            "Consider using more contractions (don't, won't, etc.)"
        ])
    
    if avg_sentence_length > 20:
        recommendations.append("Average sentence length is high - consider breaking up long sentences")
    
    if avg_sentence_length < 8:
        recommendations.append("Sentences may be too short - consider combining some for better flow")
    
    if not recommendations:
        recommendations.append("Readability is good - maintain current writing style")
    
    return recommendations


async def check_keyword_density(content: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Check keyword density and optimization in content.
    
    Args:
        content: Text content to analyze
        keywords: List of target keywords
        
    Returns:
        Dictionary with keyword density analysis and recommendations
    """
    content_lower = content.lower()
    word_count = len(content.split())
    
    if word_count == 0:
        return {"error": "No content to analyze"}
    
    keyword_analysis = {}
    total_keyword_density = 0
    
    for keyword in keywords:
        # Count exact matches and partial matches
        exact_count = content_lower.count(keyword.lower())
        
        # Also count individual words in multi-word keywords
        keyword_words = keyword.lower().split()
        word_counts = [content_lower.count(word) for word in keyword_words]
        
        density = (exact_count / word_count) * 100
        total_keyword_density += density
        
        # Assess density appropriateness (1-3% is generally good)
        if density < 0.5:
            status = "too_low"
            recommendation = "Consider using this keyword more frequently"
        elif density > 3.0:
            status = "too_high"
            recommendation = "Reduce usage to avoid keyword stuffing"
        else:
            status = "optimal"
            recommendation = "Keyword density is well-optimized"
        
        keyword_analysis[keyword] = {
            "exact_count": exact_count,
            "density_percentage": round(density, 2),
            "status": status,
            "recommendation": recommendation,
            "word_counts": dict(zip(keyword_words, word_counts)) if len(keyword_words) > 1 else {}
        }
    
    return {
        "total_words": word_count,
        "keyword_analysis": keyword_analysis,
        "total_keyword_density": round(total_keyword_density, 2),
        "overall_assessment": _assess_overall_keyword_optimization(total_keyword_density, len(keywords))
    }


def _assess_overall_keyword_optimization(total_density: float, keyword_count: int) -> str:
    """Assess overall keyword optimization."""
    avg_density = total_density / max(1, keyword_count)
    
    if avg_density < 0.5:
        return "Under-optimized - consider increasing keyword usage"
    elif avg_density > 4.0:
        return "Over-optimized - risk of keyword stuffing"
    else:
        return "Well-optimized keyword usage"


async def generate_meta_description(content: str, keywords: List[str] = None, max_length: int = 160) -> str:
    """
    Generate SEO-optimized meta description from content.
    
    Args:
        content: Full content text
        keywords: Optional list of keywords to include
        max_length: Maximum length for meta description
        
    Returns:
        Generated meta description
    """
    # Extract first paragraph or first few sentences
    paragraphs = content.split('\n\n')
    first_paragraph = paragraphs[0] if paragraphs else content
    
    # If first paragraph is too long, use first few sentences
    if len(first_paragraph) > max_length:
        sentences = [s.strip() for s in first_paragraph.split('.') if s.strip()]
        meta = sentences[0]
        
        # Add more sentences if they fit
        for sentence in sentences[1:]:
            if len(meta + '. ' + sentence) < max_length - 3:  # Leave room for "..."
                meta += '. ' + sentence
            else:
                break
    else:
        meta = first_paragraph
    
    # Try to include primary keyword if provided and not already present
    if keywords and keywords[0].lower() not in meta.lower():
        # Try to prepend keyword
        keyword_prefix = f"{keywords[0]}: "
        if len(keyword_prefix + meta) <= max_length:
            meta = keyword_prefix + meta
        else:
            # Try to work it in naturally
            meta = meta[:max_length - len(keywords[0]) - 10] + f" about {keywords[0]}"
    
    # Ensure it's under the max length
    if len(meta) > max_length:
        meta = meta[:max_length - 3] + "..."
    
    # Clean up any formatting issues
    meta = re.sub(r'\s+', ' ', meta.strip())
    
    return meta


async def estimate_reading_time(content: str, words_per_minute: int = 225) -> Dict[str, Any]:
    """
    Estimate reading time for content.
    
    Args:
        content: Text content to analyze
        words_per_minute: Average reading speed (default: 225 WPM)
        
    Returns:
        Dictionary with reading time estimates
    """
    word_count = len(content.split())
    
    # Calculate reading time in minutes
    reading_time_minutes = word_count / words_per_minute
    
    # Convert to human-readable format
    if reading_time_minutes < 1:
        reading_time_text = "Less than 1 minute"
    elif reading_time_minutes < 2:
        reading_time_text = "1 minute"
    else:
        reading_time_text = f"{round(reading_time_minutes)} minutes"
    
    return {
        "word_count": word_count,
        "reading_time_minutes": round(reading_time_minutes, 1),
        "reading_time_text": reading_time_text,
        "words_per_minute": words_per_minute
    }


async def analyze_content_structure(content: str) -> Dict[str, Any]:
    """
    Analyze content structure and organization.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dictionary with structure analysis
    """
    lines = content.split('\n')
    
    # Find headings (lines that are short and/or start with #)
    headings = []
    for line in lines:
        line = line.strip()
        if line.startswith('#') or (len(line) < 100 and len(line.split()) < 12 and line.endswith(':')):
            headings.append(line)
    
    # Count paragraphs (non-empty lines separated by empty lines)
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    
    # Find lists (lines starting with -, *, or numbers)
    list_items = []
    for line in lines:
        line = line.strip()
        if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
            list_items.append(line)
    
    # Calculate average paragraph length
    paragraph_lengths = [len(p.split()) for p in paragraphs]
    avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    
    return {
        "heading_count": len(headings),
        "headings": headings[:5],  # First 5 headings
        "paragraph_count": len(paragraphs),
        "avg_paragraph_length": round(avg_paragraph_length, 1),
        "list_item_count": len(list_items),
        "has_good_structure": len(headings) >= 3 and avg_paragraph_length < 100,
        "structure_recommendations": _get_structure_recommendations(
            len(headings), avg_paragraph_length, len(list_items), len(paragraphs)
        )
    }


def _get_structure_recommendations(heading_count: int, avg_paragraph_length: float, 
                                 list_count: int, paragraph_count: int) -> List[str]:
    """Generate content structure recommendations."""
    recommendations = []
    
    if heading_count < 3:
        recommendations.append("Add more headings to break up content and improve scannability")
    
    if avg_paragraph_length > 100:
        recommendations.append("Break up long paragraphs into shorter, more digestible chunks")
    
    if list_count == 0 and paragraph_count > 5:
        recommendations.append("Consider using bullet points or numbered lists for key information")
    
    if heading_count > paragraph_count:
        recommendations.append("Consider combining some sections or adding more content under headings")
    
    if not recommendations:
        recommendations.append("Content structure looks good - well-organized and scannable")
    
    return recommendations