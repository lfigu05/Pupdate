# To not have views.py crowded, I made a separate file for
# any Gemini-related code.

import json
from datetime import date, timedelta
from django.conf import settings
from google import genai
from google.genai import types
import time

# - asking gemini to split one big goal into smaller study steps
# - returns a list of date task pairs or an empty list if something goes wrong
def make_study_plan(goal, due_date, topics):
    today = date.today() # the day the plan starts

    # - this is the prompt with instructions sent to Gemini. the user's info is plugged in
    # - {{ and }} are doubled so the f-string prints real curly braces for the JSON example
    prompt = f"""
    A college student has this goal: {goal}
    It is due on {due_date}. Today is {today}.
    Topics to cover: {topics}

    Break this into small daily study steps, one per day, starting today and ending the day before the due date. 
    Each step should take 20-40 minutes and be specific and actionable.
    Make them actually practice stuff, like doing problems or just quizzing themselves.
    Do not just tell them to reread slides.

    Respond with ONLY a JSON list like:
    [ {{"date": "YYYY-MM-DD", "task": "short specific task"}}]
    """

    steps = None # holds Gemini's answer once we get a good one

    for attempt in range(3): #trying up to 3 times before it gives up
        try: #anything can fail so catch errors
            client = genai.Client(api_key=settings.GEMINI_API_KEY) #connect to Gemini with the key
            response = client.models.generate_content(
                model="gemini-3.8-flash", #gemini model
                contents=prompt, #prompt from above
                config=types.GenerateContentConfig(response_mime_type="application/json"), # reply in JSON to make it easier for Python
            )
            steps = json.loads(response.text)

            if isinstance(steps, dict):
                steps = next((v for v in steps.values() if isinstance(v,list)), [])

            if steps: #got a usable answer, stop retrying
                break
        except Exception as e: # if something failed
            print(f"Gemini attempt {attempt + 1} failed: {e}") # show real error in terminal
            time.sleep(2 * (attempt + 1)) # wait longer after each failure so Google's servers are able to recover
    
    if not steps: # all 3 failed
        return[] # empty isntead of crashing
    
    plan = [] # cleaned up list of steps that will be returned
    for step in steps: #go through the steps Gemini gave
        try:
            step_date = date.fromisoformat(step["date"]) #turn "2026-09-26" into a real date
            # keep the steps between today and the due date in case Gemini gets creative
            if today <= step_date < due_date:
                plan.append((step_date, step["task"])) # add it as a date task pair
        except (KeyError, ValueError): # missing date/task or the date has a bad format
            continue #skip and continue
    return plan # give the finished plan back to code that called the function