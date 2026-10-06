import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0):
    groq_key = os.getenv("GROQ_API_KEY")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq

        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        print(f"✅ Đang dùng Model Groq: {model_name}")
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            api_key=groq_key,
            max_retries=2,
        )

    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        from langchain_google_genai import ChatGoogleGenerativeAI

        model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        print(f"✅ Đang dùng Model Google: {model_name}")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=google_key,
        )

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from langchain_openai import ChatOpenAI

        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        print(f"✅ Đang dùng Model OpenAI-compatible: {model_name} ({base_url})")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=openai_key,
            base_url=base_url,
        )

    raise RuntimeError(
        "❌ Không tìm thấy API Key hợp lệ trong file .env!\n"
        "Vui lòng khai báo GROQ_API_KEY, GOOGLE_API_KEY hoặc OPENAI_API_KEY."
    )