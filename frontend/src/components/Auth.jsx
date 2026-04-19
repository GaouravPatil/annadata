import { useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

export default function Auth({ onLogin }) {
    const [form, setForm] = useState({ name: "", location: "", age: "", language: "en" })
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const [focused, setFocused] = useState({})

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
            onLogin(res.data.token, res.data.farmer_id)
        } catch (err) {
            setError("Could not connect. Please try again.")
        } finally {
            setLoading(false)
        }
    }

    const fields = [
        { key: "name", label: "Your name", type: "text", icon: "👤", placeholder: "e.g. Ramesh Kumar" },
        { key: "location", label: "Village / District", type: "text", icon: "📍", placeholder: "e.g. Nashik, Maharashtra" },
        { key: "age", label: "Your age", type: "number", icon: "🎂", placeholder: "e.g. 35" },
    ]

    return (
        <div style={styles.page}>
            {/* Background blobs */}
            <div style={styles.blob1} />
            <div style={styles.blob2} />

            <div style={styles.card}>
                {/* Logo / Brand */}
                <div style={styles.brand}>
                    <div style={styles.logoCircle}>
                        <span style={{ fontSize: 28 }}>🌾</span>
                    </div>
                    <h1 style={styles.title}>AnnaData</h1>
                    <p style={styles.subtitle}>AI assistant for Indian farmers</p>
                </div>

                {/* Step label */}
                <div style={styles.stepBadge}>
                    <span style={styles.stepDot} />
                    Tell us about yourself
                </div>

                <form onSubmit={handleSubmit} style={styles.form} noValidate>

                    {fields.map(({ key, label, type, icon, placeholder }) => {
                        const isFocused = focused[key]
                        const hasValue = !!form[key]
                        const active = isFocused || hasValue
                        return (
                            <div key={key} style={styles.fieldWrap}>
                                <div style={{
                                    ...styles.inputBox,
                                    borderColor: isFocused ? "var(--green-600)" : hasValue ? "var(--green-200)" : "var(--gray-200)",
                                    boxShadow: isFocused ? "0 0 0 3px rgba(22,163,74,0.12)" : "none",
                                }}>
                                    <span style={styles.fieldIcon}>{icon}</span>
                                    <div style={styles.inputInner}>
                                        <label
                                            htmlFor={`field-${key}`}
                                            style={{
                                                ...styles.floatLabel,
                                                top: active ? "6px" : "50%",
                                                transform: active ? "translateY(0) scale(0.82)" : "translateY(-50%) scale(1)",
                                                color: isFocused ? "var(--green-600)" : "var(--gray-400)",
                                                fontSize: active ? "11px" : "14px",
                                                fontWeight: active ? "600" : "400",
                                            }}
                                        >
                                            {label}
                                        </label>
                                        <input
                                            id={`field-${key}`}
                                            type={type}
                                            value={form[key]}
                                            min={type === "number" ? 1 : undefined}
                                            max={type === "number" ? 120 : undefined}
                                            onChange={e => update(key, e.target.value)}
                                            onFocus={() => setFocused(prev => ({ ...prev, [key]: true }))}
                                            onBlur={() => setFocused(prev => ({ ...prev, [key]: false }))}
                                            placeholder={active ? placeholder : ""}
                                            style={styles.input}
                                            autoComplete="off"
                                        />
                                    </div>
                                </div>
                            </div>
                        )
                    })}

                    {/* Language selector */}
                    <div style={styles.fieldWrap}>
                        <div style={{
                            ...styles.inputBox,
                            borderColor: focused.language ? "var(--green-600)" : "var(--gray-200)",
                            boxShadow: focused.language ? "0 0 0 3px rgba(22,163,74,0.12)" : "none",
                        }}>
                            <span style={styles.fieldIcon}>🗣️</span>
                            <div style={styles.inputInner}>
                                <label htmlFor="field-lang" style={{ ...styles.floatLabel, top: "6px", transform: "translateY(0) scale(0.82)", color: "var(--gray-400)", fontSize: "11px", fontWeight: 600 }}>
                                    Preferred language
                                </label>
                                <select
                                    id="field-lang"
                                    value={form.language}
                                    onChange={e => update("language", e.target.value)}
                                    onFocus={() => setFocused(prev => ({ ...prev, language: true }))}
                                    onBlur={() => setFocused(prev => ({ ...prev, language: false }))}
                                    style={{ ...styles.input, paddingTop: "18px", cursor: "pointer" }}
                                >
                                    <option value="en">English</option>
                                    <option value="hi">Hindi</option>
                                    <option value="mr">Marathi</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div style={styles.errorBox}>
                            <span>⚠️</span> {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            ...styles.btn,
                            opacity: loading ? 0.75 : 1,
                        }}
                        onMouseEnter={e => { if (!loading) e.currentTarget.style.transform = "translateY(-1px)" }}
                        onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)" }}
                    >
                        {loading
                            ? <><span style={styles.spinner} /> Starting up...</>
                            : "Start Chatting →"
                        }
                    </button>
                </form>

                <p style={styles.privacy}>
                    🔒 Your data stays private and is used only to personalise your experience.
                </p>
            </div>
        </div>
    )
}

