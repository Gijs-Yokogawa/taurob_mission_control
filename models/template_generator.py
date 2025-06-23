# models/template_generator.py
# Genereert een lege checkpoint-template als JSON-dict

def generate_empty_checkpoint_template(name: str, checkpoint_type: str) -> dict:
    """
    Maak een lege template voor een checkpoint met een standaard ActionID = None.
    """
    if not name.strip():
        raise ValueError("Naam van checkpoint mag niet leeg zijn.")

    ctype = checkpoint_type.strip().lower()
    valid = ['drive', 'dock', 'measure']
    if ctype not in valid:
        raise ValueError(
            f"'{checkpoint_type}' is geen geldig checkpoint type. Kies uit: {', '.join(valid)}"
        )

    # Basisvelden
    template = {
        'ActionID': None,             # standaard None; wordt door API overschreven
        'ActionName': name,
        'ActionType': ctype,
        'RobotPose': "",
        'ActionInfo': "",
        'Metadata': ""
    }

    # Voor 'dock' en 'measure' ook AssetName
    if ctype in ['dock', 'measure']:
        template['AssetName'] = ""

    return template
