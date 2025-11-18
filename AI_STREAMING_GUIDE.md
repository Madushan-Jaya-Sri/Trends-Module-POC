# AI Analysis Streaming Endpoints - Frontend Integration Guide

## Overview

Two new AI-powered endpoints provide real-time streaming responses for trend analysis and marketing recommendations:

1. **`POST /ai-interpretation`** - AI-powered interpretation of trending data
2. **`POST /ai-recommendations`** - AI-powered marketing recommendations

Both endpoints stream responses in real-time, allowing you to display the AI analysis as it's being generated.

## Prerequisites

1. First, fetch unified trends data using `/unified-trends` endpoint
2. The AI endpoints retrieve the latest trends from MongoDB and analyze them
3. Requires authentication (Bearer token)
4. Requires `OPENAI_API_KEY` to be configured in `.env`

## API Request

### Request Body (Same for both endpoints)

```json
{
  "country_code": "US",
  "category": "technology",  // Optional
  "time_range": "7d"         // Options: '24h', '7d', '30d', '90d'
}
```

## Frontend Integration Examples

### 1. JavaScript Fetch API with Stream Reading

```javascript
async function streamAIInterpretation(countryCode, category, timeRange, authToken) {
  const response = await fetch('http://localhost:8000/ai-interpretation', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      country_code: countryCode,
      category: category,
      time_range: timeRange
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    const chunk = decoder.decode(value, { stream: true });

    // Display the chunk in your UI
    displayChunk(chunk);
  }
}

function displayChunk(chunk) {
  const outputElement = document.getElementById('ai-output');
  outputElement.textContent += chunk;
}
```

### 2. React Component with Streaming

```javascript
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function AIInterpretation({ authToken }) {
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInterpretation = async () => {
    setIsLoading(true);
    setContent('');
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ai-interpretation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          country_code: 'US',
          category: null,
          time_range: '7d'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        setContent(prev => prev + chunk);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="ai-interpretation">
      <h2>AI Trend Interpretation</h2>

      <button
        onClick={fetchInterpretation}
        disabled={isLoading}
      >
        {isLoading ? 'Generating...' : 'Get AI Interpretation'}
      </button>

      {error && (
        <div className="error">Error: {error}</div>
      )}

      <div className="content-area">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}

export default AIInterpretation;
```

### 3. Vue.js Component with Streaming

```vue
<template>
  <div class="ai-recommendations">
    <h2>AI Marketing Recommendations</h2>

    <button
      @click="fetchRecommendations"
      :disabled="isLoading"
    >
      {{ isLoading ? 'Generating...' : 'Get Recommendations' }}
    </button>

    <div v-if="error" class="error">
      Error: {{ error }}
    </div>

    <div class="content-area" v-html="renderedMarkdown"></div>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  name: 'AIRecommendations',
  props: {
    authToken: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      content: '',
      isLoading: false,
      error: null
    };
  },
  computed: {
    renderedMarkdown() {
      return marked(this.content);
    }
  },
  methods: {
    async fetchRecommendations() {
      this.isLoading = true;
      this.content = '';
      this.error = null;

      try {
        const response = await fetch('http://localhost:8000/ai-recommendations', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            country_code: 'US',
            category: 'technology',
            time_range: '7d'
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { value, done } = await reader.read();

          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          this.content += chunk;
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.content-area {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  min-height: 200px;
  white-space: pre-wrap;
}

.error {
  color: red;
  padding: 10px;
  margin: 10px 0;
}
</style>
```

### 4. Angular Component with Streaming

```typescript
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { marked } from 'marked';

@Component({
  selector: 'app-ai-interpretation',
  template: `
    <div class="ai-interpretation">
      <h2>AI Trend Interpretation</h2>

      <button
        (click)="fetchInterpretation()"
        [disabled]="isLoading"
      >
        {{ isLoading ? 'Generating...' : 'Get AI Interpretation' }}
      </button>

      <div *ngIf="error" class="error">
        Error: {{ error }}
      </div>

      <div class="content-area" [innerHTML]="renderedContent"></div>
    </div>
  `,
  styles: [`
    .content-area {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      min-height: 200px;
    }
  `]
})
export class AIInterpretationComponent {
  content = '';
  renderedContent = '';
  isLoading = false;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  async fetchInterpretation() {
    this.isLoading = true;
    this.content = '';
    this.error = null;

    const authToken = localStorage.getItem('auth_token');

    try {
      const response = await fetch('http://localhost:8000/ai-interpretation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          country_code: 'US',
          category: null,
          time_range: '7d'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        this.content += chunk;
        this.renderedContent = marked(this.content) as string;
      }
    } catch (err: any) {
      this.error = err.message;
    } finally {
      this.isLoading = false;
    }
  }
}
```

