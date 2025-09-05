import re
import logging
from typing import List, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    keywords: List[str]
    case_sensitive: bool = False
    whole_word_only: bool = True
    description: str = ""

ALERT_RULES = [
    AlertRule(
        keywords=["Cloudwalk", "CloudWalk", "CLOUDWALK", "cloudwalk"],
        case_sensitive=False,
        whole_word_only=True,
        description="Cloudwalk enterprise mention"
    )
]

def sanitize_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    return text[:5000]

def check_keyword_match(text: str, rule: AlertRule) -> bool:
    try:
        clean_text = sanitize_text(text)
        if not clean_text:
            return False
            
        for keyword in rule.keywords:
            if not keyword:
                continue
                
            search_text = clean_text if rule.case_sensitive else clean_text.lower()
            search_keyword = keyword if rule.case_sensitive else keyword.lower()
            
            if rule.whole_word_only:
                pattern = r'\b' + re.escape(search_keyword) + r'\b'
                if re.search(pattern, search_text):
                    logger.info(f"Alert triggered by keyword: {keyword}")
                    return True
            else:
                if search_keyword in search_text:
                    logger.info(f"Alert triggered by keyword: {keyword}")
                    return True
                    
        return False
        
    except Exception as e:
        logger.error(f"Error checking keyword match: {e}")
        return False

def check_alerts(text: str) -> bool:
    try:
        if not text or not isinstance(text, str):
            return False
            
        for rule in ALERT_RULES:
            if check_keyword_match(text, rule):
                logger.warning(f"Alert rule triggered: {rule.description}")
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Error in check_alerts: {e}")
        return False

def get_matched_keywords(text: str) -> Set[str]:
    matched = set()
    
    try:
        clean_text = sanitize_text(text)
        if not clean_text:
            return matched
            
        for rule in ALERT_RULES:
            for keyword in rule.keywords:
                if not keyword:
                    continue
                    
                search_text = clean_text if rule.case_sensitive else clean_text.lower()
                search_keyword = keyword if rule.case_sensitive else keyword.lower()
                
                if rule.whole_word_only:
                    pattern = r'\b' + re.escape(search_keyword) + r'\b'
                    if re.search(pattern, search_text):
                        matched.add(keyword)
                else:
                    if search_keyword in search_text:
                        matched.add(keyword)
                        
    except Exception as e:
        logger.error(f"Error getting matched keywords: {e}")
        
    return matched