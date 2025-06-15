from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os
import uuid
import subprocess

from code_problem.forms import CodeSubmissionForm
from home.models import Problem
from .models import CodeSubmission
from home.models import TestCase


import subprocess
import tempfile
import uuid
import os

def run_code(language, code, input_data):
    # Sanitize code: remove non-breaking spaces and non-ASCII characters
    code = ''.join(char if ord(char) < 128 else ' ' for char in code)

    file_ext = {"py": "py", "c": "c", "cpp": "cpp"}
    file_name = f"{uuid.uuid4()}.{file_ext[language]}"
    file_path = os.path.join("codes", file_name)

    with open(file_path, "w") as f:
        f.write(code)

    try:
        if language == "py":
            result = subprocess.run(["python3", file_path],
                                    input=input_data or "",
                                    text=True,
                                    capture_output=True,
                                    timeout=5)
        elif language == "c":
            exe_file = file_path.replace(".c", "")
            compile_result = subprocess.run(["gcc", file_path, "-o", exe_file],
                                            capture_output=True,
                                            text=True)
            if compile_result.returncode != 0:
                return f"Compilation Error:\n{compile_result.stderr}"
            result = subprocess.run([exe_file],
                                    input=input_data or "",
                                    text=True,
                                    capture_output=True,
                                    timeout=5)
        elif language == "cpp":
            exe_file = file_path.replace(".cpp", "")
            compile_result = subprocess.run(["g++", file_path, "-o", exe_file],
                                            capture_output=True,
                                            text=True)
            if compile_result.returncode != 0:
                return f"Compilation Error:\n{compile_result.stderr}"
            result = subprocess.run([exe_file],
                                    input=input_data or "",
                                    text=True,
                                    capture_output=True,
                                    timeout=5)
        else:
            return "Unsupported language"

        if result.returncode != 0:
            return f"Runtime Error:\n{result.stderr}"
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Time Limit Exceeded"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Clean up files
        try:
            os.remove(file_path)
            if language in ["c", "cpp"]:
                os.remove(exe_file)
        except:
            pass


@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)

    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            action = request.POST.get("action")

            # Create submission instance but don't save yet
            submission = form.save(commit=False)
            submission.user = request.user
            submission.problem = problem

            if action == "run":
                # Do not save to DB, only run the code
                output = run_code(submission.language, submission.code, submission.input_data or "")
                return render(request, "result.html", {
                    "submission": submission,
                    "output": output,
                    "is_run": True,
                })

            elif action == "submit":
                submission.save()  # Save only now
                testcases = TestCase.objects.filter(problem=problem)
                all_passed = True
                failed_test = None

                for index, test in enumerate(testcases, start=1):
                    output = run_code(submission.language, submission.code, test.input_data)
                    expected = test.output_data.strip().replace("\r\n", "\n")
                    actual = output.strip().replace("\r\n", "\n")

                    if actual != expected:
                        all_passed = False
                        failed_test = index
                        break

                if all_passed:
                    submission.verdict = "Accepted"
                    submission.output_data = "All test cases passed."
                else:
                    submission.verdict = f"Wrong Answer on Test Case {failed_test}"
                    submission.output_data = f"Output mismatch on test case #{failed_test}."

                submission.save()
                return redirect("code_problem:submission_history", user_id=request.user.id)
    else:
        form = CodeSubmissionForm()

    return render(request, "submit_code.html", {"form": form, "problem": problem})

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

@login_required
def submission_history(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    submissions = CodeSubmission.objects.filter(user__id=user_id).order_by("-timestamp")
    return render(request, "submission_history.html", {
        "submissions": submissions,
        "user_profile": user_profile
    })


import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
#from google import genai
import os

import google.generativeai as genai  # Correct import

import google.generativeai as genai
import os
from django.conf import settings

import os
import google.generativeai as genai
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import google.generativeai as genai
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import os
import re
import markdown  # new import
import google.generativeai as genai

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import CodeSubmission  # adjust if your import path is different


@login_required
@csrf_exempt
def view_code(request, submission_id):
    submission = get_object_or_404(CodeSubmission, pk=submission_id)
    ai_feedback = None  # this will hold HTML (converted from Markdown)

    if request.method == "POST" and "ai_review" in request.POST:
        # 1) Build the problem description
        problem = submission.problem
        problem_description = f"Statement: {problem.statement}\n"

        # 2) Build the prompt
        prompt = (
            "You are a code reviewer for a competitive programming judge. "
            "Given a problem and a user-submitted solution, review the code for correctness, "
            "efficiency, and coding style. Provide suggestions for improvement if needed.\n\n"
            f"Problem Description:\n{problem_description}\n\n"
            f"Language: {submission.language}\n"
            f"User Code:\n{submission.code}"
        )

        # 3) Fetch the API key from environment (or settings)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            ai_feedback = "<p style='color:red;'>⚠️ GEMINI_API_KEY is not set.</p>"
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-1.5-flash")

            try:
                response = model.generate_content(prompt)
                raw_md = response.text  # this is Markdown text (with **bold**, ```code```, etc.)

                # 4) Convert Markdown → HTML
                #    The `extensions=['fenced_code']` ensures code fences become <pre><code> blocks.
                html = markdown.markdown(
                    raw_md,
                    extensions=["fenced_code", "codehilite", "nl2br"]
                )

                # 5) (Optional) Post–processing tweaks: for example, ensure any leading/trailing <p> tags are intact
                #    You can also clean up nested tags here if you wish. For now, we trust markdown() output.
                ai_feedback = html

            except Exception as e:
                # On error, display a plain‐text fallback
                fallback = "AI review unavailable: " + str(e)
                # wrap in a <pre> so it still shows monospace
                ai_feedback = f"<pre style='color:red'>{fallback}</pre>"

    return render(request, "view_code.html", {
        "submission": submission,
        "ai_feedback": ai_feedback,
    })

