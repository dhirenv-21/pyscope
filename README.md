# ⬡ PyScope — Code Execution & Profiling Tool

> A premium, IDE-style web application for real-time code execution tracing, performance profiling, and cross-language algorithm comparison.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🔍 Step-by-Step Execution Tracing** — Walk through Python code line-by-line with variable inspection
- **📊 Real-Time Performance Graphs** — Memory, CPU, GPU, and execution step monitoring
- **⚖️ Cross-Language Comparison** — Compare algorithms across Python, C, C++, Java, and JavaScript
- **🧠 Smart Insights Engine** — Automated performance analysis and optimization suggestions
- **🌳 Call Stack Visualization** — See function call hierarchies in real-time
- **🎨 Premium IDE Interface** — Dark/light theme with a polished, modern design

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pyscope.git
cd pyscope

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Optional: Desktop Launcher
```bash
python launcher.py
```

### Optional: Build a Standalone .exe
```bash
pip install pyinstaller
pyinstaller pyscope.spec
```
The executable is written to `dist/`.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit, Custom CSS |
| Execution Engine | Python `sys.settrace`, subprocess |
| Profiling | `psutil`, `tracemalloc`, `GPUtil` |
| Visualization | Matplotlib, NumPy |
| Multi-Language | C/C++ (gcc/g++), Java (javac), Node.js |

## 📁 Project Structure

```
pyscope/
├── app.py                 # Main Streamlit application & page router
├── execution_engine.py    # Python code tracer & profiler
├── multi_lang_runner.py   # Cross-language execution engine
├── insights.py            # Performance analysis & insights generator
├── graph_utils.py         # Matplotlib graph builders
├── ui_components.py       # HTML/CSS UI component renderers
├── ui_styles.py           # Complete CSS design system
├── launcher.py            # Desktop launcher script
├── pyscope.spec           # PyInstaller build spec
├── requirements.txt       # Python dependencies
├── main_25.py … main_100.py  # Milestone prototypes (25% → 100%)
├── execution_monitor.py   # Earliest tracer prototype
├── docs/                  # Abstract, review slides and final report
└── .streamlit/
    └── config.toml        # Streamlit server configuration
```

## 📸 Screenshots

> Run the app locally to experience the full premium interface!

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Dhire** — Built as an EOC Project @ Amrita University
