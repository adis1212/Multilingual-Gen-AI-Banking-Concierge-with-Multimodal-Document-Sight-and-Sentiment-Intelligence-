import { useState, useRef, useEffect } from 'react';
import { Mic, Send, X, Volume2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const BankingAssistantPage = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const [customerName, setCustomerName] = useState('');
  const recognitionRef = useRef(null);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onstart = () => setIsListening(true);
      recognitionRef.current.onend = () => setIsListening(false);

      recognitionRef.current.onresult = (event) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptSegment = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            interim += transcriptSegment + ' ';
          }
        }
        setTranscript(interim || transcript);
      };
    }
  }, []);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = getLanguageCode(language);
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const getLanguageCode = (lang) => {
    const codes = {
      en: 'en-US',
      hi: 'hi-IN',
      mr: 'mr-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      bn: 'bn-IN',
      gu: 'gu-IN',
      kn: 'kn-IN',
      ml: 'ml-IN'
    };
    return codes[lang] || 'en-US';
  };

  const handleSubmit = async () => {
    if (!transcript.trim()) {
      toast.error('Please say something or type your question');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/banking-assistant/help', {
        query: transcript,
        language,
        customer_name: customerName,
        session_id: `session-${Date.now()}`
      });

      setResponse(res.data);
      toast.success('Got your answer!');
      speakResponse(res.data.message);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to get assistance');
    } finally {
      setLoading(false);
    }
  };

  const speakResponse = (message) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.lang = getLanguageCode(language);
      utterance.rate = 0.9; // Slower for clarity
      speechSynthesis.speak(utterance);
    }
  };

  const handleClear = () => {
    setTranscript('');
    setResponse(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">
            🏦 Union Bank Banking Assistant
          </h1>
          <p className="text-gray-600">
            Ask me anything about our services. I'll guide you to the right counter.
          </p>
        </div>

        {/* Settings */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Your Name (Optional)
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="Your name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="mr">Marathi</option>
                <option value="ta">Tamil</option>
                <option value="te">Telugu</option>
                <option value="bn">Bengali</option>
                <option value="gu">Gujarati</option>
                <option value="kn">Kannada</option>
                <option value="ml">Malayalam</option>
              </select>
            </div>
          </div>
        </div>

        {/* Voice Input */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Your Question
            </label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Type here or use the microphone..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows="3"
            />
          </div>

          {/* Buttons */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={isListening ? stopListening : startListening}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition ${
                isListening
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              <Mic size={20} />
              {isListening ? 'Stop Listening' : 'Start Listening'}
            </button>

            <button
              onClick={handleSubmit}
              disabled={loading || !transcript.trim()}
              className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Send size={20} />
              {loading ? 'Processing...' : 'Get Help'}
            </button>

            <button
              onClick={handleClear}
              className="flex items-center gap-2 px-6 py-3 bg-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-400 transition"
            >
              <X size={20} />
              Clear
            </button>
          </div>
        </div>

        {/* Response */}
        {response && (
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-green-700 mb-2">
                ✓ Help for: {response.intent.replace(/_/g, ' ').toUpperCase()}
              </h2>

              <div className="bg-blue-50 p-4 rounded-lg mb-4 border border-blue-200">
                <p className="text-lg text-blue-900 font-semibold">
                  📍 {response.counter}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <p className="text-gray-700 text-lg leading-relaxed">
                  {response.message}
                </p>
              </div>

              <button
                onClick={() => speakResponse(response.message)}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
              >
                <Volume2 size={18} />
                Hear Response
              </button>
            </div>

            <div className="text-sm text-gray-500 mt-4">
              Language: {language.toUpperCase()} | Intent Confidence: High
            </div>
          </div>
        )}

        {/* Counter Info */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">📋 Branch Counters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <strong>Counter 1:</strong> Account Services
            </div>
            <div className="p-3 bg-green-50 rounded border border-green-200">
              <strong>Counter 2:</strong> Cash Deposit/Withdrawal
            </div>
            <div className="p-3 bg-purple-50 rounded border border-purple-200">
              <strong>Counter 3:</strong> Loan Desk
            </div>
            <div className="p-3 bg-orange-50 rounded border border-orange-200">
              <strong>Counter 4:</strong> Passbook Update
            </div>
            <div className="p-3 bg-red-50 rounded border border-red-200">
              <strong>Counter 5:</strong> Customer Support
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BankingAssistantPage;
