# Energy Advisor Chat Feature

## Overview

A new **💬 Energy Advisor Chat** tab has been added to the Smart Energy Advisor application. This feature allows users to have ongoing conversations with an AI energy advisor powered by Google Gemini 2.5 Flash.

## What's New

### Tab 6: Energy Advisor Chat
- **Location**: New dedicated tab (moved "About & Resources" to Tab 7)
- **Icon**: 💬
- **Purpose**: Real-time conversations about solar energy, financing, maintenance, and energy efficiency

### Key Features

#### 1. **Interactive Conversation**
- Chat history maintained throughout your session
- Context-aware responses based on previous messages in the conversation
- User messages show with 👤 avatar
- AI responses show with 🤖 avatar
- Easy-to-read message display

#### 2. **Quick Question Buttons**
Six pre-suggested questions to get started:
- "What's the best time to install solar in Kenya?"
- "How much does a 5kW system cost in Kenya?"
- "What maintenance does a solar system need?"
- "Can I get loans for solar installation?"
- "How long does a solar panel last?"
- "What's the difference between grid-tied and off-grid?"

Just click any button to instantly populate it as your question.

#### 3. **Custom Question Input**
- Large text area for typing detailed questions
- Placeholder examples to guide you
- "Send Message" button to submit queries
- "Clear Chat" button to reset conversation history

#### 4. **AI Advisor Expertise**
The advisor specializes in:
- Solar panel systems and installation
- Kenya's electricity tariffs (EPRA 2024-2026)
- Equipment selection and maintenance
- Financial aspects (ROI, payback periods, financing options)
- Environmental impact of renewable energy
- Local regulations and incentives in Kenya
- Energy efficiency and conservation tips
- Troubleshooting solar systems

#### 5. **Helpful Tips Section**
- Expandable section with guidance on getting better responses
- Topics the advisor can help with
- Tips for asking specific, detailed questions
- Advice on using the main app alongside the chat

## How to Use

### Starting a Conversation
1. Go to **Tab 6: 💬 Energy Advisor Chat**
2. Either:
   - Click one of the **Quick Question** buttons, or
   - Type your question in the text area
3. Click **📤 Send Message**
4. Wait for the AI to generate a response

### Following Up
- The advisor remembers your previous questions in the same chat session
- Ask follow-up questions for clarification
- Build context through the conversation

### Clearing the Chat
- Click **🗑️ Clear Chat** to reset and start a new conversation
- This removes all history from your current session

### Example Conversations

**Example 1: Cost Inquiry**
```
User: How much does a 5kW system cost?
Assistant: [Provides cost breakdown]
User: And what about installation costs?
Assistant: [Adds installation details]
```

**Example 2: Financing Questions**
```
User: What financing options exist in Kenya?
Assistant: [Lists various options]
User: Which one is best for someone with limited upfront capital?
Assistant: [Recommends PayGo or lease options]
```

## Technical Implementation

### New Functions

**`chat_with_gemini(user_message, chat_history=[])`**
- Manages conversation with Gemini API
- Maintains chat history for context
- Returns AI response and any error messages
- Uses system prompt specialized for energy advisory

### Session State
- Conversation stored in `st.session_state.chat_history`
- Persists while you're on the tab
- Clears on page refresh (browser) or manually via "Clear Chat" button

### AI Configuration
- **Model**: Gemini 2.5 Flash
- **Temperature**: 0.7 (balanced between creativity and consistency)
- **Context**: Full conversation history passed for coherent responses

## Integration with Other Features

The chat advisor works alongside other app features:
- **Tab 1 (Input & Quick Analysis)**: Get quick estimates there, then discuss results with the advisor
- **Tab 2 (AI Recommendation)**: Ask the advisor to explain the generated recommendations
- **Tab 3 (Financial Analysis)**: Get help interpreting financial projections
- **Tab 5 (Radiation Data)**: Ask about solar data sources and their implications

## Tips for Best Results

1. **Be Specific**: Include details about your situation
   - ❌ "How much does solar cost?"
   - ✅ "How much does a 5kW grid-tied system cost in Nairobi with battery backup?"

2. **Ask Follow-ups**: The advisor remembers context
   - ✅ "That sounds expensive. What about smaller systems?" (after asking about costs)

3. **Use with the App**: Combine tools for better insights
   - Use Tab 1 to calculate your consumption
   - Use Tab 2 to get a detailed recommendation
   - Use Tab 6 to discuss the results

4. **Provide Context**: More info = better advice
   - Your location (county/area)
   - Current consumption (monthly kWh or bill)
   - Budget constraints
   - Specific concerns

## Troubleshooting

### "API key not found" Error
- Ensure `GEMINI_API_KEY` is set in your `.env` file
- Check that the environment variable is properly loaded

### No Response or Timeout
- The API call may take 10-30 seconds
- Wait for the spinner to complete
- Check your internet connection

### Chat History Not Persisting
- Chat history only persists within a single browser session
- Refreshing the page or reopening the app will clear history
- Use "Clear Chat" button to manually reset

## Future Enhancements

Potential improvements:
- Export conversation as PDF
- Save chat history to file
- Multi-language support (Swahili)
- Integration with user profile for personalized recommendations
- Document-based context (upload photos of bills, quotes)
- Real-time data integration (current quotes, tariffs)

## Architecture

```
User Input
    ↓
chat_with_gemini() function
    ↓
Prepares conversation history + system prompt
    ↓
Calls Gemini 2.5 Flash API
    ↓
Response returned + stored in session
    ↓
Displayed with 🤖 avatar in chat UI
```

---

**Version**: 1.0
**Added**: November 24, 2025
**Status**: Active and ready for user testing
