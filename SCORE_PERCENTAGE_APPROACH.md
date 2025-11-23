# Score Percentage Calculation - Proportion of Total

## Fundamental Change

Changed from **min-max normalization** (percentile position) to **percentage of total** (proportion).

### Previous Approach: Min-Max Normalization ❌
```
- Find minimum and maximum values
- Scale each value: ((value - min) / (max - min)) * 100
- Result: Values range from 0 to 100
- Problem: Always assigns 100 to max value, 0 to min value
- Sum of all percentages: NOT 100%
```

**Example with min-max:**
- Trend A: volume 1000 → 100% (max)
- Trend B: volume 500 → 0% (min)
- Trend C: volume 500 → 0% (min)
- **Sum: 100% (only because there's one max)**
- **Issue: Multiple trends can have identical scores**

### New Approach: Percentage of Total ✅
```
- Sum all values for a metric
- Each value: (value / total) * 100
- Result: Values represent proportion of total
- Sum of all percentages: Always 100%
```

**Example with percentage of total:**
- Trend A: volume 1000 → (1000/2000) * 100 = **50%**
- Trend B: volume 500 → (500/2000) * 100 = **25%**
- Trend C: volume 500 → (500/2000) * 100 = **25%**
- **Sum: 50 + 25 + 25 = 100%** ✅
- **No duplicate 100% scores unless there's only one trend**

## Implementation

### File Modified
`backend/app/services/trending_score_calculator.py` - Line 792-840

### New `_normalize_scores` Method

```python
def _normalize_scores(self, trends: List[Dict[str, Any]], score_key: str):
    """
    Normalize scores to percentage of total (0-100 scale).

    Each score represents the proportion of the total for that metric.
    All scores for a metric sum to 100%.
    """
    if not trends:
        return

    scores = [t.get(score_key, 0) for t in trends]
    total_score = sum(scores)

    logger.info(f"Normalizing {score_key}: {len(trends)} trends, total={total_score:.4f}")

    # Handle case where all scores are zero
    if total_score == 0:
        logger.info(f"All {score_key} values are zero, setting all to equal distribution")
        equal_percentage = 100.0 / len(trends)
        for trend in trends:
            trend[score_key] = equal_percentage
        return

    # Calculate percentage of total
    normalized_values = []
    for trend in trends:
        raw_score = trend.get(score_key, 0)
        percentage = (raw_score / total_score) * 100
        trend[score_key] = percentage
        normalized_values.append(percentage)

    # Verify sum equals 100
    total_percentage = sum(normalized_values)
    logger.info(f"Normalized {score_key}: total={total_percentage:.2f}% (should be ~100%)")
```

## How It Works

### For Each Metric (Volume, Engagement, Velocity, Recency)

1. **Calculate Raw Scores** for all trends in the platform
2. **Sum all raw scores** for that metric
3. **Calculate each trend's percentage** of the total
4. **Result**: All percentages for that metric sum to 100%

### Example: YouTube Videos

**Volume (viewCount):**
- Video 1: 10M views → (10M / 25M) * 100 = **40%**
- Video 2: 8M views → (8M / 25M) * 100 = **32%**
- Video 3: 5M views → (5M / 25M) * 100 = **20%**
- Video 4: 2M views → (2M / 25M) * 100 = **8%**
- **Total: 40 + 32 + 20 + 8 = 100%** ✅

**Engagement (engagement rate * 1M):**
- Video 1: 50K engagement score → (50K / 150K) * 100 = **33.33%**
- Video 2: 60K engagement score → (60K / 150K) * 100 = **40%**
- Video 3: 30K engagement score → (30K / 150K) * 100 = **20%**
- Video 4: 10K engagement score → (10K / 150K) * 100 = **6.67%**
- **Total: 33.33 + 40 + 20 + 6.67 = 100%** ✅

## Benefits

1. **No Duplicate 100% Scores**: Only one trend can have 100% if it represents all of the metric
2. **Additive Property**: All percentages sum to 100% for each metric
3. **Intuitive Interpretation**: "This trend represents 25% of total volume"
4. **Fair Distribution**: Even if values are close, they get proportional percentages
5. **No Arbitrary Scaling**: Based purely on actual contribution to total

## Edge Cases Handled

### All Scores Are Zero
If all trends have 0 for a metric (e.g., no engagement data):
- Distribute equally: Each trend gets `100 / number_of_trends`
- Example: 4 trends with 0 engagement → each gets 25%
- This ensures scores still sum to 100%

### Single Trend
If there's only one trend:
- It gets 100% of each metric
- This is correct since it represents all of the data

## Impact on Frontend

### Before (Min-Max Normalization)
```json
{
  "score_breakdown": {
    "volume": 100.0,      // This is the max
    "engagement": 100.0,  // This is also the max (identical!)
    "velocity": 50.0,     // Middle value
    "recency": 0.0        // This is the min
  }
}
```
**Problem**: Multiple 100.0 values don't tell you anything meaningful

### After (Percentage of Total)
```json
{
  "score_breakdown": {
    "volume": 15.3,       // 15.3% of total volume
    "engagement": 22.7,   // 22.7% of total engagement
    "velocity": 8.9,      // 8.9% of total velocity
    "recency": 3.2        // 3.2% of total recency
  }
}
```
**Benefit**: Each percentage tells you the trend's contribution to the total

## Verification

To verify the implementation is working:

1. Call `/unified-trends` endpoint
2. For each platform, sum all `volume` percentages → should equal ~100%
3. Sum all `engagement` percentages for that platform → should equal ~100%
4. Sum all `velocity` percentages for that platform → should equal ~100%
5. Sum all `recency` percentages for that platform → should equal ~100%

## Logs to Expect

Old logs:
```
WARNING: 12 trends have engagement_score=100.0 (max value=95947.37)
```

New logs:
```
Normalizing volume_score: 633 trends, total=1500000000.0000
Normalized volume_score: total=100.00%, >10%: 5, <0.1%: 200
```

No more warnings about duplicate 100.0 values!

## Changes to Comments

Updated all `score_breakdown` comments to reflect new approach:

**Before:**
```python
# These scores represent the trend's position relative to other trends
# 0 = lowest in dataset, 100 = highest in dataset
```

**After:**
```python
# These scores represent the proportion of the total for each metric
# All volumes sum to 100%, all engagements sum to 100%, etc.
# Example: volume=25% means this trend represents 25% of total volume
```

---

**Date**: November 24, 2025
**Status**: ✅ Implemented - Percentage of Total Approach
**Breaking Change**: Yes - score_breakdown values now represent proportion, not position
