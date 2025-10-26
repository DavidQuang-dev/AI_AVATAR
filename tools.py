import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


@function_tool()
async def get_weather(
    context: RunContext,
    city: str) -> str:
    """Fetches the current weather for a given city
    """
    try:
        response = requests.get(f"http://wttr.in/{city}?format=3")
        if response.status_code != 200:
            logging.error(f"Failed to fetch weather data: {response.status_code}")
            return f"Sorry, I couldn't fetch the weather information for {city}."
        logging.info(f"Weather data for {city}: {response.text.strip()}")
        return response.text.strip()
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data for {city}: {e}")
        return f"An error occurred while fetching the weather information for {city}."

@function_tool()
async def search_web(
    context: RunContext,
    query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Web search results for query '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error performing web search for query '{query}': {e}")
        return f"An error occurred while performing the web search for '{query}'."

@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None) -> str:
    """
    Send an email throught Gmail SMTP.

    Args:
        to_email (str): Recipient email address.
        subject (str): Subject of the email.
        message (str): Body of the email.
        cc_email (Optional[str]): CC email address.
    """

    try: 
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.getenv("MAIL_USER")
        gmail_password = os.getenv("MAIL_PASSWORD")

        if not gmail_user or not gmail_password:
            logging.error("Gmail user or password not set.")
            return "Failed to send email: Gmail credentials not set."

        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        # Attach the message body
        msg.attach(MIMEText(message, "plain"))

        # Connect to the Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
            
        # Send the email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()

        logging.info(f"Email sent to {to_email} with subject '{subject}'")
        return f"Email successfully sent to {to_email}."

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Authentication error while sending email to {to_email}: {e}")
        return f"Failed to send email to {to_email} due to authentication error."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred while sending email to {to_email}: {e}")
        return f"Failed to send email to {to_email} due to SMTP error."
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {e}")
        return f"An error occurred while sending the email to {to_email}."