# cmio_v0

A local-first care coordination sandbox showcasing the CMIO data model and a pastel morning dashboard for approving pending facts, promoting encounter notes to case notes, and planning time-blocked tasks.

## Running the UI

The dashboard is powered by Flask with in-memory sample data.

```bash
pip install flask
FLASK_APP=app.py flask run
```

Open http://127.0.0.1:5000/ to explore the pink-and-purple interface, approve pending facts, promote encounter notes, toggle task steps, and choose the AI model posture.
