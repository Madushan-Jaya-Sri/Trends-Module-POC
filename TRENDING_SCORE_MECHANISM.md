# Overall Trending Score Mechanism

## Overview
The system calculates a **Universal Trending Score (0-100)** for content across Google Trends, YouTube, and TikTok using a scientifically weighted scoring algorithm.

---

## System Architecture & Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA COLLECTION PHASE                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │Google Trends │  │   YouTube    │  │   TikTok     │
          │    Service   │  │   Service    │  │   Service    │
          └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    │   Fetch Data    │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATA NORMALIZATION PHASE                                │
│                   (TrendAggregatorService)                                   │
│                                                                              │
│  • Google Trends → Normalized format (search queries)                       │
│  • YouTube       → Normalized format (videos)                               │
│  • TikTok        → Normalized format (hashtags, creators, sounds, videos)   │
│                                                                              │
│  All data converted to unified schema with platform tag                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCORE CALCULATION PHASE                                   │
│               (TrendingScoreCalculator)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │   STEP 1:    │  │   STEP 2:    │  │   STEP 3:    │
          │  Calculate   │  │  Normalize   │  │   Apply      │
          │  Component   │  │  Component   │  │  Platform-   │
          │   Scores     │  │   Scores     │  │  Specific    │
          │              │  │   (0-100)    │  │  Weights     │
          └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                          ┌──────────────────────┐
                          │   FINAL TRENDING     │
                          │    SCORE (0-100)     │
                          │                      │
                          │  Sorted descending   │
                          └──────────────────────┘
```

---

## Component Scores (5 Dimensions)

## DETAILED CALCULATION METHODS

### 1. VOLUME SCORE - `_calculate_volume_score(trend)`
**What it measures:** Total reach and visibility across platforms

**Purpose:** Raw reach indicates how many people have been exposed to the trend

#### Code Implementation Logic:

```python
def _calculate_volume_score(self, trend: Dict[str, Any]) -> float:
    platform = trend.get('platform', '')

    if platform == 'google_trends':
        # Google Trends search volumes are typically 1K-500K
        # YouTube/TikTok views are 100K-10M
        # Multiply by 100 to bring to similar scale
        search_volume = float(trend.get('search_volume', 0))
        return search_volume * 100  # BOOST FACTOR

    elif platform == 'youtube':
        return float(trend.get('viewCount', 0))

    elif platform == 'tiktok':
        entity_type = trend.get('entity_type', '')
        if entity_type == 'hashtag':
            return float(trend.get('viewCount', 0))
        elif entity_type == 'creator':
            # Followers are more stable than views
            return float(trend.get('followerCount', 0)) * 10  # Weight up slightly
        elif entity_type == 'sound':
            return float(trend.get('viewCount', 0))
        elif entity_type == 'video':
            return float(trend.get('viewCount', 0))

    return 0.0
```

#### Platform-Specific Formulas:

**Google Trends:**
```
volume_score = search_volume × 100
```
- **Why × 100?** Google Trends volumes (1K-500K) are much smaller than social media views (100K-10M)
- **Boost factor** brings them to comparable scale
- **Example:** 50,000 searches → 5,000,000 volume score

**YouTube:**
```
volume_score = viewCount
```
- **Direct mapping** from view count
- **Example:** 1,500,000 views → 1,500,000 volume score

**TikTok:**
- **Hashtag:**
  ```
  volume_score = viewCount
  ```
  - Example: 10,000,000 views → 10,000,000 volume score

- **Creator:**
  ```
  volume_score = followerCount × 10
  ```
  - **Why × 10?** Follower count is more stable/lower than view counts
  - Example: 500,000 followers → 5,000,000 volume score

- **Sound/Video:**
  ```
  volume_score = viewCount
  ```
  - Example: 2,000,000 views → 2,000,000 volume score

**Note:** Returns RAW score - will be normalized to 0-100 later using min-max normalization

---

### 2. ENGAGEMENT SCORE - `_calculate_engagement_score(trend)`
**What it measures:** Quality of user interaction, not just passive viewing

**Purpose:** High engagement indicates genuine interest and active participation

#### Code Implementation Logic:

```python
def _calculate_engagement_score(self, trend: Dict[str, Any]) -> float:
    platform = trend.get('platform', '')

    if platform == 'google_trends':
        # For Google Trends, use increase_percentage as proxy for engagement
        # Return raw value - will be scaled dynamically later
        increase_pct = trend.get('increase_percentage', 0)
        return float(increase_pct)  # Return raw value

    elif platform == 'youtube':
        views = trend.get('viewCount', 0)
        if views == 0:
            return 0.0

        likes = trend.get('likeCount', 0)
        comments = trend.get('commentCount', 0)

        # Engagement rate formula: (likes + comments) / views * 100
        engagement_rate = ((likes + comments) / views) * 100

        # Scale it up for better distribution (typical ER is 2-5%)
        return engagement_rate * 1000

    elif platform == 'tiktok':
        entity_type = trend.get('entity_type', '')

        if entity_type == 'hashtag':
            video_count = trend.get('videoCount', 0)
            view_count = trend.get('viewCount', 1)  # Avoid division by zero
            # More videos per view indicates active participation
            return float(video_count) / float(view_count) * 1000000

        elif entity_type == 'creator':
            liked_count = trend.get('likedCount', 0)
            follower_count = trend.get('followerCount', 1)
            # Likes per follower ratio
            return (liked_count / follower_count) * 100

        elif entity_type == 'sound' or entity_type == 'video':
            # Use rank as proxy (lower rank = better engagement)
            rank = trend.get('rank', 100)
            return (100 - rank) * 10  # Invert so lower rank = higher score

    return 0.0
