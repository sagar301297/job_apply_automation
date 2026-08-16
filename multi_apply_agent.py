import asyncio
import os
import csv
import subprocess
import time
from datetime import datetime
from browser_use import Agent, Browser, ChatGoogle, Controller

# --- LOAD .ENV VARIABLES ---
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val.strip("'\"")

API_KEY = os.environ.get("GEMINI_API_KEY", "")

# =====================================================================
# 1. PROFILE DATA (Shared across all platforms)
# =====================================================================
my_profile_data = {
    "personal": {

    },
    "employment": {
        "current_role": "Senior Technical Consultant",
        "total_experience_years": "7",
        "current_ctc_lpa": "18 LPA",
        "expected_ctc_lpa": "24 LPA",
        "notice_period_days": "30", 
        "can_join_immediately": "Yes",
        "willing_to_relocate": "Yes",
        "sponsorship_required": "No"
    },
    "skills_experience_years": {
        "Python": "6",
        "Machine Learning": "2",
        "Deep Learning": "2",
        "NLP": "2",
        "RAG": "2",
        "TensorFlow": "2",
        "PyTorch": "2",
        "scikit-learn": "2",
        "Hugging Face": "2",
        "LLMs": "2",
        "Vector Databases (Milvus)": "2",
        "FastAPI": "2",
        "NodeJS": "1",
        "ReactJS": "1",
        "PHP": "7",
        "Kafka": "5",
        "Redis": "5",
        "Docker": "5",
        "Git": "6",
        "Jenkins": "4",
        "REST APIs": "6",
        "Microservices": "4",
        "Agile": "5",
        "Backend Architecture": "6"
    },
    "cover_letter_blurb": (
        "As a Results-driven AI/ML and backend engineer with 6+ years of experience, "
        "I specialize in building scalable systems using Python, NLP, RAG, and production ML "
        "(TensorFlow, PyTorch, Hugging Face). Most recently, I architected a Real-Time AI "
        "Recommendation Engine and semantic search system. I excel at designing cloud-native APIs "
        "and integrating AI solutions seamlessly into enterprise platforms. I am eager to bring my "
        "expertise in MLOps, backend architecture, and generative AI to your team."
    )
}

SEARCH_KEYWORDS = "Python AI ML Backend Engineer"
LOCATION = "India"

# =====================================================================
# 2. PLATFORM SPECIFIC CONFIGURATIONS
# =====================================================================
# You can tweak the rules for each platform individually here!

PLATFORM_CONFIGS = {
    "LinkedIn": {
        "starting_url": f"https://www.linkedin.com/jobs/search/?f_AL=true&keywords={SEARCH_KEYWORDS.replace(' ', '%20')}&location={LOCATION}",
        "apply_button_name": "Easy Apply",
        "extra_rules": (
            "- When navigating jobs, look for the job listings specifically on the left sidebar.\n"
            "- CRITICAL RULE: On the final 'Review' screen right before you click Submit, you MUST locate the 'Follow [Company]' checkbox. You MUST click it to UNCHECK it so I do not follow the company. If it is already unchecked, leave it alone. Do this on every single application."
        )
    },
    "Wellfound": {
        "starting_url": f"https://wellfound.com/jobs", 
        "apply_button_name": "Apply",
        "extra_rules": (
            "- Wellfound often has a straightforward apply process. Click 'Apply' and confirm.\n"
            "- If they ask for a custom pitch or note to the founder, use the 'cover_letter_blurb' from the dictionary."
        )
    },
    "Indeed": {
        "starting_url": f"https://in.indeed.com/jobs?q={SEARCH_KEYWORDS.replace(' ', '+')}&l={LOCATION}",
        "apply_button_name": "Apply now",
        "extra_rules": (
            "- Make sure to click jobs that say 'Easily apply' or 'Apply now' with the Indeed logo.\n"
            "- If clicking apply redirects to a completely different third-party company site, click the 'Back' button, close the modal, and skip that job."
        )
    }
}

# =====================================================================
# 3. TASK GENERATOR
# =====================================================================
def generate_task(platform_name, max_jobs):
    config = PLATFORM_CONFIGS[platform_name]
    
    env_prefix = platform_name.upper()
    login_email = os.environ.get(f"{env_prefix}_EMAIL", os.environ.get("LINKEDIN_EMAIL", ""))
    login_pass = os.environ.get(f"{env_prefix}_PASSWORD", os.environ.get("LINKEDIN_PASSWORD", ""))
    
    return f"""
You are an autonomous Job Application Assistant. Your goal is to apply to exactly {max_jobs} jobs on {platform_name}.

STARTING INSTRUCTION:
1. Immediately navigate to this URL: {config['starting_url']}
2. Do NOT go to any user profiles first.
3. Once the page loads, look at the main search bar on the platform. Verify that it contains exactly '{SEARCH_KEYWORDS}'. If it only says 'Python' or is incorrect, click the search bar, type exactly '{SEARCH_KEYWORDS}', and press Enter to reload the correct jobs.

DATA DICTIONARY:
Use this data to answer all form questions: {my_profile_data}

WORKFLOW & RULES:
1. Login Handling: If you encounter a login screen, use these credentials to sign in: Email "{login_email}" and Password "{login_pass}". Once logged in, proceed to the starting URL if needed.
2. Job Selection: Look at the job listings. Click on a job listing. Verify the title or description generally aligns with AI, ML, Data, or Backend.
3. Initiate: Click the "{config['apply_button_name']}" button.
4. Form Navigation (The Loop):
   - Answer questions using the DATA DICTIONARY.
   - If a question asks for a numeric CTC or Notice Period, use the exact numbers.
   - If a text box asks for a cover letter, pitch, or "why hire you", use the 'cover_letter_blurb'.
   - If a field is optional and you lack data, leave it blank.
   - Click "Next", "Continue", or "Review" until you reach the final submit screen.
4. Strategy for Maximizing Selection (Fallback Rules):
   - Always try to answer in the employer's favor to pass automated ATS filters.
   - If asked a Yes/No question about your willingness to do something, proficiency, or meeting a requirement, select "Yes" unless it's a hard dealbreaker (like needing sponsorship, which you don't).
   - If asked for years of experience in a specific skill NOT explicitly listed, output "1" or "2" instead of "0" so you don't get auto-rejected.
5. Resume Handling: If asked to select a Resume, choose the most recently uploaded one from the dropdown or default option.
6. Platform Specific Rules:
{config['extra_rules']}
7. Submit & Track: On the final screen, click the final Submit button. 
   IMPORTANT: AFTER clicking submit, you MUST call the 'log_job_to_csv' tool with the Job Title, Company Name, and URL.
8. Error Handling: If you get stuck on a page for more than 2 steps, click the "X" or "Discard" button to close the modal, and move to the next job on the list.
9. Termination: Keep track of successful submissions. Once you have successfully applied to {max_jobs} jobs, STOP all execution and output "Task Complete".
"""

