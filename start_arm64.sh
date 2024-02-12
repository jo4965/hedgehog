nohup ./pocketbase_arm64/pocketbase serve --http 0.0.0.0:8090 &
nohup uvicorn main:app --host 0.0.0.0 --port 80 &
