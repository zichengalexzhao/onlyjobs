# backend/services/process_emails/classifier_logic.py
# Purpose: This is the core "intelligence" module.

# Functionality: It initializes the Vertex AI client and loads the Gemini 2.5 Flash model. It contains the is_job_application function (though main.py might bypass it if the primary check is in classify_email) and, most importantly, the classify_email function. This function takes raw email content, sends it to Gemini, and parses Gemini's response into structured job application details (Company, Job Title, Status, Location).

import vertexai
from vertexai.generative_models import GenerativeModel
import os # Added for config import

# Import configuration (assuming config.py is at the backend root)
# You might need to adjust sys.path if importing from parent directory in a complex setup.
# For Cloud Run, you'd typically pass these as environment variables or rely on Application Default Credentials.
# For simplicity, let's assume direct import for now, or use os.environ.get for env vars
# --- FIX APPLIED HERE ---
from config import PROJECT_ID, LOCATION # Corrected import to find config.py from project root

# Initialize Vertex AI — Gemini models must use a supported region like us-central1
vertexai.init(project=PROJECT_ID, location=LOCATION) # Use config variables
gemini_model = GenerativeModel("gemini-2.5-flash") # As per your code

def is_job_application(snippet: str) -> bool:
    """Determine if an email snippet is related to a job application."""
    prompt = (
        "Determine if this email snippet is related to a job application "
        "(e.g., confirmation, rejection, interview). Return only 'Yes' or 'No'.\n\n"
        f"Snippet:\n{snippet}"
    )
    response = gemini_model.generate_content(prompt)
    return response.text.strip().lower() == "yes"

def classify_email(email_content: str) -> str:
    """
    Analyze an email and extract job application details if applicable.

    Returns:
        - Extracted fields in format:
            Company: ...
            Job Title: ...
            Location: ...
            Status: ...
        - Or "Not Job Application" if irrelevant.
    """
    prompt = (
        "You are an expert at analyzing job application emails. "
        "If the email is not job-related, return only: 'Not Job Application'.\n"
        "If it is, extract the following in this format:\n"
        "Company: [company name]\n"
        "Job Title: [job title]\n"
        "Location: [location]\n"
        "Status: [Applied, Interviewed, Declined, Offer, or Unknown]\n\n"
        f"Email Content:\n{email_content[:4000]}"
    )
    response = gemini_model.generate_content(prompt)
    text = response.text.strip()

    if not text.lower().startswith("company:"):
        return "Not Job Application"

    return text