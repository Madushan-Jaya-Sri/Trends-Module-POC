# Trending Score Methodology - Simplified Guide

## Overview
This document explains the Universal Trending Score (0-100) calculation methodology used to rank content across Google Trends, YouTube, and TikTok.

---

## Scoring Components & Weightages

The trending score is calculated using 5 key components, each with a specific weight:

| Component | Weight | Purpose |
|-----------|--------|---------|
| **Volume** | 30% | Measures reach and visibility |
| **Engagement** | 25% | Measures quality of interaction |
| **Velocity** | 20% | Measures speed of growth |
| **Recency** | 15% | Measures time relevance |
| **Cross-Platform** | 10% | Measures multi-platform presence |

**Total:** 100%

---

## 1. VOLUME SCORE (30% Weight)

### What It Measures
Total reach and visibility - how many people have been exposed to the trend

### Why 30% Weight?
- **Highest weight** because volume is the primary indicator of trend magnitude
- More people engaged = stronger trend
- Foundation metric that all other metrics build upon

### Formulas by Platform

**Google Trends:**
```
Volume Score = Search Volume × 100
```

**YouTube:**
```
Volume Score = View Count
```

**TikTok:**
- Hashtag: `Volume Score = View Count`
- Creator: `Volume Score = Follower Count × 10`
- Sound/Video: `Volume Score = View Count`

### Example
- Google Trends: 50,000 searches → 5,000,000 volume score
- YouTube: 1,500,000 views → 1,500,000 volume score
- TikTok Creator: 500,000 followers → 5,000,000 volume score

---

## 2. ENGAGEMENT SCORE (25% Weight)

### What It Measures
Quality of user interaction - indicates genuine interest, not just passive viewing

### Why 25% Weight?
- **Second highest** because engagement shows active participation
- High engagement = genuine interest vs. passive consumption
- Distinguishes truly resonant content from merely visible content

### Formulas by Platform

**Google Trends:**
```
Engagement Score = Increase Percentage
(dynamically normalized to match other platforms)
```

**YouTube:**
```
Engagement Rate = (Likes + Comments) / Views × 100
Engagement Score = Engagement Rate × 1,000
```

**TikTok:**
- Hashtag: `Engagement Score = (Video Count / View Count) × 1,000,000`
- Creator: `Engagement Score = (Total Likes / Followers) × 100`
- Sound/Video: `Engagement Score = (100 - Rank) × 10`

### Example
- YouTube: 1M views, 30K likes, 5K comments
  - ER = (30,000 + 5,000) / 1,000,000 × 100 = 3.5%
  - Score = 3.5 × 1,000 = 3,500

---

## 3. VELOCITY SCORE (20% Weight)

### What It Measures
Speed of growth and viral potential

### Why 20% Weight?
- **Critical for identifying emerging trends** before they peak
- Fast growth = viral potential and breaking phenomena
- Balances historical volume with forward momentum

### Formulas by Platform

**Google Trends:**
```
Base Velocity = Increase Percentage × 30
Active Multiplier = 1.5 (if currently active) or 1.0 (if not)
Viral Multiplier = 1.2 (if increase ≥ 1000%) or 1.0

Velocity Score = Base × Active Multiplier × Viral Multiplier
```

**YouTube:**
```
Velocity Score = View Count / Hours Since Published
```

**TikTok:**
```
Growth Rate = Last Histogram Value - First Histogram Value
Velocity Score = Growth Rate × 100
```

### Example
- Google Trends: 1500% increase, active, viral
  - Base: 1500 × 30 = 45,000
  - Active: 45,000 × 1.5 = 67,500
  - Viral: 67,500 × 1.2 = 81,000

- YouTube: 1.2M views in 10 hours
  - Velocity: 1,200,000 / 10 = 120,000 views/hour

---

## 4. RECENCY SCORE (15% Weight)

### What It Measures
How recent the trend is using exponential decay

### Why 15% Weight?
- **Ensures prioritization of fresh content**
- Recent trends are more actionable for real-time decisions
- Lower than volume/engagement because older trends can still be relevant
- Exponential decay prevents abrupt cutoffs

### Universal Formula

```
Recency Score = 100 × (0.5)^(Age in Hours / 24)
```

**Half-life:** 24 hours (score halves every day)

### Decay Schedule

| Content Age | Score |
|-------------|-------|
| 1 hour | 97.2 |
| 6 hours | 84.1 |
| 12 hours | 70.7 |
| 24 hours (1 day) | 50.0 |
| 48 hours (2 days) | 25.0 |
| 72 hours (3 days) | 12.5 |
| 1 week | 1.5 |

### Example
- Content published 12 hours ago:
  - Recency = 100 × (0.5)^(12/24) = 100 × 0.707 = 70.7

---

## 5. CROSS-PLATFORM SCORE (10% Weight)

### What It Measures
Presence across multiple platforms using fuzzy term matching

### Why 10% Weight?
- **Bonus for universal trends** that transcend single platforms
- Reduces platform-specific bias and noise
- Lowest weight because it's a validation metric, not a primary indicator
- Most trends exist on single platforms, this rewards exceptional ones

