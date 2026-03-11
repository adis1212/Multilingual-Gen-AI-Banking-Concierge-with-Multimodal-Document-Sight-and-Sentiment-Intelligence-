#!/bin/bash
echo "🛡️  Setting up Linguist-Guardian..."

# Backend
echo "📦 Installing Python dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env template
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Please fill in your API keys in backend/.env"
fi

cd ..

# Frontend
echo "📦 Installing Node dependencies..."
cd frontend
npm install

if [ ! -f .env.local ]; then
  cp .env.example .env.local
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Demo UI: open assets/demo/linguist-guardian.html in browser (no server needed)"