```

#### Platform-Specific Formulas:

**Google Trends:**
```
engagement_score = increase_percentage
```
- **Raw value returned** - will be dynamically normalized later
- **Why?** Google Trends doesn't have traditional engagement metrics (likes/comments)
- **Example:** 500% increase → 500 raw engagement score
- **Special processing:** Later normalized to match YouTube/TikTok scale (see _normalize_engagement_scores)

**YouTube:**
```
engagement_rate = (likeCount + commentCount) / viewCount × 100
engagement_score = engagement_rate × 1000
```
- **Why × 1000?** Typical engagement rates are 2-5%, need to scale up
- **Example:**
  - Views: 1,000,000, Likes: 30,000, Comments: 5,000
  - ER = (30,000 + 5,000) / 1,000,000 × 100 = 3.5%
  - Score = 3.5 × 1000 = 3,500

**TikTok:**

- **Hashtag:**
  ```
  engagement_score = (videoCount / viewCount) × 1,000,000
  ```
  - More videos created = more active participation
  - Example: 5,000 videos, 10M views → (5,000/10,000,000) × 1M = 500

- **Creator:**
  ```
  engagement_score = (likedCount / followerCount) × 100
  ```
  - Measures how engaged followers are
  - Example: 50M likes, 5M followers → (50M/5M) × 100 = 1,000

- **Sound/Video:**
  ```
  engagement_score = (100 - rank) × 10
  ```
  - Lower rank = better engagement
  - Example: Rank 5 → (100 - 5) × 10 = 950

**Dynamic Normalization (Special Processing):**
Google Trends engagement scores are normalized to match YouTube/TikTok range:
```
normalized = (google_score - google_min) / (google_max - google_min)
scaled_score = other_min + (normalized × other_range)
```

---

### 3. VELOCITY SCORE - `_calculate_velocity_score(trend)`
**What it measures:** Speed of growth and viral potential

**Purpose:** Fast-growing trends indicate emerging phenomena and viral content

#### Code Implementation Logic:

```python
def _calculate_velocity_score(self, trend: Dict[str, Any]) -> float:
    platform = trend.get('platform', '')

    if platform == 'google_trends':
        # Use a combination of increase_percentage and active status
        increase_pct = float(trend.get('increase_percentage', 0))

        # If trend is currently active, boost velocity
        is_active = trend.get('active', True)
        active_multiplier = 1.5 if is_active else 1.0

        # Calculate velocity based on increase % and activity
        velocity = increase_pct * 30 * active_multiplier  # BOOST FACTOR

        # Bonus for very high increase percentages (1000%+)
        if increase_pct >= 1000:
            velocity *= 1.2  # Extra 20% boost for viral trends

        return velocity

    elif platform == 'youtube':
        # For YouTube, calculate velocity from views/publish time
        views = trend.get('viewCount', 0)
        published_at = trend.get('publishedAt', '')

        if published_at:
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_since_publish = max(1, (self.current_time - pub_time).total_seconds() / 3600)

                # Views per hour
                velocity = views / hours_since_publish
                return velocity
            except:
                pass

        return float(views) / 24  # Assume 24 hours if no timestamp

    elif platform == 'tiktok':
        # Use trending histogram to calculate growth rate
        histogram = trend.get('trendingHistogram', [])

        if len(histogram) >= 2:
            # Calculate slope from first to last point
            first_val = histogram[0].get('value', 0)
            last_val = histogram[-1].get('value', 0)

            growth_rate = last_val - first_val
            return max(0, growth_rate) * 100  # Scale up

        # Fallback: use rank (lower = faster growing)
        rank = trend.get('rank', 100)
        return (100 - rank) * 10

    return 0.0
