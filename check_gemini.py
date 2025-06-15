# check_gemini.py
import os
import google.generativeai as genai

def main():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY is not set in the environment.")
        return

    genai.configure(api_key=key)
    try:
        models = genai.list_models()
    except Exception as e:
        print("❌ Failed to list models:", e)
        return

    print("✅ Available Gemini models:")
    for m in models:
        methods = ", ".join(m.supported_generation_methods)
        print(f"• {m.name}   (supports: {methods})")

if __name__ == "__main__":
    main()