/* ─── Styles ─────────────────────────────────────────────────────────── */
const styles = {
    page: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #f0fdf4 100%)",
        padding: "1rem",
        position: "relative",
        overflow: "hidden",
    },
    blob1: {
        position: "absolute",
        top: "-120px",
        left: "-120px",
        width: "400px",
        height: "400px",
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(74,222,128,0.18) 0%, transparent 70%)",
        pointerEvents: "none",
    },
    blob2: {
        position: "absolute",
        bottom: "-100px",
        right: "-100px",
        width: "350px",
        height: "350px",
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(22,163,74,0.14) 0%, transparent 70%)",
        pointerEvents: "none",
    },
    card: {
        position: "relative",
        background: "rgba(255,255,255,0.92)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderRadius: "24px",
        padding: "2.5rem 2rem",
        width: "100%",
        maxWidth: "420px",
        boxShadow: "0 8px 40px rgba(22,163,74,0.10), 0 1px 4px rgba(0,0,0,0.06)",
        border: "1px solid rgba(187,247,208,0.6)",
    },
    brand: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginBottom: "1.75rem",
        gap: "0.5rem",
    },
    logoCircle: {
        width: "62px",
        height: "62px",
        borderRadius: "18px",
        background: "linear-gradient(135deg, #16a34a, #15803d)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 4px 16px rgba(22,163,74,0.35)",
        marginBottom: "0.25rem",
    },
    title: {
        fontSize: "26px",
        fontWeight: "700",
        color: "#14532d",
        letterSpacing: "-0.5px",
    },
    subtitle: {
        fontSize: "14px",
        color: "var(--gray-500, #6b7280)",
        fontWeight: "400",
    },
    stepBadge: {
        display: "flex",
        alignItems: "center",
        gap: "6px",
        fontSize: "12px",
        fontWeight: "600",
        color: "#16a34a",
        textTransform: "uppercase",
        letterSpacing: "0.5px",
        marginBottom: "1.25rem",
    },
    stepDot: {
        width: "8px",
        height: "8px",
        borderRadius: "50%",
        background: "#16a34a",
        boxShadow: "0 0 0 3px rgba(22,163,74,0.2)",
        display: "inline-block",
    },
    form: {
        display: "flex",
        flexDirection: "column",
        gap: "0.75rem",
    },
    fieldWrap: {
        position: "relative",
    },
    inputBox: {
        display: "flex",
        alignItems: "center",
        border: "1.5px solid #e5e7eb",
        borderRadius: "12px",
        background: "white",
        transition: "border-color 0.2s, box-shadow 0.2s",
        overflow: "hidden",
        minHeight: "60px",
    },
    fieldIcon: {
        fontSize: "18px",
        padding: "0 12px 0 14px",
        flexShrink: 0,
        lineHeight: "1",
    },
    inputInner: {
        flex: 1,
        position: "relative",
        paddingRight: "12px",
    },
    floatLabel: {
        position: "absolute",
        left: 0,
        transformOrigin: "left center",
        transition: "top 0.18s ease, transform 0.18s ease, color 0.18s ease, font-size 0.18s ease",
        pointerEvents: "none",
        lineHeight: "1",
        whiteSpace: "nowrap",
    },
    input: {
        width: "100%",
        border: "none",
        outline: "none",
        background: "transparent",
        fontSize: "15px",
        color: "#111827",
        fontFamily: "inherit",
        fontWeight: "500",
        paddingTop: "18px",
        paddingBottom: "6px",
        appearance: "textfield",
    },
    errorBox: {
        display: "flex",
        alignItems: "center",
        gap: "6px",
        background: "#fef2f2",
        border: "1px solid #fecaca",
        borderRadius: "8px",
        padding: "10px 14px",
        fontSize: "13px",
        color: "#dc2626",
        fontWeight: "500",
    },
    btn: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "8px",
        marginTop: "0.5rem",
        width: "100%",
        padding: "15px",
        background: "linear-gradient(135deg, #16a34a, #15803d)",
        color: "white",
        border: "none",
        borderRadius: "12px",
        fontSize: "15px",
        cursor: "pointer",
        fontWeight: "600",
        fontFamily: "inherit",
        letterSpacing: "0.2px",
        boxShadow: "0 4px 16px rgba(22,163,74,0.35)",
        transition: "transform 0.15s ease, box-shadow 0.15s ease",
    },
    spinner: {
        width: "16px",
        height: "16px",
        border: "2px solid rgba(255,255,255,0.35)",
        borderTopColor: "white",
        borderRadius: "50%",
        display: "inline-block",
        animation: "spin 0.7s linear infinite",
    },
    privacy: {
        marginTop: "1.25rem",
        textAlign: "center",
        fontSize: "12px",
        color: "#9ca3af",
        lineHeight: "1.5",
    },
}

// Inject keyframe for spinner
const styleTag = document.createElement("style")
styleTag.innerHTML = `@keyframes spin { to { transform: rotate(360deg); } }`
document.head.appendChild(styleTag)