```

#### Platform-Specific Formulas:

**Google Trends:**
```
Base velocity = increase_percentage × 30
Active multiplier = 1.5 if active else 1.0
Viral multiplier = 1.2 if increase_percentage >= 1000 else 1.0

velocity_score = Base velocity × Active multiplier × Viral multiplier
```

**Step-by-step calculation:**
1. Start with increase_percentage
2. Multiply by 30 (boost factor)
3. If trend is currently active, multiply by 1.5
4. If increase >= 1000%, multiply by additional 1.2

**Example 1 (Active + Viral):**
- Increase: 1500%, Active: True
- Base: 1500 × 30 = 45,000
- Active: 45,000 × 1.5 = 67,500
- Viral: 67,500 × 1.2 = 81,000
- **Final: 81,000**

**Example 2 (Inactive):**
- Increase: 200%, Active: False
- Base: 200 × 30 = 6,000
- Active: 6,000 × 1.0 = 6,000
- **Final: 6,000**

**YouTube:**
```
velocity_score = viewCount / hours_since_publish
```
- **Views per hour** metric
- **Example:**
  - Views: 1,200,000
  - Published: 10 hours ago
  - Velocity: 1,200,000 / 10 = 120,000 views/hour

**TikTok:**
- **Primary method (with histogram):**
  ```
  growth_rate = last_value - first_value
  velocity_score = max(0, growth_rate) × 100
  ```
  - Uses trending histogram to calculate growth trajectory
  - Example: First value: 100, Last value: 500
  - Growth: 500 - 100 = 400
  - Velocity: 400 × 100 = 40,000

- **Fallback method (no histogram):**
  ```
  velocity_score = (100 - rank) × 10
  ```
  - Lower rank = faster growth
  - Example: Rank 8 → (100 - 8) × 10 = 920

---

### 4. RECENCY SCORE - `_calculate_recency_score(trend)`
**What it measures:** How recent the trend is using exponential decay

**Purpose:** Recent trends are more relevant for real-time insights

#### Code Implementation Logic:

```python
def _calculate_recency_score(self, trend: Dict[str, Any]) -> float:
    RECENCY_HALF_LIFE_HOURS = 24  # Score halves every 24 hours

    platform = trend.get('platform', '')
    timestamp = None

    if platform == 'google_trends':
        timestamp = trend.get('start_timestamp')
    elif platform == 'youtube':
        published_at = trend.get('publishedAt', '')
        if published_at:
            try:
                timestamp = datetime.fromisoformat(published_at.replace('Z', '+00:00')).timestamp()
            except:
                pass
    elif platform == 'tiktok':
        # TikTok doesn't always provide timestamps, use trending start
        histogram = trend.get('trendingHistogram', [])
        if histogram:
            try:
                date_str = histogram[-1].get('date', '')
                timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00')).timestamp()
            except:
                pass

    if not timestamp:
        # No timestamp available, assume recent (12 hours ago)
        return 70.0

    # Calculate age in hours
    age_seconds = self.current_time.timestamp() - timestamp
    age_hours = max(0, age_seconds / 3600)

    # Exponential decay formula
    decay_factor = age_hours / RECENCY_HALF_LIFE_HOURS
    recency_score = 100 * math.pow(0.5, decay_factor)

    return max(0, min(100, recency_score))  # Clamp to 0-100
