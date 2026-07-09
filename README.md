# StaffDocx 🎓

StaffDocx is a cross-platform desktop application built for school administrators to easily manage and generate "Confidential Reports" for staff members. It takes employee data from a provided CSV and allows the principal/admin to fill out evaluation metrics before generating a perfectly formatted, print-ready PDF document.

## Features ✨
- **Rapid Search**: Instantly search through hundreds of staff members.
- **Dynamic PDF Generation**: Automatically inserts the school's logo, employee details, and evaluation metrics into a neatly formatted PDF.
- **Customizable Save Locations**: Leaves no messy artifact folders behind. You choose exactly where to save your generated reports.
- **Standalone Execution**: Can be bundled into a `.exe` so end-users do not need to install Python.
- **Modern UI**: Clean, light-themed interface built using PySide6.

---

## 🚀 Getting Started

### Prerequisites
You will need to have [Python](https://www.python.org/downloads/) installed, as well as the ultra-fast package manager `uv`. 

If you do not have `uv` installed, run:
```bash
pip install uv
```

### Installation
Clone this repository and let `uv` handle the dependencies automatically when you run the app:
```bash
git clone https://github.com/your-username/staffdocx.git
cd staffdocx
```

### Running Locally
To launch the application locally, you can use the provided Makefile:
```bash
make run
```
Or use `uv` directly:
```bash
uv run ./main.py
```

---

## 🛠️ Building the Standalone Executable
If you are distributing this software to users who do not have Python installed, you can build a standalone executable file (e.g., `StaffDocx.exe`).

### For Windows
You **must** run this command on a Windows machine to generate a `.exe`.
```bash
make build-windows
```

### For Linux
```bash
make build-linux
```

Once the build finishes, you will find your standalone application inside the newly created `dist/` folder!

---

## 📂 Project Structure

```
staffdocx/
├── assets/                  # Contains static assets (e.g., app_icon.png, logo.png)
├── services/
│   ├── csv_service.py       # Handles reading and filtering CSV data
│   └── pdf_service.py       # ReportLab logic for PDF generation
├── ui/
│   └── main_window.py       # PySide6 layout and styling
├── utils/
│   ├── settings.py          # Configuration saving/loading (e.g. remembering the last CSV)
│   └── validator.py         # Input validation
├── main.py                  # Application entry point
├── Makefile                 # Shortcut commands for running and building
├── pyproject.toml           # Project metadata and dependencies (managed by uv)
└── README.md
```

## Adding the School Logo to PDFs
To ensure the PDF output includes the school's logo at the top:
1. Obtain the school logo in `.png` format.
2. Name it `logo.png`.
3. Place it inside the `assets/` directory (`assets/logo.png`).
The PDF generator will automatically detect and center it!
