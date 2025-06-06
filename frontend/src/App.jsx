import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:8000/get_answer?query=' + encodeURIComponent(question))
      const data = await response.json()
      setAnswer(data.answer)
    } catch (error) {
      console.error('Error:', error)
      setAnswer('Error occurred while fetching the answer')
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>Question Answer Agent</h1>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your question..."
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Getting Answer...' : 'Ask'}
          </button>
        </div>
      </form>
      {answer && (
        <div className="answer-box">
          <h2>Answer:</h2>
          <p>{answer}</p>
        </div>
      )}
    </div>
  )
}

export default App