```

#### Universal Formula:

```
recency_score = 100 × (0.5)^(age_hours / 24)
```

**Mathematical Explanation:**
- **Exponential decay** with half-life of 24 hours
- Content loses half its recency value every 24 hours
- Formula ensures smooth decay over time

#### Decay Table:

| Age | Calculation | Score |
|-----|-------------|-------|
| 1 hour | 100 × (0.5)^(1/24) | ~97.2 |
| 6 hours | 100 × (0.5)^(6/24) | ~84.1 |
| 12 hours | 100 × (0.5)^(12/24) | ~70.7 |
| 24 hours | 100 × (0.5)^(24/24) | 50.0 |
| 48 hours | 100 × (0.5)^(48/24) | 25.0 |
| 72 hours | 100 × (0.5)^(72/24) | 12.5 |
| 1 week (168h) | 100 × (0.5)^(168/24) | ~1.5 |

#### Detailed Examples:

**Example 1: Fresh Content**
```
Published: 3 hours ago
age_hours = 3
decay_factor = 3 / 24 = 0.125
recency_score = 100 × (0.5)^0.125 = 100 × 0.917 = 91.7
```

**Example 2: Day-Old Content**
```
Published: 24 hours ago
age_hours = 24
decay_factor = 24 / 24 = 1.0
recency_score = 100 × (0.5)^1.0 = 100 × 0.5 = 50.0
```

**Example 3: Week-Old Content**
```
Published: 168 hours ago (1 week)
age_hours = 168
decay_factor = 168 / 24 = 7.0
recency_score = 100 × (0.5)^7.0 = 100 × 0.0078 = 0.78
```

**Platform-Specific Timestamp Extraction:**
- **Google Trends:** Uses `start_timestamp` field
- **YouTube:** Parses `publishedAt` ISO format datetime
- **TikTok:** Extracts from last entry in `trendingHistogram`
- **Fallback:** If no timestamp, defaults to 70.0 (assumes ~12 hours ago)

**Note:** Returns score already in 0-100 range (no further normalization needed)

---

### 5. CROSS-PLATFORM SCORE - `_calculate_cross_platform_score(trend, all_trends)`
**What it measures:** Presence across multiple platforms using fuzzy term matching

**Purpose:** Multi-platform presence indicates stronger, more universal trends

#### Code Implementation Logic:

```python
def _calculate_cross_platform_score(self, trend: Dict[str, Any], all_trends: List[Dict[str, Any]]) -> float:
    # Extract key terms from this trend
    trend_terms = self._extract_key_terms(trend)

    if not trend_terms:
        return 0.0

    # Count matches across platforms
    platforms_found = set([trend.get('platform')])

    for other in all_trends:
        if other is trend:
            continue

        other_platform = other.get('platform')
        if other_platform in platforms_found:
            continue

        other_terms = self._extract_key_terms(other)

        # Check for overlap
        if self._terms_overlap(trend_terms, other_terms):
            platforms_found.add(other_platform)

    # Score: 0 for 1 platform, 50 for 2 platforms, 100 for 3 platforms
    num_platforms = len(platforms_found)

    if num_platforms == 1:
        return 0.0
    elif num_platforms == 2:
        return 50.0
    else:  # 3 or more
        return 100.0

def _extract_key_terms(self, trend: Dict[str, Any]) -> set:
    """Extract searchable terms from trend item."""
    terms = set()

    # Get title/name/query
    text = (
        trend.get('query', '') or
        trend.get('title', '') or
        trend.get('name', '') or
        ''
    )

    # Normalize and split
    text = text.lower()
    words = text.split()

    # Remove common stop words and keep significant terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'vs', 'x'}
    significant_words = [w for w in words if len(w) > 2 and w not in stop_words]

    terms.update(significant_words)

    return terms

def _terms_overlap(self, terms1: set, terms2: set, threshold: float = 0.3) -> bool:
    """Check if two term sets overlap significantly."""
    if not terms1 or not terms2:
        return False

    intersection = terms1.intersection(terms2)
    union = terms1.union(terms2)

    if not union:
        return False

    overlap_ratio = len(intersection) / len(union)
    return overlap_ratio >= threshold
```

#### Scoring Logic:

```
If num_platforms == 1: cross_platform_score = 0
If num_platforms == 2: cross_platform_score = 50
If num_platforms >= 3: cross_platform_score = 100
```

#### Step-by-Step Process:

**Step 1: Extract Key Terms**
```python
# Input: "iPhone 15 Pro Max Review"
text = "iPhone 15 Pro Max Review"
text_lower = "iphone 15 pro max review"
words = ["iphone", "15", "pro", "max", "review"]

