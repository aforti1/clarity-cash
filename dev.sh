#!/bin/bash

##########################################################################################
# USAGE: ./dev.sh {start|stop|restart}
# This script starts, stops, or restarts the backend and frontend development servers.
##########################################################################################

case "$1" in
  start)
    echo "Starting backend..."
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    echo $! > backend.pid

    echo "Starting frontend..."
    npm run dev --prefix ./frontend > frontend.log 2>&1 &
    echo $! > frontend.pid

    echo "Servers started!"
    ;;
  
  stop)
    if [ -f backend.pid ]; then
        kill $(cat backend.pid) 2>/dev/null
        rm backend.pid
        echo "Backend stopped."
    fi

    if [ -f frontend.pid ]; then
        kill $(cat frontend.pid) 2>/dev/null
        rm frontend.pid
        echo "Frontend stopped."
    fi
    echo "Done."
    ;;
  
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  
  *)
    echo "Usage: $0 {start|stop|restart}"
    ;;
esac
