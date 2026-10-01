import { useState } from "react"
import axios from "axios"
import { useTheme } from "../theme.jsx"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function Auth({ onLogin }) {
    const { theme, toggle } = useTheme()
    const [form, setForm] = useState({ name: "", location: "", age: "", language: "en" })
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    function update(field, value) {
        setForm(prev => ({ ...prev, [field]: value }))
    }

    async function handleSubmit(e) {
        e.preventDefault()
        if (!form.name.trim() || !form.location.trim() || !form.age) {
            setError("Please fill in all fields.")
            return
        }
        const age = parseInt(form.age)
        if (isNaN(age) || age < 1 || age > 120) {
            setError("Please enter a valid age.")
            return
        }
        setLoading(true)
        setError("")
        try {
            const res = await axios.post(`${API}/register`, {
                name: form.name.trim(),
                location: form.location.trim(),
                age,
                language: form.language,
            })
            onLogin(res.data)
        } catch (err) {
            setError("Could not connect. Please try again.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={styles.page}>
            <button onClick={toggle} className="skeuo-btn-ghost" style={styles.themeToggle} title="Toggle dark / light">
                {theme === "light" ? "🌙 Dark" : "☀️ Light"}
            </button>

            <div className="skeuo-card anim-enter" style={styles.card}>
                {/* Brass screws */}
                <span style={{ ...styles.screw, top: 10, left: 12 }}>✦</span>
                <span style={{ ...styles.screw, top: 10, right: 12 }}>✦</span>

                <div style={styles.brand}>
                    <div style={styles.logoDial}>
                        <span style={{ fontSize: 30 }}>🌾</span>
                    </div>
                    <h1 className="embossed" style={styles.title}>AnnaData</h1>
                    <p style={styles.subtitle}>AI assistant for Indian farmers</p>
                    <div style={styles.meterWrap} title="Signal">
                        <div style={styles.meterTrack}>
                            <div style={styles.meterFill} />
                        </div>
                        <span style={styles.meterLabel}>LIVE • SARKARI DATA • MAUSAM</span>
                    </div>
                </div>

                <div className="skeuo-inset" style={styles.stepPlate}>
                    <span className="live-dot" />
                    <span style={styles.stepText}>Tell us about yourself — weather & mandi auto-detect your village</span>
                </div>

                <form onSubmit={handleSubmit} style={styles.form} noValidate>
                    <label style={styles.label} htmlFor="field-name">👤 Your name</label>
                    <input
                        id="field-name"
                        className="skeuo-input"
                        style={styles.input}
                        value={form.name}
                        onChange={e => update("name", e.target.value)}
                        placeholder="e.g. Ramesh Kumar"
                        autoComplete="off"
                    />

                    <label style={styles.label} htmlFor="field-location">📍 Village / District, State</label>
                    <input
                        id="field-location"
                        className="skeuo-input"
                        style={styles.input}
                        value={form.location}
                        onChange={e => update("location", e.target.value)}
                        placeholder="e.g. Nashik, Maharashtra"
                        autoComplete="off"
                    />
                    <p style={styles.hint}>Used for live weather (top-right) & mandi prices of your area.</p>

                    <div style={styles.row}>
                        <div style={{ flex: 1 }}>
                            <label style={styles.label} htmlFor="field-age">🎂 Age</label>
                            <input
                                id="field-age"
                                className="skeuo-input"
                                style={styles.input}
                                type="number" min={1} max={120}
                                value={form.age}
                                onChange={e => update("age", e.target.value)}
                                placeholder="e.g. 35"
                            />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={styles.label} htmlFor="field-lang">🗣️ Language</label>
                            <select
                                id="field-lang"
                                className="skeuo-input"
                                style={{ ...styles.input, cursor: "pointer" }}
                                value={form.language}
                                onChange={e => update("language", e.target.value)}
                            >
                                <option value="en">English</option>
                                <option value="hi">Hindi</option>
                                <option value="mr">Marathi</option>
                            </select>
                        </div>
                    </div>

                    {error && <div style={styles.errorBox}>⚠️ {error}</div>}

                    <button type="submit" disabled={loading} className="skeuo-btn" style={styles.btn}>
                        {loading ? <><span style={styles.spinner} /> Starting up...</> : "Start Chatting →"}
                    </button>
                </form>

                <p style={styles.privacy}>🔒 Your data stays private and is used only to personalise your experience.</p>
            </div>
        </div>
    )
}

const styles = {
    page: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem 1rem",
        position: "relative",
    },
    themeToggle: { position: "absolute", top: 16, right: 16, padding: "8px 14px", fontSize: 13 },
    card: { width: "100%", maxWidth: 440, padding: "2.2rem 1.8rem 1.6rem" },
    screw: { position: "absolute", fontSize: 12, opacity: 0.45 },
    brand: { display: "flex", flexDirection: "column", alignItems: "center", gap: 6, marginBottom: "1.1rem" },
    logoDial: {
        width: 72, height: 72, borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "radial-gradient(circle at 35% 30%, #fff8dd 0%, #ecd98a 35%, #b98a1e 70%, #6e4d08 100%)",
        border: "3px solid var(--card-border)",
        boxShadow: "inset 0 2px 4px rgba(255,255,255,0.8), inset 0 -6px 12px rgba(90,60,5,0.55), 0 6px 16px rgba(80,60,10,0.4)",
    },
    title: { fontSize: 28, fontWeight: 700, letterSpacing: "-0.5px" },
    subtitle: { fontSize: 13, color: "var(--text-2)" },
    meterWrap: { marginTop: 8, width: "100%", display: "flex", flexDirection: "column", gap: 4, alignItems: "center" },
    meterTrack: {
        width: "70%", height: 10, borderRadius: 8, border: "1px solid var(--card-border)",
        background: "linear-gradient(180deg, #3a3a3a, #141414)", overflow: "hidden",
        boxShadow: "inset 0 2px 4px rgba(0,0,0,0.7)",
    },
    meterFill: {
        width: "82%", height: "100%",
        background: "linear-gradient(180deg, #b6f0b8, #43a047 60%, #1b5e20)",
        boxShadow: "inset 0 1px 0 rgba(255,255,255,0.7)",
    },
    meterLabel: { fontSize: 10, letterSpacing: 1.5, color: "var(--text-3)", fontWeight: 600 },
    stepPlate: {
        display: "flex", alignItems: "center", gap: 8,
        padding: "10px 12px", marginBottom: "1rem",
    },
    stepText: { fontSize: 12, fontWeight: 600, color: "var(--text-2)" },
    form: { display: "flex", flexDirection: "column", gap: 8 },
    label: { fontSize: 12, fontWeight: 700, color: "var(--text-2)", letterSpacing: 0.3, marginTop: 4 },
    input: { padding: "11px 13px", fontSize: 14, fontFamily: "inherit", fontWeight: 500 },
    hint: { fontSize: 11, color: "var(--text-3)", marginTop: -2 },
    row: { display: "flex", gap: 10 },
    errorBox: {
        background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8,
        padding: "10px 14px", fontSize: 13, color: "#dc2626", fontWeight: 500,
    },
    btn: {
        marginTop: 10, width: "100%", padding: 14, fontSize: 15,
        display: "flex", alignItems: "center", justifyContent: "center", gap: 8, fontFamily: "inherit",
    },
    spinner: {
        width: 16, height: 16, border: "2px solid rgba(255,255,255,0.35)",
        borderTopColor: "white", borderRadius: "50%", display: "inline-block",
        animation: "spin 0.7s linear infinite",
    },
    privacy: { marginTop: "1.1rem", textAlign: "center", fontSize: 12, color: "var(--text-3)" },
}
