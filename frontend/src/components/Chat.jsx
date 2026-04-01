import { useState, useEffect, useRef } from "react"
import axios from "axios"
import ReactMarkdown from "react-markdown"

const API = "http://127.0.0.1:8000"

export default function Chat({ token, onLogout }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [location, setLocation] = useState({ lat: null, lon: null })
    const [sessions, setSessions] = useState([])
    const bottomRef = useRef(null)

    useEffect(() => {
        navigator.geolocation.getCurrentPosition(pos => {
            setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude })
        })
    }, [])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    async function sendMessage() {
        if (!input.trim() || loading) return
        const userMsg = { role: "user", content: input }
        setMessages(prev => [...prev, userMsg])
        setInput("")
        setLoading(true)

        try {
            const res = await axios.post(`${API}/chat`, {
                message: input,
                session_id: sessionId,
                latitude: location.lat,
                longitude: location.lon
            }, {
                headers: { Authorization: `Bearer ${token}` }
            })

            setSessionId(res.data.session_id)
            setMessages(prev => [...prev, { role: "assistant", content: res.data.reply }])
            if (!sessions.includes(res.data.session_id)) {
                setSessions(prev => [...prev, res.data.session_id])
            }
        } catch (err) {
            setMessages(prev => [...prev, {
                role: "assistant", content: "Sorry, something went wrong. Please try again."
            }])
        } finally {
            setLoading(false)
        }
    }

    function newChat() {
        setSessionId(null)
        setMessages([])
    }

    return (
        <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>

            {/* Sidebar */}
            <div style={{
                width: "220px", background: "#166534", color: "white",
                display: "flex", flexDirection: "column", padding: "1rem"
            }}>
                <h2 style={{ margin: "0 0 1rem", fontSize: "18px" }}>🌾 AnnaData</h2>
                <button onClick={newChat} style={{
                    background: "white", color: "#166534", border: "none",
                    borderRadius: "8px", padding: "8px", cursor: "pointer",
                    fontWeight: "500", marginBottom: "1rem"
                }}>+ New Chat</button>

                <div style={{ flex: 1, overflowY: "auto" }}>
                    {sessions.map((s, i) => (
                        <div key={s} style={{
                            padding: "8px", borderRadius: "6px", cursor: "pointer",
                            background: s === sessionId ? "rgba(255,255,255,0.2)" : "transparent",
                            fontSize: "13px", marginBottom: "4px"
                        }} onClick={() => setSessionId(s)}>
                            Chat {i + 1}
                        </div>
                    ))}
                </div>

                {location.lat && (
                    <div style={{ fontSize: "11px", opacity: 0.8, marginBottom: "8px" }}>
                        📍 {location.lat.toFixed(2)}, {location.lon.toFixed(2)}
                    </div>
                )}
                <button onClick={onLogout} style={{
                    background: "transparent", color: "white",
                    border: "1px solid rgba(255,255,255,0.4)",
                    borderRadius: "6px", padding: "6px", cursor: "pointer", fontSize: "13px"
                }}>Logout</button>
            </div>

            {/* Chat area */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "#f9fafb" }}>

                {/* Messages */}
                <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem" }}>
                    {messages.length === 0 && (
                        <div style={{ textAlign: "center", color: "#9ca3af", marginTop: "4rem" }}>
                            <p style={{ fontSize: "32px" }}>🌾</p>
                            <p>Ask me anything about farming!</p>
                            <p style={{ fontSize: "13px" }}>Weather, crops, market prices, pest control...</p>
                        </div>
                    )}
                    {messages.map((m, i) => (
                        <div key={i} style={{
                            display: "flex",
                            justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                            marginBottom: "12px"
                        }}>
                            <div style={{
                                maxWidth: "70%", padding: "10px 14px",
                                borderRadius: m.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                                background: m.role === "user" ? "#16a34a" : "white",
                                color: m.role === "user" ? "white" : "#111827",
                                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                                fontSize: "14px", lineHeight: "1.6"
                            }}>
                                {m.role === "assistant"
                                    ? <ReactMarkdown>{m.content}</ReactMarkdown>
                                    : m.content
                                }
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "12px" }}>
                            <div style={{
                                padding: "10px 14px", borderRadius: "18px 18px 18px 4px",
                                background: "white", boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                                color: "#6b7280", fontSize: "14px"
                            }}>
                                Thinking...
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div style={{
                    padding: "1rem", background: "white",
                    borderTop: "1px solid #e5e7eb", display: "flex", gap: "8px"
                }}>
                    <input
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === "Enter" && sendMessage()}
                        placeholder="Ask about crops, weather, market prices..."
                        style={{
                            flex: 1, padding: "10px 14px", border: "1px solid #d1d5db",
                            borderRadius: "24px", fontSize: "14px", outline: "none"
                        }}
                    />
                    <button onClick={sendMessage} disabled={loading} style={{
                        background: "#16a34a", color: "white", border: "none",
                        borderRadius: "24px", padding: "10px 20px",
                        cursor: "pointer", fontWeight: "500", fontSize: "14px"
                    }}>
                        Send
                    </button>
                </div>
            </div>
        </div>
    )
}