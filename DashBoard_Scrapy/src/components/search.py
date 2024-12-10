from dash import html


def render_input_field(name, label):
    """
    Render an HTML input field with a label.
    """
    return f"""
    <div class="form-group">
        <label for="{name}">{label}</label>
        <input type="text" id="{name}" name="{name}" class="form-control" placeholder="Entrez {label}...">
    </div>
    """