# Remove stop words (none in this case, all > 2 chars)
terms = {"iphone", "15", "pro", "max", "review"}
```

**Step 2: Find Matching Trends**
For each trend on other platforms:
1. Extract its key terms
2. Calculate overlap ratio
3. If overlap >= 30%, consider it a match

**Step 3: Calculate Overlap Ratio**
```
overlap_ratio = |intersection| / |union|
```

**Example Term Matching:**

**Trend A (YouTube):** "iPhone 15 Pro Max Review"
- Terms: `{"iphone", "15", "pro", "max", "review"}`

**Trend B (TikTok):** "iPhone 15 Pro Unboxing"
- Terms: `{"iphone", "15", "pro", "unboxing"}`

**Overlap Calculation:**
```
Intersection = {"iphone", "15", "pro"}  → 3 terms
Union = {"iphone", "15", "pro", "max", "review", "unboxing"}  → 6 terms
Overlap ratio = 3 / 6 = 0.5 = 50%

50% >= 30% threshold → MATCH!
```

#### Detailed Examples:

**Example 1: Single Platform (YouTube only)**
```
Trend: "Gaming PC Build Guide"
Platforms found: {"youtube"}
num_platforms = 1
cross_platform_score = 0.0
```

**Example 2: Two Platforms (YouTube + TikTok)**
```
YouTube: "Taylor Swift New Album"
TikTok: "Taylor Swift Album Review"

YouTube terms: {"taylor", "swift", "new", "album"}
TikTok terms: {"taylor", "swift", "album", "review"}

Intersection: {"taylor", "swift", "album"} → 3
Union: {"taylor", "swift", "new", "album", "review"} → 5
Overlap: 3/5 = 0.6 = 60% >= 30% ✓

Platforms found: {"youtube", "tiktok"}
num_platforms = 2
cross_platform_score = 50.0
```

**Example 3: Three Platforms (Google + YouTube + TikTok)**
```
Google Trends: "World Cup 2024"
YouTube: "World Cup Highlights"
TikTok: "World Cup Goals"

All share terms: {"world", "cup"}
Overlap ratios all >= 30%

Platforms found: {"google_trends", "youtube", "tiktok"}
num_platforms = 3
cross_platform_score = 100.0
```

#### Stop Words Filter:
```python
stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'vs', 'x'}
```
- Common words removed to focus on meaningful terms
- Only words with length > 2 characters kept

**Note:** Returns score already in 0-100 range (no further normalization needed)

---

## Score Normalization

### Step 1: Calculate Raw Scores
Each component score is calculated using platform-specific formulas

### Step 2: Min-Max Normalization (0-100)
```
normalized_score = ((raw_score - min_score) / (max_score - min_score)) × 100
```

**Applied to:**
- Volume scores
- Engagement scores (after Google Trends dynamic normalization)
- Velocity scores

**Not applied to:**
- Recency scores (already 0-100)
- Cross-platform scores (already 0-100)

---

## Platform-Specific Weighted Scoring

### Adaptive Weights by Platform

#### **Google Trends** (limited metrics available)
```
┌─────────────────────┬─────────┬──────────────────────────┐
│ Component           │ Weight  │ Justification            │
├─────────────────────┼─────────┼──────────────────────────┤
│ Volume              │  35%    │ Increased (strength)     │
│ Engagement          │  15%    │ Decreased (limited data) │
│ Velocity            │  30%    │ Increased (strength)     │
│ Recency             │  15%    │ Same                     │
│ Cross-Platform      │   5%    │ Decreased                │
└─────────────────────┴─────────┴──────────────────────────┘
```

#### **YouTube** (balanced metrics)
```
┌─────────────────────┬─────────┬──────────────────────────┐
│ Component           │ Weight  │ Justification            │
├─────────────────────┼─────────┼──────────────────────────┤
│ Volume              │  30%    │ Balanced                 │
│ Engagement          │  25%    │ Balanced                 │
│ Velocity            │  20%    │ Balanced                 │
│ Recency             │  15%    │ Balanced                 │
│ Cross-Platform      │  10%    │ Balanced                 │
└─────────────────────┴─────────┴──────────────────────────┘
```

#### **TikTok** (rich engagement data)
```
┌─────────────────────┬─────────┬──────────────────────────┐
│ Component           │ Weight  │ Justification            │
├─────────────────────┼─────────┼──────────────────────────┤
│ Volume              │  25%    │ Decreased                │
│ Engagement          │  30%    │ Increased (strength)     │
│ Velocity            │  20%    │ Same                     │
│ Recency             │  15%    │ Same                     │
│ Cross-Platform      │  10%    │ Same                     │
└─────────────────────┴─────────┴──────────────────────────┘
```

---

## Final Score Calculation

### Formula:
```
trending_score =
    (weight_volume × volume_score) +
    (weight_engagement × engagement_score) +
    (weight_velocity × velocity_score) +
    (weight_recency × recency_score) +
    (weight_cross_platform × cross_platform_score)
