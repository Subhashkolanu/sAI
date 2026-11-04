
# sAI — Scalable AI Interface

**A local-first desktop AI assistant powered by Ollama.**

sAI is a Windows desktop AI assistant built with Python and CustomTkinter. It is designed to make locally running AI more accessible, giving users a desktop interface for interacting with AI models running on their own computers.

The default setup uses **Ollama**, allowing users to run local AI models without depending on a paid cloud AI API.

[GitHub Repository](https://github.com/Subhashkolanu/sAI) · [V1.0.0 Release](https://github.com/Subhashkolanu/sAI/releases/tag/V1.0.0)

---

## Features

### Available in V1.0.0

- **Local AI Chat:** Interact with locally running Ollama models.
- **First-Run Setup Wizard:** Guided initial setup and model selection.
- **Conversation Memory:** Store and access conversation history locally.
- **Conversation Search:** Search through saved conversations.
- **Provider Configuration:** Configure Ollama and optional OpenAI-compatible endpoints.
- **Desktop Integration:** Perform explicitly approved desktop-opening actions.
- **Customizable Interface:** Configure application themes and provider settings.
- **Optional Vision Support:** Additional vision-related functionality through optional dependencies.

### Development status

Some capabilities are experimental or not exposed in the V1.0.0 interface. Voice is experimental and disabled in the V1.0.0 UI. Desktop automation and the separate web-search helper are not currently available as complete user-facing features.

---

## Requirements

Before installing sAI, make sure your system has:

- Windows 10 or Windows 11
- Python 3.10 or later
- Git (optional, for cloning the repository)
- [Ollama](https://ollama.com/) for local AI models
- Sufficient RAM and storage for your chosen AI model

Actual model performance depends on your computer's hardware and the model you select.

---

## Installation

### Step 1 — Install Ollama

Download and install Ollama:

https://ollama.com/download

### Step 2 — Download sAI

Clone the repository:

```powershell
git clone https://github.com/Subhashkolanu/sAI.git
cd sAI
```

Alternatively, download the source code ZIP from the GitHub repository.

### Step 3 — Create a virtual environment

```powershell
py -m venv venv
```

### Step 4 — Install dependencies

```powershell
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 5 — Download a local AI model

For example:

```powershell
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

You can choose another compatible model based on your hardware.

sAI does not automatically download AI models. You must install your preferred model through Ollama.

### Step 6 — Launch sAI

```powershell
venv\Scripts\python.exe run.py
```

On first launch, the First-Run Setup Wizard helps you check Ollama and select an installed model.

---

## Optional Vision Dependencies

To install the additional dependencies for Vision-related functionality:

```powershell
venv\Scripts\python.exe -m pip install -r requirements-vision.txt
```

For detailed setup instructions and troubleshooting, see:

[Windows Installation Guide](WINDOWS_INSTALLATION.md)

---

## Privacy and Data

sAI is designed around local-first operation.

- Local Ollama conversations are processed by the model running on your computer.
- Conversation history and profile information are stored locally.
- Application data is stored in the local `data` directory or `%LOCALAPPDATA%\sAI\data` for packaged installations.
- Choosing an external AI endpoint sends prompts to that endpoint.
- API keys for OpenAI-compatible endpoints should be configured through environment variables, not committed to the repository.

**Important:** Local-first does not mean every feature is automatically offline. External providers and online services require network access.

---

## Project Structure

```text
sAI/
├── backend/          # AI logic, providers, memory and system operations
├── frontend/         # Desktop user interface
├── assets/           # Application assets
├── tests/            # Automated tests
├── requirements.txt  # Default dependencies
├── requirements-core.txt
├── requirements-vision.txt
├── run.py            # Application launcher
├── main.py           # Main application entry point
├── sAI.spec           # PyInstaller configuration
├── installer.iss      # Windows installer configuration
└── README.md
```

---

## Run Tests

To verify the project installation:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

Check Python compilation:

```powershell
venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py
```

Check installed dependencies:

```powershell
venv\Scripts\python.exe -m pip check
```

---

## Roadmap

Future development will focus on improving reliability, usability, local AI capabilities, and the overall desktop experience.

---

## Contributing

Contributions, suggestions, bug reports, and feedback are welcome.

If you find an issue, please report it through the repository's GitHub Issues section.

---

## License

No license is currently specified. Please check the repository for licensing updates before redistributing or reusing the source code.

---

**Built by Subhash Kolanu**

[GitHub](https://github.com/Subhashkolanu) · [LinkedIn](https://www.linkedin.com/in/sai-subhash-kolanu-358ba0376/)
