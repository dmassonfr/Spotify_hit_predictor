streamlit:
	-@streamlit run app/app.py

requirements:
	@pip install -r requirements.txt

fastapi:
	@uvicorn inference-api:inference --reload

build_docker:
	@docker build -t api .

run_docker:
	@docker run -p 8080:8000 api
	