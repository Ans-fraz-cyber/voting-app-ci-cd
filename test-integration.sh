#!/bin/bash

echo "Running integration tests..."

# Test vote service
echo "Testing vote service..."
VOTE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
if [ "$VOTE_RESPONSE" != "200" ]; then
    echo "Vote service test failed: HTTP $VOTE_RESPONSE"
    exit 1
fi

# Test result service
echo "Testing result service..."
RESULT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001)
if [ "$RESULT_RESPONSE" != "200" ]; then
    echo "Result service test failed: HTTP $RESULT_RESPONSE"
    exit 1
fi

# Test voting functionality
echo "Testing voting functionality..."
VOTE_POST=$(curl -s -o /dev/null -w "%{http_code}" -X POST -d "vote=a" http://localhost:5000)
if [ "$VOTE_POST" != "200" ]; then
    echo "Vote POST test failed: HTTP $VOTE_POST"
    exit 1
fi

echo "All integration tests passed!"