```

### Result:
- **Range:** 0-100
- **Precision:** Rounded to 2 decimal places
- **Sorting:** Descending (highest score first)

---

## Score Transparency

Each trend includes a `score_breakdown` showing:
```json
{
  "trending_score": 87.45,
  "score_breakdown": {
    "volume": 92.15,
    "engagement": 78.30,
    "velocity": 95.60,
    "recency": 88.20,
    "cross_platform": 50.00
  },
  "weights_used": {
    "volume": 0.30,
    "engagement": 0.25,
    "velocity": 0.20,
    "recency": 0.15,
    "cross_platform": 0.10
  }
}
```

---

## Implementation Flow (Code Level)

### File: `main.py`
```
POST /unified-trends endpoint:
│
├─ Step 1: Aggregate data from all platforms
│  └─ TrendAggregatorService.aggregate_all_trends()
│     ├─ Fetch Google Trends
│     ├─ Fetch YouTube videos
│     ├─ Fetch TikTok data
│     └─ Normalize all to unified format
│
├─ Step 2: Filter by time range (optional)
│  └─ TrendAggregatorService.filter_by_time_range()
│
├─ Step 3: Calculate trending scores
│  └─ TrendAggregatorService.calculate_trending_scores()
│     └─ TrendingScoreCalculator.calculate_universal_score_adaptive()
│        ├─ Calculate component scores (volume, engagement, velocity, recency, cross-platform)
│        ├─ Normalize engagement scores (Google Trends → others)
│        ├─ Normalize all scores to 0-100
│        ├─ Apply platform-specific weights
│        └─ Sort by trending_score (descending)
│
├─ Step 4: Limit to top N results
│
└─ Step 5: Return response with metadata
```

### File: `trending_score_calculator.py`
**Key Methods:**
- `calculate_universal_score_adaptive()` - Main scoring orchestrator
- `_calculate_volume_score()` - Calculates volume component
- `_calculate_engagement_score()` - Calculates engagement component
- `_calculate_velocity_score()` - Calculates velocity component
- `_calculate_recency_score()` - Calculates recency component
- `_calculate_cross_platform_score()` - Calculates cross-platform component
- `_normalize_engagement_scores()` - Dynamic normalization for Google Trends
- `_normalize_scores()` - Min-max normalization to 0-100
- `_extract_key_terms()` - Extracts terms for cross-platform matching
- `_terms_overlap()` - Fuzzy matching for cross-platform detection

---

## Example Calculation

### Input: YouTube Video
```
Views: 1,000,000
Likes: 50,000
Comments: 5,000
Published: 12 hours ago
Found on: YouTube only
```

### Component Calculations:
1. **Volume:** 1,000,000 (raw) → Normalized to 85.5
2. **Engagement:** ((50,000 + 5,000) / 1,000,000) × 100 × 1000 = 5,500 → Normalized to 72.3
3. **Velocity:** 1,000,000 / 12 = 83,333 → Normalized to 91.2
4. **Recency:** 100 × (0.5)^(12/24) = 70.7
5. **Cross-Platform:** 0 (only on YouTube)

### Final Score (YouTube weights):
```
trending_score =
    (0.30 × 85.5) +  # Volume
    (0.25 × 72.3) +  # Engagement
    (0.20 × 91.2) +  # Velocity
    (0.15 × 70.7) +  # Recency
    (0.10 × 0)       # Cross-Platform
