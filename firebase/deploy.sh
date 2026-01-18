#!/usr/bin/env bash
set -euo pipefail
command -v firebase >/dev/null || npm i -g firebase-tools
firebase emulators:start --only auth,firestore,functions,hosting   # local
# firebase deploy --only hosting,functions,firestore               # prod
