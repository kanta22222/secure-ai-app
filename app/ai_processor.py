import re
from collections import Counter

def summarize_text(text: str, max_sentences: int = 3) -> str:
    # Improved extractive summarizer: pick sentences with highest word frequency score
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return ""
    # Simple TF-IDF like scoring: word frequency in sentence vs overall
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    total_words = len(words)
    scored_sentences = []
    for sent in sentences:
        sent_words = re.findall(r'\b\w+\b', sent.lower())
        score = sum(word_freq[w] / total_words for w in sent_words if w in word_freq)
        scored_sentences.append((score, sent))
    # Sort by score descending
    scored_sentences.sort(reverse=True)
    selected = [s for _, s in scored_sentences[:max_sentences]]
    # Preserve original order
    ordered = [s for s in sentences if s in selected]
    return " ".join(ordered).strip()

def extract_keywords(text: str, num_keywords: int = 10) -> list:
    # Extract top keywords using frequency
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove stop words (simple list)
    stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'])
    filtered = [w for w in words if w not in stop_words and len(w) > 2]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(num_keywords)]

def analyze_sentiment(text: str) -> str:
    # Simple sentiment analysis based on positive/negative words
    positive_words = set(['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'happy', 'joy', 'positive'])
    negative_words = set(['bad', 'terrible', 'awful', 'hate', 'worst', 'sad', 'angry', 'negative', 'poor', 'horrible'])
    words = re.findall(r'\b\w+\b', text.lower())
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"
