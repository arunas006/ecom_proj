import importlib.metadata
packages = [
    "langchain",
    "python-dotenv",
    "ipykernel",
    "langchain-groq",
    "langchain-google-genai",
    "langchain-community",
    "faiss-cpu",
    "structlog",
    "PyMuPDF",
    "pylint",
    "langchain-core",
    "pytest",
    "streamlit",
    "fastapi",
    "uvicorn",
    "python-multipart",
    "docx2txt",
    "pypdf",
    "beautifulsoup4",
    "html5lib",
    "jinja2",
    "lxml",
    "selenium",
    "undetected-chromedriver",
    "langchain_astradb"
]
for pkg in packages:
    try:
        version = importlib.metadata.version(pkg)
        print(f"{pkg}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg} (not installed)")