### Formula

```
If found on 1 platform: Score = 0
If found on 2 platforms: Score = 50
If found on 3+ platforms: Score = 100
```

### Matching Logic
- Extract key terms from trend titles/names
- Remove stop words ('the', 'a', 'and', etc.)
- Compare term overlap across platforms
- Match if overlap ≥ 30%

### Example

**Trend appearing on 2 platforms:**
- YouTube: "iPhone 15 Pro Max Review"
- TikTok: "iPhone 15 Pro Unboxing"
- Overlap: "iphone", "15", "pro" = 50% match
- **Score: 50**

**Trend appearing on 3 platforms:**
- Google Trends: "World Cup 2024"
- YouTube: "World Cup Highlights"
- TikTok: "World Cup Goals"
- **Score: 100**

---

## Platform-Specific Weight Adjustments

### Why Adaptive Weights?
Each platform has different strengths and data availability. Adaptive weights ensure fair comparison.

### Google Trends (Limited Metrics)

| Component | Weight | Justification |
|-----------|--------|---------------|
| Volume | **35%** ↑ | Increased - primary strength |
| Engagement | **15%** ↓ | Decreased - limited engagement data |
| Velocity | **30%** ↑ | Increased - search velocity is key strength |
| Recency | 15% | Standard |
| Cross-Platform | **5%** ↓ | Decreased - less relevant for searches |

**Rationale:** Google Trends excels at showing search volume and velocity, but lacks traditional engagement metrics.

### YouTube (Balanced Metrics)

| Component | Weight | Justification |
|-----------|--------|---------------|
| Volume | 30% | Standard - well-balanced |
| Engagement | 25% | Standard - good engagement data |
| Velocity | 20% | Standard - reliable growth metrics |
| Recency | 15% | Standard |
| Cross-Platform | 10% | Standard |

**Rationale:** YouTube provides comprehensive metrics across all dimensions.

### TikTok (Rich Engagement)

| Component | Weight | Justification |
|-----------|--------|---------------|
| Volume | **25%** ↓ | Decreased - less emphasis |
| Engagement | **30%** ↑ | Increased - platform's core strength |
| Velocity | 20% | Standard |
| Recency | 15% | Standard |
| Cross-Platform | 10% | Standard |

**Rationale:** TikTok is engagement-first platform with rich interaction data.

---

## Final Score Calculation

### Step 1: Calculate Raw Component Scores
Each component is calculated using platform-specific formulas

### Step 2: Normalize to 0-100 Scale
```
Normalized Score = ((Raw Score - Min Score) / (Max Score - Min Score)) × 100
```

Applied to: Volume, Engagement, Velocity
(Recency and Cross-Platform are already 0-100)

### Step 3: Apply Weighted Formula
```
Trending Score =
    (Weight_Volume × Volume_Score) +
    (Weight_Engagement × Engagement_Score) +
    (Weight_Velocity × Velocity_Score) +
    (Weight_Recency × Recency_Score) +
    (Weight_CrossPlatform × CrossPlatform_Score)
```

### Step 4: Round and Rank
- Round to 2 decimal places
- Sort descending (highest score first)

---

## Complete Example Scenario

### Scenario: Comparing 3 Trends

We have trending content across platforms. Let's calculate and compare their scores.

---

### **TREND A: "iPhone 15 Launch" (YouTube Video)**

**Raw Metrics:**
- Views: 2,000,000
- Likes: 80,000
- Comments: 15,000
- Published: 6 hours ago
- Found only on YouTube

**Component Calculations:**

1. **Volume:** 2,000,000 views
   - Normalized: 85.0 (out of 100)

2. **Engagement:**
   - ER = (80,000 + 15,000) / 2,000,000 × 100 = 4.75%
   - Score = 4.75 × 1,000 = 4,750
   - Normalized: 78.5

3. **Velocity:**
   - 2,000,000 / 6 = 333,333 views/hour
   - Normalized: 95.2

4. **Recency:**
   - 100 × (0.5)^(6/24) = 84.1

5. **Cross-Platform:**
   - Only on YouTube = 0

**Final Score (YouTube weights: 30%, 25%, 20%, 15%, 10%):**
```
Trending Score =
    (0.30 × 85.0) +    # Volume: 25.50
    (0.25 × 78.5) +    # Engagement: 19.63
    (0.20 × 95.2) +    # Velocity: 19.04
    (0.15 × 84.1) +    # Recency: 12.62
    (0.10 × 0)         # Cross-Platform: 0

= 25.50 + 19.63 + 19.04 + 12.62 + 0
= 76.79
```

**TREND A Score: 76.79**

---

### **TREND B: "Taylor Swift Concert" (Google Trends + YouTube)**

**Raw Metrics:**
- Google Trends: 150,000 searches, 800% increase, active
- YouTube: 1,500,000 views (from 24 hours ago)
- Cross-platform match confirmed

**Google Trends Component Calculations:**

1. **Volume:**
   - 150,000 × 100 = 15,000,000
   - Normalized: 92.3

2. **Engagement:**
   - 800% (will be dynamically normalized)
   - Normalized: 70.0

