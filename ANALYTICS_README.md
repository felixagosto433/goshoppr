# GoShopPR Analytics Dashboard Implementation

## Overview

This implementation adds comprehensive analytics capabilities to your GoShopPR chatbot, enabling you to track user behavior, product recommendations, location searches, and user journey completion rates.

## Current Database Analysis

### Strengths ✅
- **Good foundation**: Existing `chat_state` table tracks user interactions
- **Session tracking**: Captures session start/end times
- **Context preservation**: JSON context field stores user preferences
- **Historical data**: Keeps all state changes for analysis

### Issues Identified ❌
- **Limited analytics structure**: JSON context makes querying difficult
- **Missing key metrics**: No direct tracking of product interactions, conversion rates
- **No structured product data**: Can't easily see which products are most recommended
- **Limited location analytics**: No tracking of which pueblos are most active

## New Analytics Features

### 1. Enhanced Database Schema
- **User Sessions Table**: Tracks complete user journeys
- **Product Interactions Table**: Monitors product recommendations and clicks
- **User Goals Table**: Stores health goals and preferences
- **Location Analytics Table**: Tracks pueblo search patterns
- **Flow Analytics Table**: Analyzes chat stage transitions

### 2. Key Metrics Tracked
- **User Engagement**: Total users, sessions, completion rates
- **Product Performance**: Recommendations shown vs. clicked
- **Location Insights**: Most searched pueblos, success rates
- **Health Goals**: Most common user objectives
- **Journey Analytics**: Session duration, completion rates

### 3. Dashboard Features
- **Real-time Metrics**: Live user engagement data
- **Interactive Charts**: Visual representation of trends
- **Export Capabilities**: Data export for external analysis
- **Responsive Design**: Works on desktop and mobile

## Implementation Steps

### Step 1: Run Database Migration
```bash
python migrate_analytics.py
```

This will:
- Create new analytics tables
- Migrate existing data from `chat_state`
- Set up indexes and views for performance

### Step 2: Update Your App Configuration

Add the dashboard routes to your `app.py`:

```python
from app.dashboard_routes import dashboard

# Register the dashboard blueprint
app.register_blueprint(dashboard)
```

### Step 3: Serve the Dashboard

Add this route to serve the dashboard HTML:

```python
@app.route('/dashboard')
def dashboard_page():
    return send_file('dashboard.html')
```

### Step 4: Integrate Analytics Tracking

Update your handlers to use the enhanced analytics:

```python
from app.analytics_db import AnalyticsDB, track_product_recommendation

# In your recommendation handlers, add:
def handle_recommendation(user_id, user_message, state):
    # ... existing code ...
    
    # Track product recommendations
    if results:
        track_product_recommendation(
            user_id=user_id,
            session_id=session_id,  # You'll need to track this
            products=results,
            stage=state["stage"],
            context=state.get("context")
        )
```

## Dashboard Access

Once implemented, access your dashboard at:
- **Main Dashboard**: `http://your-domain.com/dashboard`
- **API Endpoints**: 
  - `/api/dashboard/overview` - Complete dashboard data
  - `/api/dashboard/engagement` - User engagement metrics
  - `/api/dashboard/products` - Product analytics
  - `/api/dashboard/locations` - Location analytics

## Key Analytics Insights You'll Get

### 1. User Behavior Analysis
- **Session Duration**: How long users spend in the chatbot
- **Completion Rates**: Percentage of users who complete their journey
- **Drop-off Points**: Where users abandon the conversation
- **Return Users**: Users who come back multiple times

### 2. Product Performance
- **Most Recommended Products**: Which products are suggested most often
- **Click-through Rates**: How often users click on product recommendations
- **Category Performance**: Which product categories perform best
- **User Preference Patterns**: What types of supplements users prefer

### 3. Location Intelligence
- **Popular Pueblos**: Which locations search for pharmacies most
- **Search Success Rates**: How often location searches find results
- **Geographic Trends**: Regional patterns in user behavior

### 4. Health Goal Insights
- **Common Health Goals**: Most frequent user objectives
- **Medical Condition Patterns**: Types of conditions users mention
- **Supplement Preferences**: User preferences for vitamins, herbs, etc.

## Database Schema Details

### New Tables Created

#### `user_sessions`
- Tracks complete user sessions
- Records session duration and completion status
- Links to user goals and interactions

#### `product_interactions`
- Tracks every product recommendation
- Records user clicks and engagement
- Links to user goals and preferences

#### `user_goals`
- Stores user health objectives
- Records medical conditions and preferences
- Links to location data

#### `location_analytics`
- Tracks pueblo search patterns
- Records search success rates
- Monitors geographic trends

## Performance Optimizations

### Indexes Created
- User ID indexes for fast lookups
- Timestamp indexes for date range queries
- Location indexes for geographic analytics

### Views for Common Queries
- `user_journey_analytics`: Complete user journey data
- `product_analytics`: Product performance metrics
- `location_analytics_summary`: Location search insights

## API Endpoints

### Dashboard Data
```bash
GET /api/dashboard/overview
# Returns comprehensive dashboard data
```

### Specific Metrics
```bash
GET /api/dashboard/engagement?days=30
GET /api/dashboard/products
GET /api/dashboard/locations
GET /api/dashboard/journeys?limit=20
```

### Data Export
```bash
GET /api/dashboard/export?type=products
GET /api/dashboard/export?type=locations
GET /api/dashboard/export?type=journeys
```

## Monitoring and Maintenance

### Regular Tasks
1. **Data Cleanup**: Archive old data periodically
2. **Performance Monitoring**: Watch query performance
3. **Backup Strategy**: Ensure analytics data is backed up

### Recommended Monitoring
- **Daily**: Check dashboard for new insights
- **Weekly**: Review user engagement trends
- **Monthly**: Analyze product performance patterns

## Troubleshooting

### Common Issues

1. **Migration Fails**
   - Check database connection
   - Ensure sufficient permissions
   - Verify PostgreSQL version compatibility

2. **Dashboard Not Loading**
   - Check API endpoints are accessible
   - Verify database tables exist
   - Check browser console for errors

3. **No Data Showing**
   - Run migration script first
   - Check if new interactions are being tracked
   - Verify analytics functions are being called

### Debug Commands
```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE '%analytics%';

-- Check data counts
SELECT COUNT(*) FROM user_sessions;
SELECT COUNT(*) FROM product_interactions;
SELECT COUNT(*) FROM location_analytics;
```

## Future Enhancements

### Potential Improvements
1. **Real-time Analytics**: WebSocket updates for live data
2. **Advanced Segmentation**: User behavior clustering
3. **Predictive Analytics**: User journey prediction
4. **A/B Testing**: Test different chatbot flows
5. **Integration APIs**: Connect with external analytics tools

### Advanced Features
- **User Segmentation**: Group users by behavior patterns
- **Conversion Funnels**: Track user progression through stages
- **Heat Maps**: Visualize user interaction patterns
- **Machine Learning**: Predict user needs and preferences

## Support

For implementation help or questions:
1. Check the migration logs for errors
2. Verify database connectivity
3. Test API endpoints individually
4. Review browser console for JavaScript errors

The analytics dashboard will provide valuable insights into your chatbot's performance and help you optimize the user experience based on real data. 