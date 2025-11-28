#!/bin/bash
# Vercel build script for Next.js
set -e

echo "🔨 Starting Vercel build process..."
echo "🏗️  Building Next.js application..."
next build

echo "✅ Build completed successfully!"
