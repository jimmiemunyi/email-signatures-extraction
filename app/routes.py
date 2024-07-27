from flask import render_template, flash, redirect
from app import app
from app.forms import EmailExtractForm
from helpers import ask_claude, generate_prompts


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    form = EmailExtractForm()
    if form.validate_on_submit():
        email_extract = form.email.data
        prompt, return_format = generate_prompts(email_extract)
        email_content_anthropic = ask_claude(
            system_settings=return_format,
            ask=prompt,
        )
        flash(f"{email_content_anthropic}")
    return render_template("index.html", form=form)
