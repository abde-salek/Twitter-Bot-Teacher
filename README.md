# 🐦 Daily Tweeter Bot

An automated Twitter bot that posts daily tweets explaining a concept of a domain (i'm taking Flutter as example)
pre-listed with text and code example in a picture using 'Carbon.now.sh' as a TEXT_CODE -TO- IMAGE.
Perfect for developers who want to grow their Flutter knowledge consistently.

---

## 📌 Features

- 🚀 **One Daily Tweet**: Posts a Flutter tip every day
- 🧠 **Structured Concepts**: Beginner to intermediate Flutter topics
- 🔄 **Hashtag Rotation**: Uses trending dev hashtags like `#Flutter`, `#coding`, and `#developer`
- 📅 **Day Counter**: Tracks posting progress with a simple day tracker
- 🖼️ **(Optional)** Code-to-image conversion support
- ☁️ **GitHub Actions**: Fully automated scheduling via GitHub workflows

---

## 📁 Project Structure
```bash
Twitter-Bot-Teacher/
├── python/                  # Python logic
│   ├── generate_code.py     # Generates tweet content
│   ├── post_tweet.py        # Handles posting to Twitter
│   ├── tweet_generator.py   # Coordinates tweet logic
│   ├── code_to_image.py     # (Optional) Converts code to images
│   └── __pycache__/         # Python bytecode cache
│
├── data/
│   ├── flutter_concepts.json  # JSON list of Flutter concepts
│   └── day_counter.txt        # Tracks current tweet day number
│
├── .env                     # API keys (excluded via .gitignore)
├── main.py                  # Entry point for local testing
├── requirements.txt         # Python dependencies
├── setup_env.py             # Helper script for environment setup
├── remove_geckodriver.py    # Script to remove incompatible geckodriver
│
├── run_bot.bat              # Windows batch file to run the bot
├── run_bot_mock.bat         # Windows batch file to run in mock mode
├── setup.bat                # Windows batch file for setup
├── remove_geckodriver.bat   # Windows batch file to fix geckodriver
│
├── .github/
│   └── workflows/
│       └── tweet.yml        # GitHub Actions workflow
│
└── README.md                # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/Twitter-Bot-Teacher.git
cd Twitter-Bot-Teacher
```

### 2. Quick Start with Batch Files (Windows)

This project comes with convenient batch files for Windows users:

1. **Setup**: Run `setup.bat` to install dependencies and configure your environment
   ```
   setup.bat
   ```

2. **Run the Bot**: Use `run_bot.bat` to start the bot
   ```
   run_bot.bat
   ```

3. **Test Mode**: For testing without making API calls, use mock mode
   ```
   run_bot_mock.bat
   ```

4. **Fix GeckoDriver**: If you encounter Firefox compatibility issues
   ```
   remove_geckodriver.bat
   ```
   Note: Run this as Administrator

### 3. Manual Setup

```bash
pip install -r requirements.txt
python setup_env.py
```

### 4. Setup Environment and API Keys

Run the automated setup script:
```bash
python setup_env.py
```

This script will:
- Create a `.env` file with your Twitter API credentials
- Check if your web drivers (Chrome/Firefox) are installed and working

Alternatively, manually create a `.env` file with:
```
GROQ_API_KEY=your_groq_api_key_here
CONSUMER_KEY=your_twitter_api_key_here
CONSUMER_SECRET=your_twitter_api_secret_here
ACCESS_TOKEN=your_twitter_access_token_here
ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
```

### 5. Test Locally
```bash
python main.py  # Standard mode
python main.py --mock  # Mock mode (no API calls)
```

### 6. Troubleshooting Common Issues

#### GeckoDriver Compatibility
If you encounter errors about GeckoDriver version compatibility:

1. **Automatic Fix** (Windows): Run as Administrator
   ```
   remove_geckodriver.bat
   ```

2. **Manual Fix**:
   - Run: `python remove_geckodriver.py`
   - Or download the compatible version from: https://github.com/mozilla/geckodriver/releases
   - For Firefox 140.x, use GeckoDriver 0.36.0 or later

#### Twitter API Authentication
If you get "401 Unauthorized" errors when posting tweets:

1. Verify your Twitter API credentials in `.env`
2. Check if your Twitter Developer account is active
3. Ensure your Twitter App has proper permissions (Read + Write)
4. Regenerate tokens if needed through the Twitter Developer Portal

  ☁️ Run on GitHub Actions (Recommended)
This project uses GitHub Actions to tweet daily. To enable:

1.Fork or clone the repository
2.GitHub will automatically run the workflow once per day

  💡 How It Works:
-Concepts are stored in flutter_concepts.json (Content is curated with a quality-over-quantity approach.) 
 and scheduled based on a day counter
-Each run fetches the next concept, generates a tweet, and posts it
-Tweets follow a consistent, high-quality format with descriptions, benefits, and hashtags

  ✅ To-Do (Open Source Contributors Welcome!)
 - [ ] i know this is basic level but i didn't wanna think to much about it, and this can easily scale
 - [ ] Respond using the same Grok API to 5tweet/day that asks a question about Our concept

  📜 License
This project is open source under the MIT License.

  🙌 Contributing
Contributions, issues, and feature requests are welcome. Please open a pull request or create an issue to get started.
  **Made with 💙 for Flutter learners around the world**