# =====================================================================
# 4. CUSTOM ACTIONS & CONTROLLER
# =====================================================================
controller = Controller()

@controller.action('Log successful job application to the local CSV file')
def log_job_to_csv(job_title: str, company: str, platform_url: str):
    """Call this tool immediately after successfully submitting a job application."""
    csv_path = os.path.join(os.getcwd(), 'applied_jobs.csv')
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([job_title, company, platform_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    return f"Successfully logged {job_title} at {company} to CSV."

# =====================================================================
# 5. INTERACTIVE SCRIPT RUNNER
# =====================================================================
async def run_agent_for_platform(platform_name, max_jobs, headless):
    print(f"\n🚀 Starting Agent for {platform_name} (Target: {max_jobs} jobs)...")
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    
    # Launch Chrome
    chrome_args = [
        "/usr/bin/google-chrome",
        "--remote-debugging-port=9222",
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    if headless:
        chrome_args.append("--headless=new")
        
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:9222/json/version", timeout=1)
    except Exception:
        subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for browser to initialize before connecting
        time.sleep(3)

    browser = Browser(cdp_url="http://localhost:9222")
    llm = ChatGoogle(model="gemini-3.1-flash-lite", api_key=API_KEY)
    
    agent = Agent(
        task=generate_task(platform_name, max_jobs),
        llm=llm,
        browser=browser,
        controller=controller
    )
    
    # Initialize tracking CSV
    if not os.path.exists('applied_jobs.csv'):
        with open('applied_jobs.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Job Title', 'Company', 'URL', 'Timestamp'])
            
    try:
        start_time = time.time()
        await agent.run()
        os.system('spd-say "Agent has completed successfully" || echo -e "\\a\\a\\a"')
    except Exception as e:
        print(f"❌ Agent stopped due to error: {e}")
        # Trigger system bell and vocal alert for user intervention
        for _ in range(3):
            print("\a", end="", flush=True) 
            time.sleep(0.5)
        os.system('spd-say "Attention! AI Agent requires your intervention or encountered an error" || notify-send "AI Agent" "Attention required!"')
    finally:
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        minutes = int(execution_time // 60)
        seconds = int(execution_time % 60)
        
        print(f"\n✅ Finished execution phase for {platform_name}!")
        print(f"⏱️  Total Execution Time: {minutes} minutes and {seconds} seconds.")
        
        # Save the AI's thought process and DOM actions
        try:
            model_str = getattr(llm, 'model', getattr(llm, 'model_name', 'gemini')).split('/')[-1]
            log_file = f"thought_log_{platform_name}_{model_str}_{int(start_time)}.json"
            agent.history.save_to_file(log_file)
            print(f"🧠 AI thought process and memory saved to: {log_file}")
        except Exception as log_e:
            print(f"Could not save history log: {log_e}")

async def main():
    print("===========================================")
    print(" Welcome to the Multi-Platform AI Job Agent")
    print("===========================================")
    
    # Question 1: Platform
    print("\nWhich platform would you like to apply on today?")
    platforms = list(PLATFORM_CONFIGS.keys())
    for i, p in enumerate(platforms):
        print(f"{i+1}. {p}")
    print(f"{len(platforms)+1}. All (Iterate through all sequentially)")
    
    plat_choice = input("\nEnter number (default 1): ")
    try:
        plat_idx = int(plat_choice) - 1
        if plat_idx == len(platforms):
            selected_platforms = platforms
        else:
            selected_platforms = [platforms[plat_idx]]
    except:
        selected_platforms = ["LinkedIn"]

    # Question 2: Jobs Limit
    jobs_input = input("\nHow many jobs should I apply to PER PLATFORM? (default 10): ")
    try:
        max_jobs = int(jobs_input)
    except:
        max_jobs = 10

    # Question 3: Headless
    headless_input = input("\nRun in Headless mode? (Invisible background processing) [y/N]: ").lower()
    headless = headless_input.startswith('y')
    
    print("\n" + "-"*40)
    print(f"Executing for: {', '.join(selected_platforms)}")
    print(f"Jobs per platform: {max_jobs}")
    print(f"Headless mode: {headless}")
    print("-"*40)

    for platform in selected_platforms:
        await run_agent_for_platform(platform, max_jobs, headless)
        
    print("\n🎉 All tasks completed!")

if __name__ == "__main__":
    asyncio.run(main())
