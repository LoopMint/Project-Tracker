# Journalist Newsworthiness Agent

An AI-powered agent that evaluates press releases for likelihood of journalist interest and coverage in Singapore mainstream, business, and alternative media platforms.

## 🏃 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# 3. Run the Streamlit app
streamlit run journalist_agent_streamlit.py
```

## Features

### 📊 Comprehensive 8-Criteria Scoring

- **Timeliness** (15% weight): Is the announcement time-sensitive?
- **Impact** (20% weight): How many people/businesses affected?
- **Novelty** (15% weight): Is it a new/unique development?
- **Controversy** (10% weight): Does it touch on contentious issues?
- **Singapore Relevance** (20% weight): How relevant to SG context?
- **Human Interest** (10% weight): Does it resonate emotionally?
- **Credibility** (5% weight): Is it from a credible source?
- **Clarity** (5% weight): Is the message clear?

### 🏢 Platform Identification

Automatically identifies which media platforms would be most interested:

- **Mainstream**: Channel NewsAsia, Straits Times, Today
- **Tech Media**: Tech in Asia, DZone, Singapore tech publications
- **Business**: Business Times, Singapore Business Review
- **Industry-Specific**: Vertical industry publications
- **Alternative**: Mothership, New Media, other platforms

### 💡 Actionable Improvement Suggestions

- Prioritized by impact
- Specific recommendations with examples
- Focuses on weakest scoring areas

### 👥 Journalist Targeting

Recommends specific types of journalists to target at each platform:
- Tech reporters
- Business/finance writers
- Enterprise journalists
- Industry specialists

### 🎬 Story Angles

Extracts and suggests the most compelling angles for journalists to cover.

## Scoring Tiers

- 🟢 **8.0+**: Highly Newsworthy - Ready for distribution
- 🟢 **6.5-7.9**: Newsworthy - Minor refinements suggested
- 🟡 **5.0-6.4**: Moderately Newsworthy - Improvements needed
- 🟠 **3.0-4.9**: Low Newsworthiness - Significant revisions recommended
- 🔴 **<3.0**: Not Newsworthy - Major repositioning needed

## API Usage

```python
from journalist_newsworthiness_agent import JournalistNewsworthinessAgent

agent = JournalistNewsworthinessAgent()
report = agent.evaluate_press_release("Your press release text here...")

print(f"Score: {report.overall_score}/10")
print(f"Tier: {report.tier.value}")
print(f"Primary platforms: {[p.value for p in report.primary_platforms]}")

for improvement in report.improvements:
    print(f"\n{improvement.category}: {improvement.recommendation}")
```
