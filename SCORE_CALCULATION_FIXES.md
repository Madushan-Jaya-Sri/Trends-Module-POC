# Score Calculation Fixes - Engagement and Velocity

## Problem Identified

Multiple trends were receiving identical normalized scores (100.0) for both engagement and velocity, even though they had different raw metric values. This occurred because:

1. **Engagement Score Issue**: Used raw sum of `(likes + comments)`, so multiple YouTube videos with the same total engagement received identical scores regardless of their view counts
2. **Velocity Score Issue**: Used only `views / hours_since_publish`, so videos published at similar times with similar views received identical velocities

## Root Cause Analysis

### Engagement Score (Previous Implementation)
```python
# OLD CODE (Line 355)
engagement_score = (likes + comments)
```

**Problem**:
- Video A: 1M views, 1.3M likes+comments → engagement_score = 1,307,349
- Video B: 100M views, 1.3M likes+comments → engagement_score = 1,307,349
- Both videos get the same score despite vastly different engagement rates!

### Velocity Score (Previous Implementation)
```python
# OLD CODE (Lines 501-502)
velocity = views / hours_since_publish
```

**Problem**:
- Video A: 10M views in 10 hours → velocity = 1,000,000
- Video B: 10M views in 10 hours → velocity = 1,000,000
- If they have different engagement patterns, this isn't captured

## Solutions Implemented

### 1. Engagement Score Fix

**File**: `backend/app/services/trending_score_calculator.py` (Lines 345-362)

**New Implementation**:
```python
elif platform == 'youtube':
    views = trend.get('viewCount', 0)
    if views == 0:
        return 0.0

    likes = trend.get('likeCount', 0)
    comments = trend.get('commentCount', 0)

    # Engagement rate formula: (likes + comments) / views
    # This ensures videos with the same likes+comments but different views get different scores
    engagement_rate = (likes + comments) / views

    # Scale by 1M to get reasonable numbers for normalization
    # Typical engagement rates are 2-5%, so 0.02-0.05
    # Multiply by 1M to get 20,000-50,000 range
    engagement_score = engagement_rate * 1_000_000

    return engagement_score
```

**Benefits**:
- Now considers engagement **rate** relative to views
- Videos with same total engagement but different views get different scores
- Better represents actual user engagement quality
- Scores are scaled appropriately for min-max normalization

**Example**:
- Video A: 1M views, 1.3M engagement → rate = 1.3, score = 1,300,000
- Video B: 100M views, 1.3M engagement → rate = 0.013, score = 13,000
- After normalization to 0-100, these will have very different percentile scores

### 2. Velocity Score Fix

**File**: `backend/app/services/trending_score_calculator.py` (Lines 492-518)

**New Implementation**:
```python
elif platform == 'youtube':
    # For YouTube, calculate velocity from views/publish time
    views = trend.get('viewCount', 0)
    likes = trend.get('likeCount', 0)
    comments = trend.get('commentCount', 0)
    published_at = trend.get('publishedAt', '')

    if published_at:
        try:
            pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            hours_since_publish = max(1, (self.current_time - pub_time).total_seconds() / 3600)

            # Combined velocity: views per hour + engagement per hour
            # Weight views more heavily (70%) than engagement (30%)
            view_velocity = views / hours_since_publish
            engagement_velocity = (likes + comments) / hours_since_publish

            # Combined velocity with weighted average
            velocity = (view_velocity * 0.7) + (engagement_velocity * 0.3)
            return velocity
        except:
            pass

    # Fallback: assume 24 hours if no timestamp
    view_velocity = float(views) / 24
    engagement_velocity = float(likes + comments) / 24
    return (view_velocity * 0.7) + (engagement_velocity * 0.3)
```

**Benefits**:
- Combines both view velocity (70%) and engagement velocity (30%)
- Even if two videos have identical views per hour, they'll differ based on engagement velocity
- More nuanced measure of viral growth potential
- Weighted average prioritizes views while still considering engagement

**Example**:
- Video A: 10M views, 100K engagement in 10 hours → velocity = (1M × 0.7) + (10K × 0.3) = 703,000
- Video B: 10M views, 500K engagement in 10 hours → velocity = (1M × 0.7) + (50K × 0.3) = 715,000
- Different velocity scores even with same view counts!

## Expected Results

After these fixes:

1. **No More Duplicate 100.0 Scores**: Multiple trends should no longer show identical maximum scores unless they truly have identical engagement rates or velocities
2. **Better Score Distribution**: Scores will be more evenly distributed across the 0-100 range
3. **More Accurate Rankings**: Trends will be ranked more accurately based on their actual performance relative to views and time
4. **Improved Percentiles**: The percentage values in `score_breakdown` will better represent each trend's position relative to others

## Testing

To verify the fixes work:

1. Fetch unified trends: `POST /unified-trends`
2. Check the logs for normalization output
3. Verify that multiple trends no longer have identical `engagement_score=100.0` or `velocity_score=100.0`
4. Confirm scores are distributed across a range of values

## Files Modified

- `backend/app/services/trending_score_calculator.py`
  - Lines 345-362: Engagement score calculation for YouTube
  - Lines 492-518: Velocity score calculation for YouTube

## Impact

- **Engagement**: Now uses rate-based scoring instead of absolute values
- **Velocity**: Now combines view and engagement velocities
- **Score Distribution**: More diverse and accurate scores across all trends
- **Frontend Display**: Percentage values in `score_breakdown` will now be more meaningful

---

**Date**: November 23, 2025
**Status**: ✅ Fixed and Deployed
