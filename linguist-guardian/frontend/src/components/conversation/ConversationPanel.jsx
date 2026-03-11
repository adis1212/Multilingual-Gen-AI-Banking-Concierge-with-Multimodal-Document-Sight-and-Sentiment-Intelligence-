import { useRef, useEffect } from 'react'
import { useSessionStore }  from '@/store/sessionStore'
import { useWebSocket }     from '@/hooks/useWebSocket'
import { useAudioCapture }  from '@/hooks/useAudioCapture'
import MessageBubble        from './MessageBubble'
import InputBar             from './InputBar'

// Demo messages to show on load
const DEMO_MESSAGES = [
  {
    id: '1', speaker: 'customer', channel: 'A', language: 'mr',
    text: 'मला माझे कार्ड हरवले आहे. मला खूप काळजी वाटत आहे!',
    translation: 'I lost my card. I am very worried!',
    intent: { intent: 'lost_card', urgency: 'critical', emotion: 'distressed',
              staff_advisory: 'CRITICAL: Customer reported a lost card. Initiate card block immediately.' },
    timestamp: new Date().toISOString(),
  },
  {
    id: '2', speaker: 'ai', channel: null, language: 'en',
    text: '🔴 CRITICAL: Customer reported a lost card. Stress level elevated (78%).\n\n1. Acknowledge distress warmly in Marathi\n2. Initiate card block (Card #4829)\n3. Offer expedited re-issue (3 business days)\n4. Verify KYC before proceeding',
    timestamp: new Date().toISOString(),
  },
  {
    id: '3', speaker: 'staff', channel: 'B', language: 'en',
    text: "Don't worry, Priya ji. We'll block your card right now and help you get a new one today.",
    translation: 'काळजी करू नका, प्रिया जी. आम्ही आत्ताच तुमचे कार्ड ब्लॉक करतो.',
    timestamp: new Date().toISOString(),
  },
]

export default function ConversationPanel() {
  const bottomRef  = useRef(null)
  const { sessionId, messages, addMessage } = useSessionStore()

  const { sendAudioChunk } = useWebSocket(sessionId)
  const { isRecording, startRecording, stopRecording } = useAudioCapture({
    onChunk: sendAudioChunk,
    language: 'mr',
  })

  // Seed demo messages
  useEffect(() => {
    if (messages.length === 0) {
      DEMO_MESSAGES.forEach(m => addMessage(m))
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const allMessages = messages.length > 0 ? messages : DEMO_MESSAGES

  return (
    <>
      <div className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4">
        {allMessages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <InputBar
        isRecording={isRecording}
        onStartRecord={() => startRecording('A')}
        onStopRecord={stopRecording}
      />
    </>
  )
}