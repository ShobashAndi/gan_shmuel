from flask import Flask, request, jsonify

import os

import subprocess

import smtplib

from email.message import EmailMessage



app = Flask(__name__)



# Git Configuration

GIT_REPO = "https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main"

LOCAL_REPO_PATH = "/home/andishobash/Desktop/orange-team-gan-shmuel-main"

SERVICES = ["weight", "billing"]

ZOHO_EMAIL_PASSWORD = "Maxops1313!"



# Zoho Mail Configuration

EMAIL_SENDER = "orange.team.ci@zohomail.com"

EMAIL_PASSWORD = ZOHO_EMAIL_PASSWORD  # Securely read from environment variable

SMTP_SERVER = "smtp.zoho.com"

SMTP_PORT = 587




@app.route('/webhook', methods=['POST'])

def github_webhook():

    payload = request.json

    event_type = request.headers.get('X-GitHub-Event')



    if event_type == "pull_request":

        action = payload.get("action", "")

        

        if action == "closed" and payload.get("pull_request", {}).get("merged", False):

            branch = payload["pull_request"]["base"]["ref"]
            print(branch)

            commit_id = payload["pull_request"]["head"]["sha"]

            # Run git show and capture output
            subprocess.run(["git", "fetch", "--all"], check=True) # to get all the commits
            
            result = subprocess.run(
                ["git", "-C", LOCAL_REPO_PATH, "show", "--no-patch", "--pretty=format:%an|%ae", commit_id],
                capture_output=True,
                text=True,
                check=True
            )

            # Extract Name and Email
            output = result.stdout.strip()  # Remove extra spaces/newlines
            github_username, developer_email = output.split("|")
            

            print(f"🔹 Merge detected on branch: {branch} by {github_username} ({developer_email})")



            try:

                pull_latest_code(branch)

                run_ci_pipeline(branch,github_username,developer_email)

                if branch == "billing" or branch == "weight" or branch == "devops":
                    send_email(

                    subject=f"✅ CI Success for {branch} by {github_username}",

                    body="CI pipeline completed successfully for your merged PR.",

                    receiver=developer_email

                     )
                elif branch == "main":
                    deploy_to_production(github_username,developer_email)

                return jsonify({"message": "CI pipeline ran successfully"}), 200



            except subprocess.CalledProcessError as e:

                error_message = f"CI pipeline failed: {str(e)}"

                print(f"❌ {error_message}")

                send_email(

                    subject=f"❌ CI Failure for {branch} by {github_username}",

                    body=f"CI pipeline failed for your merged PR.\n\nError:\n{error_message}",

                    receiver=developer_email

                )

                return jsonify({"message": "CI pipeline failed", "error": str(e)}), 500
            
        elif action == "closed" and not payload.get("pull_request", {}).get("merged", False):
            tobranch = payload["pull_request"]["base"]["ref"]
            branch = payload["pull_request"]["head"]["ref"]
            name = payload["pull_request"]["head"]["user"]["login"]
            print(f"⛓️  PR closed on branch: {tobranch} from {branch} by {name}")

        else:
            tobranch = payload["pull_request"]["base"]["ref"]
            branch = payload["pull_request"]["head"]["ref"]
            name = payload["pull_request"]["user"]["login"]
            print(f"🚀 PR detected on branch: {tobranch} from {branch} by {name}")


    return jsonify({"message": "Not a relevant event"}), 200



def pull_latest_code(branch):

    if not os.path.exists(LOCAL_REPO_PATH):

        print(f"Cloning repository {GIT_REPO}...")

        subprocess.run(["git", "clone", GIT_REPO, LOCAL_REPO_PATH], check=True)

    else:

        print(f"Pulling latest changes in {LOCAL_REPO_PATH}...")

        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "fetch"], check=True)

        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "checkout", "--track", "-B", branch, "origin/" + branch], check=True) # to ensure we pull from the right branch

        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull", "origin", branch], check=True)  # Pull specific branch



def run_ci_pipeline(branch, github_username, developer_email):
    """
    Runs CI pipeline for the given branch.
    If it's a test branch, it uses `docker-compose.test.yml`.
    If it's the main branch, it uses `docker-compose.product.yml`.
    """

    print(f"🔧 Running CI pipeline for branch: {branch}")

    compose_file = "docker-compose.test.yml" 

    try:
        print(f"🚀 Using compose file: {compose_file}")
        subprocess.run(["docker-compose", "-f", compose_file, "build"], cwd=LOCAL_REPO_PATH, check=True)
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], cwd=LOCAL_REPO_PATH, check=True)

        print("✅ Services started successfully.")

        if compose_file == "docker-compose.test.yml":
            print("🚀 Running API Tests for Billing & Weight...")

            test_services = {
                "weight_app_test":"/weight/testing/main_test.py",
            }

            for service, test_script in test_services.items():
                print(f"🔍 Running tests in {service}...")

                test_command = [
                    "docker", "exec", "-i", service, "python3", test_script
                ]

                try:
                    subprocess.run(test_command, check=True)
                    print(f"✅ Tests passed in {service}!")

                except subprocess.CalledProcessError as e:
                    print(f"❌ Tests failed in {service}: {str(e)}")

                    send_email(
                        subject=f"❌ CI Test Failure for {branch} by {github_username}",
                        body=f"Tests failed in {service} during CI pipeline.\n\nError:\n{str(e)}",
                        receiver=developer_email
                    )

                    subprocess.run(["docker-compose", "-f", compose_file, "down"], cwd=LOCAL_REPO_PATH, check=True)
                    return  # Stop further execution if tests fail

        subprocess.run(["docker-compose", "-f", compose_file, "down"], cwd=LOCAL_REPO_PATH, check=True)
        print("✅ CI pipeline completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ CI pipeline failed: {str(e)}")

        send_email(
            subject=f"❌ CI Failure for {branch} by {github_username}",
            body=f"CI pipeline failed for your merged PR.\n\nError:\n{str(e)}",
            receiver=developer_email
        )




def send_email(subject, body, receiver):

    msg = EmailMessage()

    msg.set_content(body)

    msg["Subject"] = subject

    msg["From"] = EMAIL_SENDER

    msg["To"] = receiver



    print(f"📧 Sending email to {receiver} via Zoho...")



    try:

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:

            smtp.ehlo()

            smtp.starttls()

            smtp.ehlo()

            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

            smtp.send_message(msg)

        print("✅ Email sent successfully.")

    except Exception as e:

        print(f"❌ Email failed: {e}")

def deploy_to_production(github_username,developer_email):
    compose_file = "docker-compose.prod.yml" 

    subprocess.run(["docker-compose", "-f", compose_file, "down"], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["docker-compose", "-f", compose_file, "build"], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], cwd=LOCAL_REPO_PATH, check=True)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5050)