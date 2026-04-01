import { useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

export default function Auth({ onLogin }) {
    const [form, setForm] = useState({ name: "", phone: "", language: "en", location: "" })
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e) {
        e.preventDefault()
        setLoading(true)
        setError("")
        try {
            const res = await axios.post(`${API}/register`, form)
            onLogin(res.data.token, res.data.farmer_id)
        } catch (err) {
            setError("Registration failed. Please try again.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            minHeight: "100vh", display: "flex", alignItems: "center",
            justifyContent: "center", background: "#f0fdf4"
        }}>
            <div style={{
                background: "white", padding: "2rem", borderRadius: "12px",
                width: "100%", maxWidth: "400px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
            }}>
                <h1 style={{ color: "#166534", marginBottom: "0.25rem" }}>🌾 AnnaData</h1>
                <p style={{ color: "#6b7280", marginBottom: "1.5rem" }}>AI assistant for Indian farmers</p>

                <form onSubmit={handleSubmit}>
                    <input
                        placeholder="Your name"
                        value={form.name}
                        onChange={e => setForm({ ...form, name: e.target.value })}
                        required
                        style={inputStyle}
                    />
                    <input
                        placeholder="Phone number"
                        value={form.phone}
                        onChange={e => setForm({ ...form, phone: e.target.value })}
                        required
                        style={inputStyle}
                    />
                    <input
                        placeholder="Location (e.g. Pune)"
                        value={form.location}
                        onChange={e => setForm({ ...form, location: e.target.value })}
                        style={inputStyle}
                    />
                    <select
                        value={form.language}
                        onChange={e => setForm({ ...form, language: e.target.value })}
                        style={inputStyle}
                    >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="mr">Marathi</option>
                    </select>

                    {error && <p style={{ color: "red", fontSize: "14px" }}>{error}</p>}

                    <button type="submit" disabled={loading} style={btnStyle}>
                        {loading ? "Logging in..." : "Start Chatting"}
                    </button>
                </form>
            </div>
        </div>
    )
}

const inputStyle = {
    width: "100%", padding: "10px 12px", marginBottom: "12px",
    border: "1px solid #d1d5db", borderRadius: "8px",
    fontSize: "14px", boxSizing: "border-box"
}

const btnStyle = {
    width: "100%", padding: "12px", background: "#16a34a",
    color: "white", border: "none", borderRadius: "8px",
    fontSize: "15px", cursor: "pointer", fontWeight: "500"
}