3. **Velocity:**
   - Base: 800 × 30 = 24,000
   - Active: 24,000 × 1.5 = 36,000
   - Normalized: 88.7

4. **Recency:**
   - 100 × (0.5)^(24/24) = 50.0

5. **Cross-Platform:**
   - On 2 platforms = 50

**Final Score (Google Trends weights: 35%, 15%, 30%, 15%, 5%):**
```
Trending Score =
    (0.35 × 92.3) +    # Volume: 32.31
    (0.15 × 70.0) +    # Engagement: 10.50
    (0.30 × 88.7) +    # Velocity: 26.61
    (0.15 × 50.0) +    # Recency: 7.50
    (0.05 × 50)        # Cross-Platform: 2.50

= 32.31 + 10.50 + 26.61 + 7.50 + 2.50
= 79.42
```

**TREND B Score: 79.42**

---

### **TREND C: "Viral Dance Challenge" (All 3 Platforms)**

**Raw Metrics:**
- Google Trends: 80,000 searches, 1200% increase, active, viral
- YouTube: 3,000,000 views (from 12 hours ago)
- TikTok Hashtag: 50M views, 10K videos
- Cross-platform on all 3

**YouTube Component Calculations:**

1. **Volume:**
   - 3,000,000 views
   - Normalized: 95.8

2. **Engagement:**
   - Assume 120,000 likes + 20,000 comments
   - ER = (140,000 / 3,000,000) × 100 = 4.67%
   - Score = 4.67 × 1,000 = 4,670
   - Normalized: 82.3

3. **Velocity:**
   - 3,000,000 / 12 = 250,000 views/hour
   - Normalized: 91.5

4. **Recency:**
   - 100 × (0.5)^(12/24) = 70.7

5. **Cross-Platform:**
   - On 3 platforms = 100

**Final Score (YouTube weights: 30%, 25%, 20%, 15%, 10%):**
```
Trending Score =
    (0.30 × 95.8) +    # Volume: 28.74
    (0.25 × 82.3) +    # Engagement: 20.58
    (0.20 × 91.5) +    # Velocity: 18.30
    (0.15 × 70.7) +    # Recency: 10.61
    (0.10 × 100)       # Cross-Platform: 10.00

= 28.74 + 20.58 + 18.30 + 10.61 + 10.00
= 88.23
```

**TREND C Score: 88.23**

---

## Final Rankings

| Rank | Trend | Platform | Score | Key Strengths |
|------|-------|----------|-------|---------------|
| 🥇 1 | Viral Dance Challenge | YouTube | **88.23** | High volume, cross-platform presence (100), strong velocity |
| 🥈 2 | Taylor Swift Concert | Google Trends | **79.42** | High velocity (88.7), strong volume (92.3), cross-platform (50) |
| 🥉 3 | iPhone 15 Launch | YouTube | **76.79** | Excellent velocity (95.2), very recent (84.1), high volume |

---

## Why This Ranking Makes Sense

### 1st Place: Viral Dance Challenge (88.23)
- **Strongest:** Cross-platform dominance (+10 points over others)
- **Volume leader:** Highest raw reach (3M views)
- **Universal appeal:** Present on all major platforms
- **Rightfully #1:** Truly viral, transcending platform boundaries

### 2nd Place: Taylor Swift Concert (79.42)
- **Strongest:** Velocity on Google Trends (88.7)
- **Good reach:** High search volume boosted 100×
- **Cross-platform:** On 2 platforms (+2.5 points)
- **Slightly older:** 24 hours reduces recency to 50.0

### 3rd Place: iPhone 15 Launch (76.79)
- **Strongest:** Velocity (95.2) and Recency (84.1)
- **Very fresh:** Only 6 hours old
- **Missing:** No cross-platform presence (0 points lost)
- **Single platform:** Limits overall trending status

---

## Key Insights from Example

### Weight Distribution Impact
- **10-point difference** between 1st and 3rd place
- Cross-platform presence worth up to **10 points** in final score
- Recency decay creates **significant differences** (84.1 vs 50.0 vs 70.7)

### Platform Strengths
- Google Trends: Best for catching **early velocity signals**
- YouTube: Best for **balanced, comprehensive metrics**
- TikTok: Best for **engagement-heavy content**

### Time Sensitivity
- Fresh content (6 hours) scores **34.1 points higher** on recency than day-old content
- Velocity matters more for **recent trends**
- Volume becomes dominant for **established trends**

---

## Summary

The Universal Trending Score provides a **scientifically-justified, transparent, and fair** method to compare trends across platforms by:

1. **Weighing dimensions appropriately** (Volume 30%, Engagement 25%, Velocity 20%, Recency 15%, Cross-Platform 10%)
2. **Adapting to platform strengths** (Google: velocity, TikTok: engagement)
3. **Normalizing different scales** (searches vs. views vs. followers)
4. **Rewarding universal trends** (cross-platform bonus)
5. **Prioritizing freshness** (exponential recency decay)

Result: A single 0-100 score that accurately reflects the overall "trendiness" of any content, regardless of source platform.
