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
Daily_bot/
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
├── .env                    # API keys (excluded via .gitignore)
├── main.py                 # Entry point for local testing
├── requirements.txt        # Python dependencies
│
├── .github/
│   └── workflows/
│       └── tweet.yml       # GitHub Actions workflow
│
└── README.md               # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/Twitter-Bot-Teacher.git
cd Twitter-Bot-Teacher
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```
### 3. Add Twitter API Keys
-Create a .env file in the root
-Use the same structure on '.env.example' just replace the fields with your actual keys

### 4. Test Locally
```
python main.py
```

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
- [] i know this is basic level but i didn't wanna think to much about it, and this can easily scale
- [] Respond using the smae Grok API to 5 tweet/day that asks a question about Our concept

  📜 License
This project is open source under the MIT License.

  🙌 Contributing
Contributions, issues, and feature requests are welcome. Please open a pull request or create an issue to get started.
  **Made with 💙 for Flutter learners around the world**
