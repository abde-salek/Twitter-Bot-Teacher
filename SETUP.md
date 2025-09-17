# 🔧 Setup and Usage Guide

## Quick Start (No API Keys Required)

If you just want to test the bot locally without setting up API keys, you can use **mock mode**:

```bash
# Clone the repository
git clone https://github.com/abde-salek/Twitter-Bot-Teacher.git
cd Twitter-Bot-Teacher

# Install dependencies
pip install -r requirements.txt

# Run in mock mode (no API calls made)
python main.py --mock
```

This will:
- Use the pre-populated list of 100 Flutter concepts
- Generate realistic tweets (but not post them)
- Generate sample code snippets
- Skip image generation
- Progress through the concept list day by day

## Full Setup (With API Keys)

### 1. Get API Keys

**Twitter API** (required for posting tweets):
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app with Read + Write permissions
3. Generate API keys and access tokens

**Groq API** (required for AI-generated content):
1. Go to [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
CONSUMER_KEY=your_actual_twitter_consumer_key
CONSUMER_SECRET=your_actual_twitter_consumer_secret
ACCESS_TOKEN=your_actual_twitter_access_token
ACCESS_TOKEN_SECRET=your_actual_twitter_access_token_secret
GROQ_API_KEY=your_actual_groq_api_key
```

### 3. Run the Bot

```bash
# Full mode with API calls
python main.py

# Mock mode for testing
python main.py --mock
```

## How It Works

### Two Operating Modes

**1. API Mode (with valid keys):**
- Generates new Flutter concepts dynamically using Groq AI
- Creates unique, educational tweets for each concept
- Generates realistic code examples
- Creates code images using Carbon
- Posts everything to Twitter
- Adds new concepts to the concept database

**2. Mock/Offline Mode (without API keys):**
- Uses the pre-populated list of 100 Flutter concepts
- Cycles through concepts sequentially based on day counter
- Generates sample tweets and code (no AI calls)
- Skips image generation and Twitter posting
- Perfect for testing and development

### Concept Database

The bot includes a comprehensive list of Flutter concepts in `data/flutter_concepts.json`:
- 100 educational topics from basic to advanced
- Covers widgets, state management, architecture patterns, and more
- Curated for educational value and practical application

### Day Counter

The bot tracks progress in `data/day_counter.txt`:
- Increments after each successful run
- In offline mode: cycles through the concept list
- In API mode: tracks total concepts generated
- Reset to `1` to start over

## Troubleshooting

### "Consumer key must be string or bytes, not NoneType"
- **Solution**: Use mock mode (`python main.py --mock`) or add valid Twitter API keys to `.env`

### "Failed to initialize Groq client"
- **Solution**: Add valid Groq API key to `.env` or use mock mode

### Empty concepts or repeated concepts
- **Fixed**: Bot now includes 100 pre-populated concepts and proper cycling logic

### Tweet length issues
- **Fixed**: Adaptive tweet templates ensure proper length (170-200 characters)

### Image generation fails
- **Expected**: Images are skipped in mock mode
- **With API keys**: Requires Firefox/Chrome browser for Carbon screenshots

## Development

### Running Tests
```bash
# Test several runs in mock mode
python main.py --mock
python main.py --mock
python main.py --mock
```

Each run should:
- Use a different concept from the list
- Generate proper tweet length
- Increment day counter
- Show no validation errors

### Adding New Concepts
Edit `data/flutter_concepts.json` to add new educational topics:
```json
[
  "StatelessWidget Basics",
  "Your New Concept Here",
  "Another Concept"
]
```

### Resetting Progress
Set day counter back to day 1:
```bash
echo "1" > data/day_counter.txt
```

## API Limits and Costs

- **Twitter API**: Free tier allows limited posts per month
- **Groq API**: Free tier includes generous token allowances
- **Mock mode**: Completely free, no API calls made

## Security

- Never commit real API keys to version control
- Use environment variables for all credentials
- The `.env` file is excluded from git by `.gitignore`