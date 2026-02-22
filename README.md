pip install -r requirements.txt
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install psycopg[binary]
Start-Process python -ArgumentList "-m clientes.app"
Start-Process python -ArgumentList "-m inmuebles.app"
Start-Process python -ArgumentList "-m citas.app"

pip install psycopg[binary] flask python-dotenv
pip install flask
pip install python-dotenv
pip install python-dotenv
pip install reportlab


python -m clientes.app
python -m inmuebles.app
python -m citas.app

python app.py

