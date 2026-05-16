# ChatGPT-Like UI - User Guide

## Access the Chat Interface

### URLs Available:
- **http://localhost:8000/** - Main chat interface (recommended)
- **http://localhost:8000/chat** - Alternative URL
- **http://localhost:8000/docs** - Original Swagger API documentation

## Features

### 💬 Chat Interface
- **Clean, modern design** inspired by ChatGPT
- **Real-time typing indicators** while waiting for responses
- **Dark theme** with gradient accents for better readability
- **Responsive design** works on desktop, tablet, and mobile

### ⚡ Elasticsearch Integration
- **Auto-storage** - Every query automatically stored in Elasticsearch
- **Intelligent caching** - Similar questions answered instantly from cache
- **Query history** - All your questions and answers are saved
- **Response tracking** - Each response gets a unique ID for retrieval

### 📊 Response Features

Each assistant response shows:

```
Your Question
├─ Answer (with markdown formatting)
├─ Cache Badge (⚡ CACHED or ✨ FRESH)
├─ Response ID (for later retrieval)
└─ Sources (documents used to generate answer)
```

### 🎯 Quick Tips

1. **Send Questions** - Type any question and press Enter or click Send
2. **View Cache Status** - Green badge means cached, blue means freshly generated
3. **See Sources** - Review the documents used to answer your question
4. **Clear Chat** - Click "Clear History" to reset the UI (database remains intact)
5. **View Statistics** - Click "View Stats" to see session information

### ⌨️ Keyboard Shortcuts

- **Enter** - Send message
- **Shift + Enter** - New line in message
- **Focus on input** - Automatically when page loads

## UI Components

### Header
- Title with gradient styling
- Always visible at top

### Chat Area
- Messages from user (blue, right-aligned)
- Responses from AI (dark, left-aligned)
- Smooth animations for new messages
- Auto-scrolling to latest message
- Scrollbar optimized for dark theme

### Input Area
- Text input field with placeholder
- Send button with hover effects
- Clear History button
- View Stats button

## Response Information

### Badge Types

| Badge | Meaning | Color |
|-------|---------|-------|
| ⚡ CACHED | Retrieved from cache (instant response) | Green |
| ✨ FRESH | Newly generated response | Blue |

### Response ID
- Unique identifier in Elasticsearch
- Shown as truncated version (first 8 chars)
- Use full ID from browser dev tools if needed
- Can be used to retrieve response later via API

### Sources
- Documents/knowledge used to generate answer
- Displayed as list below response
- Helps verify answer reliability
- Clickable in future versions

## Error Handling

- **Connection errors** - Displayed as red error messages
- **API failures** - Show error details with HTTP status
- **Empty responses** - Handled gracefully

## Browser Compatibility

- **Chrome/Edge** - Full support ✓
- **Firefox** - Full support ✓
- **Safari** - Full support ✓
- **Mobile browsers** - Full support with responsive design ✓

## Performance Tips

1. **Use caching** - Let similar questions benefit from cache
2. **Clear old chats** - Keeps UI responsive
3. **Batch questions** - Group related questions together

## Behind the Scenes

### What Happens When You Send a Query:

```
1. UI sends request to /api/ask
   ↓
2. API checks Elasticsearch for similar cached queries
   ├─ If found → Return cached answer (instant)
   └─ If not found ↓
3. Search knowledge base (documents index)
   ↓
4. Generate answer with OpenAI
   ↓
5. Store query + answer in Elasticsearch (documents-queries index)
   ↓
6. Return response with ID, timestamp, and sources
   ↓
7. UI displays answer with cache status and sources
```

### Database Storage

Every response stored includes:
- Query text
- Generated answer
- Source documents used
- Timestamp (ISO 8601 format)
- Document count

## Accessing API Directly

While the UI is user-friendly, you can also use the APIs directly:

### Example: Get Query History
```bash
curl "http://localhost:8000/api/query-history?limit=10&query=India"
```

### Example: Get Specific Response
```bash
curl "http://localhost:8000/api/response/LLCTMZ4BHcjDPy-9qEPO"
```

### Example: Ask Question
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Prime Minister of India?", "use_cache": true}'
```

## Statistics

The "View Stats" button shows:
- **Total Stored Queries** - All queries in Elasticsearch database
- **Current Session Messages** - Questions asked in this session
- **Cached Responses** - Answers retrieved from cache
- **Cache Rate** - Percentage of cached vs. fresh responses

## Customization

The UI can be customized by editing `chat.html`:

### Change Colors
Find the CSS section and modify gradient colors:
```css
background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
```

### Add Features
- Add export to PDF functionality
- Add conversation sharing
- Add response rating system
- Add advanced search filters

## Troubleshooting

### Chat not connecting
- Ensure FastAPI server is running: `python -m uvicorn app.main:app --reload`
- Check Elasticsearch is accessible: `curl http://localhost:9200`
- Check browser console (F12) for errors

### Responses not being stored
- Verify Elasticsearch connection works
- Check if `documents-queries` index exists
- Review Elasticsearch logs

### UI not loading
- Hard refresh page (Ctrl+F5 or Cmd+Shift+R)
- Check browser cache
- Verify file path to chat.html is correct

## Next Steps

1. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Open in browser:**
   Navigate to `http://localhost:8000/`

3. **Start chatting:**
   Ask your first question!

4. **View history:**
   Click "View Stats" or use `/api/query-history` endpoint

---

**Enjoy your ChatGPT-like AI Assistant!** 🚀
