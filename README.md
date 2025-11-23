# cmio_v0

A local-first care coordination sandbox showcasing the CMIO data model and a pastel morning dashboard for approving pending facts, promoting encounter notes to case notes, and planning time-blocked tasks.

## Running the UI

The dashboard is powered by Flask with in-memory sample data.

### Quick launch

```bash
python run_cmio.py
```

This starts the app on http://127.0.0.1:8000/ and opens it in your default browser.

### Manual launch

```bash
python -m pip install -r requirements.txt
pip install flask
FLASK_APP=app.py flask run --host=0.0.0.0 --port=8000
```

Then open http://127.0.0.1:8000/ to explore the pink-and-purple interface, approve pending facts, promote encounter notes, toggle task steps, and choose the AI model posture.

If the launcher closes immediately, install dependencies with `python -m pip install -r requirements.txt` and run it from a terminal so any error messages stay visible.
```bash
pip install flask
FLASK_APP=app.py flask run
```

Open http://127.0.0.1:5000/ to explore the pink-and-purple interface, approve pending facts, promote encounter notes, toggle task steps, and choose the AI model posture.
