from typing import Dict, Any, List
import re
import logging
import traceback

logger = logging.getLogger(__name__)

class PriorityService:
    """Service for determining email priority"""
    
    def __init__(self):
        # Define priority keywords and their weights with expanded vocabulary
        self.priority_keywords = {
            "urgent": [
                # Direct urgency indicators
                "immediately", "urgent", "critical", "emergency", "asap", "right now",
                "cannot access", "system down", "broken", "urgently", "desperately",
                "help needed now", "urgent assistance", "critical issue", "emergency support",
                # System failures
                "outage", "downtime", "crash", "failure", "not working", "unresponsive",
                "error", "bug", "glitch", "malfunction", "broken", "unusable",
                # Business impact
                "losing money", "revenue impact", "business critical", "production issue",
                "blocking", "showstopper", "blocker", "preventing", "unable to",
                # Security concerns
                "security breach", "unauthorized access", "compromised", "hacked",
                "data leak", "vulnerability", "exposed", "threat", "attack",
                # Customer impact
                "customer complaint", "angry customer", "customer escalation",
                "refund request", "cancellation", "chargeback"
            ],
            "high": [
                # Important but not critical
                "important", "priority", "high priority", "urgent matter", "time sensitive",
                "deadline", "due date", "meeting", "appointment", "schedule",
                "urgent request", "high importance", "urgent inquiry", "urgent question",
                # Performance issues
                "slow", "performance", "laggy", "delayed", "timeout", "hanging",
                # Business processes
                "workflow blocked", "process issue", "approval needed", "sign-off required",
                # Financial matters
                "invoice", "payment", "billing", "subscription", "renewal",
                # Customer retention
                "unhappy", "dissatisfied", "frustrated", "disappointed"
            ],
            "normal": [
                # Standard inquiries
                "question", "inquiry", "request", "help", "support", "information",
                "general", "regular", "standard", "normal", "usual", "routine",
                # Feature requests
                "feature request", "enhancement", "improvement", "suggestion",
                # Documentation
                "documentation", "instructions", "guide", "manual", "how to",
                # Account management
                "account", "profile", "settings", "preferences", "configuration"
            ],
            "low": [
                # Explicitly low priority
                "when convenient", "no rush", "low priority", "not urgent", "take your time",
                "when possible", "low importance", "minor", "trivial", "non-urgent",
                # Informational
                "fyi", "for your information", "just letting you know", "update", "newsletter",
                # Feedback
                "feedback", "thoughts", "opinion", "survey", "questionnaire",
                # General inquiries
                "wondering", "curious", "interested in", "considering"
            ]
        }
        
        # Define business impact indicators with expanded categories
        self.business_impact_indicators = {
            "high": [
                # Financial impact
                "revenue", "customer", "client", "business", "sales", "money", "payment",
                "profit", "loss", "financial", "income", "earnings", "budget", "fiscal",
                # Customer impact
                "customer satisfaction", "client relationship", "account", "contract",
                "enterprise", "partner", "stakeholder", "investor", "shareholder",
                # Brand impact
                "reputation", "brand", "image", "public relations", "pr", "media",
                # Legal/compliance
                "legal", "compliance", "regulation", "law", "policy", "requirement",
                "gdpr", "hipaa", "pci", "sox", "audit", "security", "breach"
            ],
            "medium": [
                # Operational impact
                "process", "workflow", "efficiency", "productivity", "team",
                "operation", "procedure", "function", "performance", "service",
                # Internal systems
                "internal", "system", "tool", "application", "platform", "software",
                "database", "server", "network", "infrastructure", "integration",
                # Team productivity
                "team", "department", "division", "group", "staff", "employee",
                "colleague", "coworker", "manager", "supervisor", "director"
            ],
            "low": [
                # Individual impact
                "personal", "general", "information", "question", "curiosity",
                "individual", "single user", "one person", "myself", "me", "my",
                # Informational
                "fyi", "update", "newsletter", "announcement", "notification",
                "bulletin", "memo", "notice", "advisory", "communication",
                # Feedback
                "feedback", "suggestion", "idea", "thought", "opinion", "comment",
                "review", "rating", "evaluation", "assessment", "appraisal"
            ]
        }
        
        # Define time sensitivity patterns with expanded regex patterns
        self.time_patterns = {
            "urgent": [
                # Immediate timeframes
                r"today", r"tonight", r"within \d+ hours?", r"asap", r"immediately",
                r"right now", r"urgently", r"emergency", r"critical",
                # Specific urgent timeframes
                r"\bnow\b", r"\binstantly\b", r"\bimmediately\b", r"\bpromptly\b",
                r"\bas soon as\b", r"\bwithout delay\b", r"\bstraight away\b",
                r"\bin the next hour\b", r"\bwithin the hour\b", r"\bby noon\b", r"\bby \d+(?:am|pm)\b",
                # Deadlines today
                r"\bdeadline today\b", r"\bdue today\b", r"\bby end of day\b", r"\bby EOD\b",
                r"\bby close of business\b", r"\bby COB\b", r"\bbefore \d+(?:am|pm) today\b",
                # Emergency situations
                r"\bemergency\b", r"\bcrisis\b", r"\bcritical situation\b", r"\btime-critical\b"
            ],
            "high": [
                # Near-term timeframes
                r"this week", r"within \d+ days?", r"soon", r"quickly", r"promptly",
                # Specific high-priority timeframes
                r"\btomorrow\b", r"\bnext day\b", r"\bin \d+ days?\b", r"\bwithin \d+ days?\b",
                r"\bby (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
                r"\bthis (week|month)\b", r"\bby the end of (this|the) week\b",
                # Upcoming deadlines
                r"\bupcoming deadline\b", r"\bdue soon\b", r"\bdue date\b", r"\bdue by\b",
                r"\bscheduled for\b", r"\btime-sensitive\b", r"\bpressing\b"
            ],
            "normal": [
                # Standard timeframes
                r"when possible", r"at your convenience", r"no rush",
                # Specific normal timeframes
                r"\bnext week\b", r"\bin the coming weeks?\b", r"\bwithin \d+ weeks?\b",
                r"\bnext month\b", r"\bin the near future\b", r"\beventually\b",
                # Flexible timing
                r"\bwhen you have time\b", r"\bat your earliest convenience\b",
                r"\bwhen you get a chance\b", r"\bwhen you're free\b"
            ],
            "low": [
                # Extended timeframes
                r"\bno deadline\b", r"\bno hurry\b", r"\bno rush\b", r"\btake your time\b",
                r"\bwhenever\b", r"\bat your leisure\b", r"\bwhen convenient\b",
                # Future timeframes
                r"\bin the future\b", r"\beventually\b", r"\bsomeday\b", r"\blater\b",
                r"\bin \d+ months?\b", r"\bnext quarter\b", r"\bnext year\b"
            ]
        }
    
    def determine_priority(self, subject: str, body: str, sender: str = None) -> Dict[str, Any]:
        """
        Determine the priority of an email based on content analysis
        
        Args:
            subject (str): Email subject line
            body (str): Email body content
            sender (str): Sender email address
            
        Returns:
            Dict containing priority analysis results
        """
        try:
            # Handle edge cases
            if not subject and not body:
                return {
                    "priority": "normal",
                    "score": 0.5,
                    "confidence": 0.4,
                    "method": "default",
                    "reasoning": "Empty email content"
                }
            
            # Combine subject and body for analysis with subject having higher weight (3x)
            full_text = f"{subject} {subject} {subject} {body}".lower()
            
            # Store original values for reference
            self._subject = subject
            self._body = body[:500] if body else ""  # Store truncated body for reference
            self._sender = sender
            
            # Analyze keyword presence
            keyword_scores = self._analyze_keywords(full_text)
            
            # Analyze business impact
            business_impact = self._analyze_business_impact(full_text)
            
            # Analyze time sensitivity
            time_sensitivity = self._analyze_time_sensitivity(full_text)
            
            # Analyze sender importance (if available)
            sender_priority = self._analyze_sender_priority(sender) if sender else 0
            
            # Calculate overall priority score
            priority_score = self._calculate_priority_score(
                keyword_scores, business_impact, time_sensitivity, sender_priority
            )
            
            # Determine priority level
            priority_level = self._map_priority_level(priority_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                keyword_scores, business_impact, time_sensitivity
            )
            self._confidence = confidence  # Store for reasoning generation
            
            # Prepare detailed result with all analysis components
            result = {
                "priority": priority_level,
                "score": priority_score,
                "confidence": confidence,
                "factors": {
                    "keyword_scores": keyword_scores,
                    "business_impact": business_impact,
                    "time_sensitivity": time_sensitivity,
                    "sender_priority": sender_priority
                },
                "reasoning": self._generate_priority_reasoning(
                    keyword_scores, business_impact, time_sensitivity, priority_level
                ),
                "analysis": {
                    "keyword_analysis": {
                        "scores": {k: round(v, 2) for k, v in keyword_scores.items() if v > 0},
                    },
                    "business_impact": {
                        "scores": {k: round(v, 2) for k, v in business_impact.items() if v > 0},
                    },
                    "time_sensitivity": {
                        "scores": {k: round(v, 2) for k, v in time_sensitivity.items() if v > 0},
                    },
                    "sender_priority": round(sender_priority, 2)
                }
            }
            
            # Add matched examples if available
            if hasattr(self, '_last_keyword_matches'):
                result["analysis"]["keyword_analysis"]["matches"] = {
                    k: v[:3] for k, v in self._last_keyword_matches.items() if v
                }
            
            if hasattr(self, '_last_business_matches'):
                 result["analysis"]["business_impact"]["matches"] = {
                     k: v[:3] for k, v in self._last_business_matches.items() if v
                 }
                
            if hasattr(self, '_last_time_matches'):
                result["analysis"]["time_sensitivity"]["matches"] = {
                    k: v[:3] for k, v in self._last_time_matches.items() if v
                }
            
            if hasattr(self, '_sender_priority_reason'):
                result["analysis"]["sender_reason"] = self._sender_priority_reason
                
            # Add factor weights if available
            if hasattr(self, '_factor_weights'):
                result["analysis"]["factor_weights"] = self._factor_weights
            
            return result
            
        except Exception as e:
            logger.error(f"Error in priority determination: {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            # Fallback to simpler determination if analysis fails
            fallback_result = self._fallback_priority_determination(subject, body)
            # Add error information
            fallback_result["error"] = str(e)
            return fallback_result
    
    def _analyze_keywords(self, text: str) -> Dict[str, float]:
        """Analyze presence of priority keywords with improved matching"""
        scores = {}
        matches = {}
        
        for priority_level, keywords in self.priority_keywords.items():
            score = 0
            keyword_matches = []
            
            for keyword in keywords:
                # Check for exact matches
                if keyword in text:
                    score += 1
                    keyword_matches.append(keyword)
                # Check for partial matches for multi-word keywords
                elif len(keyword.split()) > 1:
                    # For phrases, check if most words are present
                    words = keyword.split()
                    matched_words = sum(1 for word in words if f" {word} " in f" {text} ")
                    if matched_words >= len(words) * 0.75:  # 75% of words match
                        score += 0.75
                        keyword_matches.append(f"{keyword} (partial)")
            
            # Apply positional weighting - subject line matches are more important
            subject_end = min(100, len(text))  # Assume first ~100 chars are subject
            subject_text = text[:subject_end]
            subject_matches = sum(1 for k in keyword_matches if k in subject_text)
            
            # Boost score for subject line matches
            if subject_matches > 0:
                score += subject_matches * 0.5
            
            # Store matched keywords for reasoning
            matches[priority_level] = keyword_matches[:5]  # Store top 5 matches
            
            # Normalize score
            max_possible = len(keywords)
            scores[priority_level] = min(1.0, score / max_possible if max_possible > 0 else 0)
        
        # Store matches for reasoning
        self._last_keyword_matches = matches
        
        return scores
    
    def _analyze_business_impact(self, text: str) -> Dict[str, float]:
        """Analyze business impact indicators with improved matching"""
        scores = {}
        matches = {}
        
        for impact_level, indicators in self.business_impact_indicators.items():
            score = 0
            impact_matches = []
            
            for indicator in indicators:
                # Check for exact matches
                if indicator in text:
                    score += 1
                    impact_matches.append(indicator)
                # Check for partial matches for multi-word indicators
                elif len(indicator.split()) > 1:
                    words = indicator.split()
                    matched_words = sum(1 for word in words if f" {word} " in f" {text} ")
                    if matched_words >= len(words) * 0.75:  # 75% of words match
                        score += 0.75
                        impact_matches.append(f"{indicator} (partial)")
            
            # Apply contextual weighting - indicators near urgent keywords have higher impact
            for urgent_keyword in self.priority_keywords["urgent"]:
                if urgent_keyword in text and any(im in text.split(urgent_keyword)[0][-50:] or 
                                               im in text.split(urgent_keyword)[1][:50] 
                                               for im in impact_matches):
                    score += 0.5
            
            # Store matched indicators for reasoning
            matches[impact_level] = impact_matches[:5]  # Store top 5 matches
            
            # Normalize score
            max_possible = len(indicators)
            scores[impact_level] = min(1.0, score / max_possible if max_possible > 0 else 0)
        
        # Store matches for reasoning
        self._last_impact_matches = matches
        
        return scores
    
    def _analyze_time_sensitivity(self, text: str) -> Dict[str, float]:
        """Analyze time sensitivity patterns with improved regex matching"""
        scores = {}
        matches = {}
        
        for time_level, patterns in self.time_patterns.items():
            score = 0
            time_matches = []
            
            for pattern in patterns:
                regex_matches = re.findall(pattern, text)
                if regex_matches:
                    score += len(regex_matches)
                    # Add unique matches to our list
                    for match in regex_matches[:3]:  # Limit to 3 matches per pattern
                        match_text = match if isinstance(match, str) else match[0]
                        time_matches.append(match_text)
            
            # Apply positional weighting - time indicators at the beginning or end are more important
            # (often indicates deadlines in email openings or closings)
            beginning = text[:200]  # First 200 chars
            ending = text[-200:]    # Last 200 chars
            
            beginning_matches = sum(1 for tm in time_matches if tm in beginning)
            ending_matches = sum(1 for tm in time_matches if tm in ending)
            
            # Boost score for strategically placed time indicators
            if beginning_matches > 0 or ending_matches > 0:
                score += (beginning_matches + ending_matches) * 0.3
            
            # Store matched time patterns for reasoning
            matches[time_level] = time_matches[:5]  # Store top 5 matches
            
            # Normalize score with a more realistic cap
            # Most emails won't have more than 5 time indicators of the same level
            scores[time_level] = min(1.0, score / 5.0)
        
        # Store matches for reasoning
        self._last_time_matches = matches
        
        return scores
    
    def _analyze_sender_priority(self, sender: str) -> float:
        """Analyze sender priority based on email domain/role with improved recognition"""
        if not sender:
            return 0.0
        
        sender_lower = sender.lower()
        self._sender_priority_reason = ""
        
        # VIP/Executive senders (highest priority)
        executive_indicators = ["ceo", "cto", "cfo", "coo", "president", "vp", "vice president", 
                              "director", "head", "chief", "founder", "owner", "board"]
        if any(role in sender_lower for role in executive_indicators):
            self._sender_priority_reason = "Executive/VIP sender"
            return 0.9
        
        # Management senders (high priority)
        management_indicators = ["manager", "supervisor", "lead", "principal", "senior", "team lead"]
        if any(role in sender_lower for role in management_indicators):
            self._sender_priority_reason = "Management sender"
            return 0.8
        
        # Support/Customer-related senders (medium-high priority)
        support_indicators = ["support", "help", "customer", "client", "service", "account manager"]
        if any(role in sender_lower for role in support_indicators):
            self._sender_priority_reason = "Support/Customer-related sender"
            return 0.7
        
        # Domain-based priority
        email_parts = sender_lower.split('@')
        if len(email_parts) > 1:
            domain = email_parts[1]
            
            # Check for important domains
            important_domains = [".gov", ".edu", ".org", "enterprise", "corporate"]
            if any(d in domain for d in important_domains):
                self._sender_priority_reason = "Important domain sender"
                return 0.65
        
        # Automated/System senders (low priority)
        automated_indicators = ["noreply", "donotreply", "no-reply", "do-not-reply", "system", 
                              "automated", "notification", "alert", "info@", "newsletter"]
        if any(term in sender_lower for term in automated_indicators):
            self._sender_priority_reason = "Automated/System sender"
            return 0.2
        
        # Default priority for unknown senders
        self._sender_priority_reason = "Standard sender"
        return 0.5
    
    def _calculate_priority_score(self, keyword_scores: Dict, business_impact: Dict, 
                                time_sensitivity: Dict, sender_priority: float) -> float:
        """Calculate overall priority score with adaptive weighting"""
        # Store factor scores for reasoning
        self._factor_scores = {}
        
        # Calculate individual factor scores
        keyword_score = (
            keyword_scores.get("urgent", 0) * 1.0 +
            keyword_scores.get("high", 0) * 0.7 +
            keyword_scores.get("normal", 0) * 0.4 +
            keyword_scores.get("low", 0) * 0.1
        )
        self._factor_scores["keyword"] = round(keyword_score, 2)
        
        business_score = (
            business_impact.get("high", 0) * 1.0 +
            business_impact.get("medium", 0) * 0.6 +
            business_impact.get("low", 0) * 0.2
        )
        self._factor_scores["business"] = round(business_score, 2)
        
        time_score = (
            time_sensitivity.get("urgent", 0) * 1.0 +
            time_sensitivity.get("high", 0) * 0.7 +
            time_sensitivity.get("normal", 0) * 0.4 +
            time_sensitivity.get("low", 0) * 0.1
        )
        self._factor_scores["time"] = round(time_score, 2)
        
        self._factor_scores["sender"] = round(sender_priority, 2)
        
        # Adaptive weighting based on signal strength
        # If any factor has a very strong signal, increase its weight
        base_weights = {
            "keyword": 0.35,
            "business": 0.25,
            "time": 0.25,
            "sender": 0.15
        }
        
        # Adjust weights based on signal strength
        weights = base_weights.copy()
        
        # Strong urgency signals get higher weight
        if keyword_scores.get("urgent", 0) > 0.7 or time_sensitivity.get("urgent", 0) > 0.7:
            # Boost urgency factors
            boost = 0.1
            weights["keyword"] += boost * 0.5
            weights["time"] += boost * 0.5
            # Reduce other weights proportionally
            weights["business"] -= boost * 0.3
            weights["sender"] -= boost * 0.2
        
        # Strong business impact gets higher weight
        elif business_impact.get("high", 0) > 0.7:
            # Boost business impact
            boost = 0.1
            weights["business"] += boost
            # Reduce other weights proportionally
            weights["keyword"] -= boost * 0.4
            weights["time"] -= boost * 0.4
            weights["sender"] -= boost * 0.2
        
        # VIP senders get higher weight
        elif sender_priority > 0.8:
            # Boost sender priority
            boost = 0.1
            weights["sender"] += boost
            # Reduce other weights proportionally
            weights["keyword"] -= boost * 0.4
            weights["business"] -= boost * 0.3
            weights["time"] -= boost * 0.3
        
        # Store final weights for reasoning
        self._factor_weights = {k: round(v, 2) for k, v in weights.items()}
        
        # Calculate final score with adaptive weights
        final_score = (
            keyword_score * weights["keyword"] +
            business_score * weights["business"] +
            time_score * weights["time"] +
            sender_priority * weights["sender"]
        )
        
        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, final_score))
    
    def _map_priority_level(self, score: float) -> str:
        """Map priority score to priority level with more nuanced thresholds"""
        # Store the raw score for reasoning
        self._priority_score = round(score, 2)
        
        # More nuanced thresholds with slight adjustments
        if score >= 0.85:  # Very high threshold for urgent
            return "urgent"
        elif score >= 0.65:  # Slightly higher threshold for high
            return "high"
        elif score >= 0.35:  # Slightly lower threshold for normal
            return "normal"
        else:
            return "low"
    
    def _calculate_confidence(self, keyword_scores: Dict, business_impact: Dict, 
                            time_sensitivity: Dict) -> float:
        """Calculate confidence in priority determination with improved algorithm"""
        # Store max scores for reasoning
        self._max_scores = {}
        
        # Get maximum score for each factor
        max_keyword = max(keyword_scores.values()) if keyword_scores else 0
        max_business = max(business_impact.values()) if business_impact else 0
        max_time = max(time_sensitivity.values()) if time_sensitivity else 0
        
        self._max_scores["keyword"] = round(max_keyword, 2)
        self._max_scores["business"] = round(max_business, 2)
        self._max_scores["time"] = round(max_time, 2)
        
        # Calculate agreement between factors
        # Find the priority level with the highest score for each factor
        keyword_level = max(keyword_scores.items(), key=lambda x: x[1])[0] if keyword_scores else None
        business_level = None
        if business_impact:
            # Map business impact levels to priority levels
            business_map = {"high": "urgent", "medium": "high", "low": "normal"}
            business_level = business_map.get(max(business_impact.items(), key=lambda x: x[1])[0])
        
        time_level = max(time_sensitivity.items(), key=lambda x: x[1])[0] if time_sensitivity else None
        
        # Count how many factors agree on the same priority level
        levels = [l for l in [keyword_level, business_level, time_level] if l]
        level_counts = {}
        for level in levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Find the most common level
        most_common_level = max(level_counts.items(), key=lambda x: x[1])[0] if level_counts else None
        agreement_count = level_counts.get(most_common_level, 0) if most_common_level else 0
        
        # Base confidence on signal strength and agreement
        base_confidence = (max_keyword + max_business + max_time) / 3
        
        # Boost confidence based on agreement between factors
        agreement_boost = 0
        if agreement_count == 3:  # All factors agree
            agreement_boost = 0.3
        elif agreement_count == 2:  # Two factors agree
            agreement_boost = 0.15
        
        # Boost confidence if multiple strong signals exist
        strong_signals = sum(1 for score in [max_keyword, max_business, max_time] if score > 0.7)
        signal_boost = min(0.2, strong_signals * 0.1)
        
        # Calculate final confidence
        confidence = base_confidence + agreement_boost + signal_boost
        
        # Store reasoning factors
        self._confidence_factors = {
            "base": round(base_confidence, 2),
            "agreement": round(agreement_boost, 2),
            "strong_signals": round(signal_boost, 2)
        }
        
        return min(1.0, confidence)
    
    def _generate_priority_reasoning(self, keyword_scores: Dict, business_impact: Dict, 
                                   time_sensitivity: Dict, priority_level: str) -> str:
        """Generate detailed human-readable reasoning for priority level"""
        reasons = []
        detailed_reasons = []
        
        # Add priority level explanation
        priority_explanation = f"Email classified as {priority_level.upper()} priority"
        reasons.append(priority_explanation)
        
        # Add keyword-based reasoning with specific examples
        if hasattr(self, '_last_keyword_matches'):
            for level, matches in self._last_keyword_matches.items():
                if matches and keyword_scores.get(level, 0) > 0.3:
                    level_name = level.capitalize()
                    examples = '", "'.join(matches[:3])  # Show up to 3 examples
                    if examples:
                        detailed_reasons.append(f"{level_name} priority keywords detected: \"{examples}\"")
        
        # Add business impact reasoning with specific examples
        if hasattr(self, '_last_business_matches'):
            for level, matches in self._last_business_matches.items():
                if matches and business_impact.get(level, 0) > 0.3:
                    level_name = level.capitalize()
                    examples = '", "'.join(matches[:3])  # Show up to 3 examples
                    if examples:
                        detailed_reasons.append(f"{level_name} business impact indicators: \"{examples}\"")
        
        # Add time sensitivity reasoning with specific examples
        if hasattr(self, '_last_time_matches'):
            for level, matches in self._last_time_matches.items():
                if matches and time_sensitivity.get(level, 0) > 0.3:
                    level_name = level.capitalize()
                    examples = '", "'.join(matches[:3])  # Show up to 3 examples
                    if examples:
                        detailed_reasons.append(f"{level_name} time sensitivity indicators: \"{examples}\"")
        
        # Add sender priority reasoning
        if hasattr(self, '_sender_priority_reason') and self._sender_priority_reason:
            detailed_reasons.append(f"Sender analysis: {self._sender_priority_reason}")
        
        # Add factor scores if available
        if hasattr(self, '_factor_scores') and self._factor_scores:
            scores_str = []
            for factor, score in self._factor_scores.items():
                if score > 0.3:  # Only include significant factors
                    scores_str.append(f"{factor.capitalize()}: {score}")
            if scores_str:
                detailed_reasons.append(f"Factor scores: {', '.join(scores_str)}")
        
        # Add factor weights if available
        if hasattr(self, '_factor_weights') and self._factor_weights:
            # Only include this for high or urgent priorities
            if priority_level in ['high', 'urgent']:
                weights_str = []
                for factor, weight in self._factor_weights.items():
                    if weight > 0.2:  # Only include significant weights
                        weights_str.append(f"{factor.capitalize()}: {weight}")
                if weights_str:
                    detailed_reasons.append(f"Analysis weights: {', '.join(weights_str)}")
        
        # Add confidence information if available
        if hasattr(self, '_confidence_factors') and hasattr(self, '_confidence'):
            confidence_pct = int(self._confidence * 100)
            detailed_reasons.append(f"Confidence: {confidence_pct}%")
        
        # Combine all reasons
        if detailed_reasons:
            reasons.extend(detailed_reasons)
        else:
            reasons.append("Standard priority based on content analysis")
        
        return "; ".join(reasons)
    
    def _fallback_priority_determination(self, subject: str, body: str) -> Dict[str, Any]:
        """Enhanced fallback priority determination when analysis fails"""
        # Combine subject and body, but give subject higher weight by duplicating it
        text = f"{subject} {subject} {body}".lower()
        
        # More comprehensive keyword lists for fallback
        urgent_words = [
            "urgent", "critical", "emergency", "asap", "immediately", "right now",
            "escalate", "escalation", "outage", "down", "broken", "crash", "failed",
            "security breach", "breach", "hack", "attack", "virus", "malware",
            "deadline today", "deadline tomorrow", "by end of day", "by eod"
        ]
        
        high_words = [
            "important", "priority", "help", "support", "issue", "problem", "error",
            "bug", "defect", "failure", "not working", "doesn't work", "fix", "resolve",
            "attention", "review", "approve", "approval", "sign-off", "signoff"
        ]
        
        normal_words = [
            "update", "status", "information", "inform", "notification", "fyi",
            "question", "inquiry", "request", "assistance", "guidance", "advice",
            "feedback", "suggestion", "recommendation", "follow-up", "followup"
        ]
        
        # Count exact matches
        urgent_exact = sum(1 for word in urgent_words if word in text)
        high_exact = sum(1 for word in high_words if word in text)
        normal_exact = sum(1 for word in normal_words if word in text)
        
        # Count partial matches (for multi-word phrases)
        urgent_partial = sum(1 for word in urgent_words if any(w in word for w in text.split()))
        high_partial = sum(1 for word in high_words if any(w in word for w in text.split()))
        normal_partial = sum(1 for word in normal_words if any(w in word for w in text.split()))
        
        # Calculate weighted scores
        urgent_score = urgent_exact * 1.0 + urgent_partial * 0.5
        high_score = high_exact * 1.0 + high_partial * 0.5
        normal_score = normal_exact * 1.0 + normal_partial * 0.5
        
        # Check for subject-specific indicators (higher weight)
        subject_lower = subject.lower()
        if any(word in subject_lower for word in urgent_words):
            urgent_score += 2.0
        if any(word in subject_lower for word in high_words):
            high_score += 1.5
        
        # Determine priority based on scores
        matched_words = []
        if urgent_score > 0:
            matched_words.extend([word for word in urgent_words if word in text][:3])
        if high_score > 0:
            matched_words.extend([word for word in high_words if word in text][:3])
        if normal_score > 0:
            matched_words.extend([word for word in normal_words if word in text][:3])
        
        # Determine priority level
        if urgent_score >= 2.0:
            priority = "urgent"
            score = min(0.9, 0.7 + (urgent_score * 0.05))
            confidence = min(0.8, 0.6 + (urgent_score * 0.03))
        elif urgent_score > 0 or high_score >= 2.0:
            priority = "high"
            score = min(0.8, 0.6 + (high_score * 0.04))
            confidence = min(0.7, 0.5 + (high_score * 0.03))
        elif high_score > 0 or normal_score >= 3.0:
            priority = "normal"
            score = min(0.6, 0.4 + (normal_score * 0.03))
            confidence = min(0.6, 0.4 + (normal_score * 0.02))
        else:
            priority = "low"
            score = 0.3
            confidence = 0.5
        
        # Generate reasoning with matched keywords
        reasoning = "Fallback priority determination used"
        if matched_words:
            keywords_str = '", "'.join(matched_words[:5])  # Show up to 5 matched keywords
            reasoning = f"Fallback analysis detected keywords: \"{keywords_str}\""
        
        return {
            "priority": priority,
            "score": score,
            "confidence": confidence,
            "method": "fallback",
            "reasoning": reasoning
        }
    
    def batch_determine_priority(self, emails: List[Dict], include_analysis: bool = False) -> List[Dict]:
        """Determine priority for multiple emails with enhanced batch processing
        
        Args:
            emails: List of email dictionaries with subject, body, and sender fields
            include_analysis: Whether to include detailed analysis in results (default: False)
            
        Returns:
            List of priority determination results
        """
        results = []
        errors = []
        
        # Process emails in batch
        for i, email in enumerate(emails):
            try:
                # Extract email fields with fallbacks
                subject = email.get("subject", "")
                body = email.get("body", "")
                sender = email.get("sender", "")
                email_id = email.get("id", str(i))
                
                # Determine priority
                result = self.determine_priority(subject, body, sender)
                
                # Add email identifier to result
                result["email_id"] = email_id
                
                # Remove detailed analysis if not requested
                if not include_analysis and "analysis" in result:
                    del result["analysis"]
                
                results.append(result)
                
            except Exception as e:
                # Log error and continue with next email
                logger.error(f"Error processing email {i}: {str(e)}")
                errors.append({
                    "email_id": email.get("id", str(i)),
                    "error": str(e),
                    "index": i
                })
                
                # Add a default result for failed emails
                results.append({
                    "email_id": email.get("id", str(i)),
                    "priority": "normal",
                    "score": 0.5,
                    "confidence": 0.3,
                    "method": "error_fallback",
                    "reasoning": f"Error during processing: {str(e)[:100]}",
                    "error": str(e)
                })
        
        # Add batch processing metadata
        batch_result = {
            "results": results,
            "metadata": {
                "total": len(emails),
                "successful": len(emails) - len(errors),
                "failed": len(errors),
                "errors": errors if errors else None
            }
        }
        
        return batch_result