= 25.65 + 18.08 + 18.24 + 10.61 + 0
= 72.58
```

---

## Key Design Decisions

### 1. Platform-Specific Weights
- Each platform has different strengths (Google: velocity, TikTok: engagement)
- Adaptive weighting ensures fair comparison

### 2. Dynamic Engagement Normalization
- Google Trends uses increase_percentage (different scale than likes/comments)
- Dynamic normalization brings it to comparable range

### 3. Exponential Recency Decay
- Ensures recent content is prioritized
- Half-life of 24 hours balances freshness vs. stability

### 4. Cross-Platform Bonus
- Multi-platform presence indicates stronger, more universal trends
- Uses fuzzy matching to handle different naming conventions

### 5. Min-Max Normalization
- Makes scores relative to current dataset
- Ensures fair distribution across 0-100 range
- All metrics comparable despite different raw scales

---

## API Response Structure

```json
{
  "country": "US",
  "timestamp": "2025-11-12T10:30:00Z",
  "time_range": "24h",
  "total_trends_analyzed": 150,
  "returned_trends": 25,
  "platform_counts": {
    "google_trends": 50,
    "youtube": 50,
    "tiktok": 50
  },
  "score_methodology": {
    "weights": {
      "volume": 0.30,
      "engagement": 0.25,
      "velocity": 0.20,
      "recency": 0.15,
      "cross_platform": 0.10
    },
    "description": "Universal trending score combines volume, engagement, velocity, recency, and cross-platform presence",
    "scale": "0-100 (higher is better)",
    "normalization": "Min-max normalization within dataset"
  },
  "trends": [
    {
      "platform": "youtube",
      "title": "Example Video",
      "trending_score": 87.45,
      "score_breakdown": {
        "volume": 92.15,
        "engagement": 78.30,
        "velocity": 95.60,
        "recency": 88.20,
        "cross_platform": 50.00
      },
      "weights_used": {
        "volume": 0.30,
        "engagement": 0.25,
        "velocity": 0.20,
        "recency": 0.15,
        "cross_platform": 0.10
      },
      "metadata": { /* platform-specific data */ }
    }
  ]
}
```

---

## Visual Score Flow Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                   RAW DATA INPUT                               │
│  Google Trends │ YouTube │ TikTok                             │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│              COMPONENT SCORE CALCULATION                       │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │   Volume    │  │  Engagement  │  │  Velocity   │         │
│  │  (raw calc) │  │  (raw calc)  │  │ (raw calc)  │         │
│  └─────────────┘  └──────────────┘  └─────────────┘         │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐                           │
│  │  Recency    │  │Cross-Platform│                           │
│  │ (0-100)     │  │   (0-100)    │                           │
│  └─────────────┘  └──────────────┘                           │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    NORMALIZATION                               │
│                                                                │
│  1. Dynamic engagement normalization (Google Trends)          │
│  2. Min-Max normalization (0-100) for:                        │
│     - Volume                                                   │
│     - Engagement                                               │
│     - Velocity                                                 │
│                                                                │
│  Result: All scores now in 0-100 range                        │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│               PLATFORM-SPECIFIC WEIGHTING                      │
│                                                                │
│  IF platform = "google_trends":                               │
│    weights = [35%, 15%, 30%, 15%, 5%]                        │
│  ELSE IF platform = "youtube":                                │
│    weights = [30%, 25%, 20%, 15%, 10%]                       │
│  ELSE IF platform = "tiktok":                                 │
│    weights = [25%, 30%, 20%, 15%, 10%]                       │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                FINAL SCORE CALCULATION                         │
│                                                                │
│  trending_score = Σ (weight[i] × component_score[i])         │
│                                                                │
│  Range: 0-100                                                  │
│  Precision: 2 decimal places                                  │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                  SORTING & OUTPUT                              │
│                                                                │
│  Sort by trending_score (descending)                          │
│  Return top N trends with full breakdown                      │
└───────────────────────────────────────────────────────────────┘
```

---

## Summary

The scoring mechanism provides a **fair, transparent, and scientifically justified** way to compare trends across different platforms. By using:

1. **5 weighted components** that capture different aspects of trending
2. **Platform-specific adaptations** that account for data availability
3. **Dynamic normalization** to ensure fair comparison
4. **Full transparency** with score breakdowns

The system generates a universal 0-100 trending score that accurately reflects the overall "trendiness" of content across Google Trends, YouTube, and TikTok.
