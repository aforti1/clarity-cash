# Development helper functions to force kill processes running on specific ports (api and frontend)
sudo lsof -t -i:8000 | xargs kill -9
sudo lsof -t -i:5173 | xargs kill -9