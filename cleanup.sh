#!/bin/zsh

echo "Cleaning up your workspace..."
echo ""
kind delete cluster --name ml-scheduler

echo ""
echo "All clean!"