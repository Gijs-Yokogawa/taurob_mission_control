# Taurob Mission Control

Een Python-project voor het aansturen en beheren van robot-checkpoints, inclusief API-koppeling en GUI via Tkinter.

## 📦 Vereisten

- Python **3.11.4**
- Zie [`requirements.txt`](./requirements.txt) voor alle benodigde packages.

## 🏁 Starten

1. Zorg dat Python 3.11.4 geïnstalleerd is.
2. (Optioneel) Maak een virtuele omgeving aan:

   ```bash
   python -m venv env
   source env/bin/activate  # op Windows: .\env\Scripts\activate
   ```

3. Installeer de afhankelijkheden:

   ```bash
   pip install -r requirements.txt
   ```

4. Start de applicatie:

   ```bash
   python main.py
   ```

## 📂 Structuur

```text
├── gui/                  # Bevat GUI componenten (Tkinter)
├── models/               # Datamodellen en templates
├── checkpoints/          # Opgeslagen checkpoint templates
├── main.py               # Hoofdbestand om te starten
├── requirements.txt      # Afhankelijkheden
├── .gitignore            # Git-exclusies
└── README.md             # Dit bestand
```

## 🔒 .gitignore

Zorg ervoor dat de map `env/` (je virtuele omgeving) en alle `.zip` bestanden zijn uitgesloten van je Git-repository. Zie `.gitignore`.

## ✍️ Notities

- Gebruik je een andere Python-versie? Vermeld dit hier.
- Controleer altijd of de juiste `requirements.txt` is bijgewerkt na package-wijzigingen.
