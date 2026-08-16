# Autonomous Multi-Platform AI Job Applier

This project uses an AI Agent powered by Google's Gemini 2.0 Flash model and `browser-use` to autonomously apply to jobs on platforms like LinkedIn, Wellfound, and Indeed. 

The agent handles form navigation, intelligently answers application questions using your personal data dictionary, strategically passes ATS filters, and logs successful applications to a CSV file.

## 🚀 Getting Started

### 1. Activate the Virtual Environment
Before running any scripts, you must ensure your Python virtual environment is activated. 
Open your terminal in this directory and run:
```bash
source ai_job_env/bin/activate
```
*(You should see `(ai_job_env)` at the beginning of your terminal prompt indicating it is active).*

### 2. Configure Your Credentials
You must securely store your API key and login details. 
1. Open the `.env` file located in this folder.
2. Replace the placeholder values with your actual credentials:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LINKEDIN_EMAIL=your_actual_email@example.com
LINKEDIN_PASSWORD=your_actual_password
```
*(Never share or upload this `.env` file publicly!)*

### 3. Update Your Profile Data
Open `multi_apply_agent.py` in your code editor. At the top of the file, you will see a massive dictionary called `my_profile_data`. 
- Update the skills, years of experience, current salary, and notice period to match your current situation.
- The agent uses this data as its "brain" when answering strict dropdowns or text boxes on job applications.
- You can also modify `SEARCH_KEYWORDS` and `LOCATION` right below the dictionary to change the types of jobs it targets.

## ⚙️ Running the Agent

With your environment activated, start the interactive agent by running:
```bash
python multi_apply_agent.py
```

### The Interactive Menu
When you start the script, it will ask you three questions:
1. **Platform Selection:** Choose whether to target LinkedIn, Wellfound, Indeed, or let the agent iterate through All of them sequentially.
2. **Job Limit:** Tell the agent how many applications to complete per platform before stopping (e.g., 10).
3. **Headless Mode:** 
   - Enter `y` to run the agent completely invisibly in the background.
   - Enter `n` to watch the Chrome window pop up and observe the agent clicking and typing in real-time.

## 🧠 Advanced Configuration & Tuning

If you notice the agent is struggling on a specific website, you don't need to rewrite the entire script.

Look for the `PLATFORM_CONFIGS` dictionary inside `multi_apply_agent.py`. Here you can easily add specific rules for a specific site without breaking the others:
```python
"Indeed": {
    "starting_url": "...",
    "apply_button_name": "Apply now",
    "extra_rules": (
        "- Your custom rule here.\n"
        "- Another instruction on how to handle an Indeed specific pop-up."
    )
}
```

## ⚠️ Notifications & Error Handling
- **Audible Alerts:** If the agent encounters a fatal error, gets permanently stuck on a page, or requires human intervention (like solving a complex captcha), it will beep 3 times and use text-to-speech to announce that it requires your attention. 
- **Auto-Login:** If the agent hits a login wall, it will automatically attempt to use the credentials stored in your `.env` file to log in and bypass the wall.

## 📊 Tracking
Every time the agent successfully clicks a final "Submit Application" button, it will append the Job Title, Company, and URL into `applied_jobs.csv`. You can open this file in Excel or Google Sheets to track your job hunting progress!
