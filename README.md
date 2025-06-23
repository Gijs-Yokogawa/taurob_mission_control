# Taurob Mission Control

A Python project for managing and controlling robot checkpoints, including API integration and a Tkinter-based GUI.

## 📦 Requirements

- Python **3.11.4**
- See [`requirements.txt`](./requirements.txt) for all required packages.

## 🏁 Getting Started

1. Make sure Python 3.11.4 is installed.
2. (Optional) Create a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # on Windows: .\env\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python main.py
   ```

## 📂 Project Structure

```text
├── gui/                  # GUI components (Tkinter)
├── models/               # Data models and templates
├── checkpoints/          # Saved checkpoint templates
├── main.py               # Main entry point
├── requirements.txt      # Dependencies
├── .gitignore            # Git exclusions
└── README.md             # This file
```

## 🔒 .gitignore

Ensure that the `env/` folder (your virtual environment) and all `.zip` files are excluded from your Git repository. See `.gitignore`.

## ✍️ Notes

- Using a different Python version? Mention it here.
- Always update `requirements.txt` when your dependencies change.
