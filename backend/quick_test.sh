#!/bin/bash
# Quick API test

echo "Testing registration..."
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"testpass123","tier":"free"}'

echo -e "\n\nTesting login..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"testpass123"}')

echo "$RESPONSE" | head -50

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "\n\nTesting /me endpoint..."
    curl -s -X GET http://127.0.0.1:8000/api/v1/auth/me \
      -H "Authorization: Bearer $TOKEN"

    echo -e "\n\nTesting analyze endpoint..."
    curl -s -X POST http://127.0.0.1:8000/api/v1/analyze \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"text":"She dont like apples.","mode":"accuracy"}' | head -100

    echo -e "\n\nTesting history endpoint..."
    curl -s -X GET http://127.0.0.1:8000/api/v1/history \
      -H "Authorization: Bearer $TOKEN"
else
    echo "Failed to get token"
fi
