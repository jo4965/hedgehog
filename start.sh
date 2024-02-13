# shellcheck disable=SC1113
#/bin/bash

set -e
arch=$(uname -m)

case $arch in
  x86_64)
    echo "start x86_64 pocketbase"
    nohup ./pocketbase_amd64/pocketbase serve --http 0.0.0.0:8090 &
    ;;
  arm64)
    echo "start arm64 pocketbase"
    nohup ./pocketbase_arm64/pocketbase serve --http 0.0.0.0:8090 &
    ;;
  *)
    echo "error"
    exit
esac

echo "start uvicorn"
nohup uvicorn main:app --host 0.0.0.0 --port 80 &
