
# Export FX — CBM vs Full Black (Streamlit Web App)

A super-simple web app to compare Myanmar CBM split vs full black market rate for export proceeds.

## Features
- Inputs: USD amount, official %, r1 (official rate), r2 (black rate), optional fees
- Outputs: Effective blended rate, MMK with split vs full black, shortfall, % realized
- Charts: Altair bar charts comparing totals and per-$1 view
- Sensitivity: quick grid of shortfall across p1% and r2 ±400
- Scenarios: add multiple scenarios and export to CSV
- Required-rate summary to show the black rate needed on the exporter's share, accounting for % fees

## Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud (Shareable link)
1. Push these three files (`app.py`, `requirements.txt`, `README.md`) to a public GitHub repo.
2. Go to https://share.streamlit.io
3. Log in with GitHub and deploy the repo.
4. Share the link with your dad/team.

## Notes
- No external APIs used; rates are entered by you.
- Flat fees apply equally to split and full-black paths; percentage fees apply only to the black-market portion in the
  split scenario.
- You can customize branding and add authentication later if needed.
- Charts fall back to Streamlit's built-ins if `altair` isn't installed.