## Response Format

Both endpoints return streaming text in **Markdown format** with structured sections.

### AI Interpretation Response Sections

1. **Overview** - Brief summary of trends
2. **Key Patterns** - Major themes across platforms
3. **Platform Insights**
   - Google Trends analysis
   - YouTube content analysis
   - TikTok viral patterns
4. **Emerging Topics** - New or rapidly growing trends
5. **Audience Behavior** - User interests and behavior insights
6. **Temporal Analysis** - How trends vary over time

### AI Recommendations Response Sections

1. **Content Strategy** - Content themes and format recommendations
2. **Audience Targeting** - Target segments and demographics
3. **Campaign Ideas** - 3-5 specific campaign concepts
4. **SEO & Keywords** - High-priority keywords and topics
5. **Social Media Strategy** - Platform-specific tactics
6. **Quick Wins** - Immediate actionable opportunities
7. **Risk Mitigation** - Cautions and declining trends

## Error Handling

### Common Errors

**404 - No Trends Data Found**
```json
{
  "error": "No trends data found for US with the specified filters. Please fetch unified trends first using /unified-trends endpoint.",
  "status_code": 404,
  "timestamp": "2025-11-18T10:00:00.000000Z"
}
```

**Solution**: Call `/unified-trends` endpoint first to populate data.

**401 - Unauthorized**
```json
{
  "error": "Invalid authentication credentials",
  "status_code": 401,
  "timestamp": "2025-11-18T10:00:00.000000Z"
}
```

**Solution**: Ensure valid Bearer token is included in Authorization header.

**500 - Service Not Configured**
```json
{
  "error": "AI analysis service not initialized",
  "status_code": 500,
  "timestamp": "2025-11-18T10:00:00.000000Z"
}
```

**Solution**: Set `OPENAI_API_KEY` in your `.env` file.

## Complete Workflow

1. **Fetch Trends Data**
   ```javascript
   // First, get unified trends data
   await fetch('/unified-trends', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       country_code: 'US',
       category: 'technology',
       time_range: '7d'
     })
   });
   ```

2. **Get AI Interpretation** (streaming)
   ```javascript
   await streamAIInterpretation('US', 'technology', '7d', token);
   ```

3. **Get AI Recommendations** (streaming)
   ```javascript
   await streamAIRecommendations('US', 'technology', '7d', token);
   ```

## Styling the Output

Since the response is in Markdown, you can use any Markdown renderer:

- **React**: `react-markdown` package
- **Vue**: `marked` or `markdown-it` package
- **Angular**: `ngx-markdown` package
- **Vanilla JS**: `marked.js` library

Example CSS for the output:

```css
.ai-content {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
}

.ai-content h1 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.ai-content h2 {
  color: #34495e;
  margin-top: 24px;
}

.ai-content ul {
  list-style-type: disc;
  margin-left: 20px;
}

.ai-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
}

.ai-content strong {
  color: #2980b9;
}
```

## Performance Tips

1. **Show Loading State**: Display a spinner or loading animation while streaming
2. **Debounce Updates**: If rendering is slow, debounce the updates (e.g., update every 100ms)
3. **Cancel Requests**: Implement request cancellation if user navigates away
4. **Cache Results**: Cache AI responses to avoid redundant API calls

## Rate Limiting

OpenAI API has rate limits. Consider:
- Caching responses for repeated queries
- Adding a cooldown period between requests
- Displaying estimated wait time to users

## Security Notes

1. **Never expose OpenAI API key** in frontend code
2. **Always validate user authentication** (handled by Bearer token)
3. **Implement rate limiting** on your backend
4. **Monitor API usage costs** from OpenAI dashboard

## Testing

Test the streaming endpoints using cURL:

```bash
# AI Interpretation
curl -X POST http://localhost:8000/ai-interpretation \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "category": null,
    "time_range": "7d"
  }'

# AI Recommendations
curl -X POST http://localhost:8000/ai-recommendations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "category": "technology",
    "time_range": "7d"
  }'
```

You should see the response streaming in real-time!
