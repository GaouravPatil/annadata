import { useState, useEffect, useRef } from "react"
import axios from "axios"
import ReactMarkdown from "react-markdown"
import { useTheme } from "../theme.jsx"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"
const COMMODITIES = ["All", "Wheat", "Rice", "Paddy", "Onion", "Tomato", "Potato", "Cotton", "Soyabean", "Maize", "Sugarcane", "Mustard", "Groundnut", "Bajra", "Jowar"]

function weatherIcon(condition = "", code = null, rain = 0) {
    const c = (condition || "").toLowerCase()
    if (c.includes("thunder")) return "⛈️"
    if ((rain ?? 0) > 2 || c.includes("rain") || c.includes("shower") || c.includes("drizzle")) return "🌧️"
    if (c.includes("fog")) return "🌫️"
    if (c.includes("snow")) return "❄️"
    if (c.includes("overcast")) return "☁️"
    if (c.includes("partly") || c.includes("cloud")) return "⛅"
    if (c.includes("clear") || code === 0 || code === 1) return "☀️"
    return "🌤️"
}

export default function Chat({ token, farmer, onLogout }) {
    const { theme, toggle } = useTheme()
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [geo, setGeo] = useState({ lat: null, lon: null })
    const [sessions, setSessions] = useState([])
    const [tab, setTab] = useState("chat") // chat | mandi
    const [farmerLocation, setFarmerLocation] = useState(
        () => farmer?.location || localStorage.getItem("farmer_location") || localStorage.getItem("location") || ""
    )
    const [farmerName, setFarmerName] = useState(() => farmer?.name || "")

    // weather state (top-right, from login location)
    const [weather, setWeather] = useState(null)
    const [weatherLoading, setWeatherLoading] = useState(true)
    const [weatherError, setWeatherError] = useState("")
    const [showForecast, setShowForecast] = useState(false)

    // mandi state (location-scoped)
    const [mandi, setMandi] = useState({ records: [], state: "", district: null, fallback_to_state: false })
    const [mandiLoading, setMandiLoading] = useState(false)
    const [mandiError, setMandiError] = useState("")
    const [commodity, setCommodity] = useState("All")
    const [marketQuery, setMarketQuery] = useState("")

    const bottomRef = useRef(null)
    const headers = { Authorization: `Bearer ${token}` }

    // ── profile: prefer login prop, else /me, else localStorage ──
    useEffect(() => {
        async function ensureProfile() {
            if (farmerLocation) return
            try {
                const res = await axios.get(`${API}/me`, { headers })
                if (res.data?.location) {
                    setFarmerLocation(res.data.location)
                    localStorage.setItem("farmer_location", res.data.location)
                }
                if (res.data?.name) setFarmerName(res.data.name)
            } catch { /* offline / logged out */ }
        }
        ensureProfile()
        navigator.geolocation?.getCurrentPosition(
            pos => setGeo({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
            () => {},
            { timeout: 8000 }
        )
        loadSessions()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // ── weather: realtime from login-page location ──
    useEffect(() => {
        async function loadWeather() {
            setWeatherLoading(true)
            setWeatherError("")
            try {
                let res
                if (farmerLocation) {
                    res = await axios.get(`${API}/weather`, { params: { location: farmerLocation } })
                } else if (geo.lat && geo.lon) {
                    res = await axios.get(`${API}/weather`, { params: { lat: geo.lat, lon: geo.lon } })
                } else {
                    setWeatherLoading(false)
                    return
                }
                setWeather(res.data)
            } catch (e) {
                setWeatherError(e.response?.data?.detail || "Weather unavailable")
            } finally {
                setWeatherLoading(false)
            }
        }
        if (farmerLocation || (geo.lat && geo.lon)) loadWeather()
        else setWeatherLoading(false)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [farmerLocation])

    // ── mandi: live gov prices scoped to farmer location ──
    async function loadMandi(comm = commodity) {
        setMandiLoading(true)
        setMandiError("")
        try {
            let res
            try {
                // preferred: server infers state/district from stored farmer location
                res = await axios.get(`${API}/mandi-prices/me`, {
                    headers,
                    params: { commodity: comm === "All" ? undefined : comm, limit: 30 },
                })
            } catch {
                // fallback: explicit location string (works even if /me fails)
                res = await axios.get(`${API}/mandi-prices`, {
                    params: { location: farmerLocation || undefined, commodity: comm === "All" ? undefined : comm, limit: 30 },
                })
            }
            setMandi(res.data)
        } catch (e) {
            setMandiError(e.response?.data?.detail || "Mandi prices unavailable. Check connection and try again.")
        } finally {
            setMandiLoading(false)
        }
    }

    useEffect(() => {
        if (tab === "mandi" && mandi.records.length === 0 && !mandiLoading) loadMandi()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tab])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, loading])

    async function loadSessions() {
        try {
            const res = await axios.get(`${API}/sessions`, { headers })
            setSessions(res.data)
        } catch (err) {
            console.log("Could not load sessions", err)
        }
    }

    async function loadHistory(sid) {
        try {
            const res = await axios.get(`${API}/history/${sid}`, { headers })
            setMessages(res.data)
            setSessionId(sid)
            setTab("chat")
        } catch (err) {
            console.log("Could not load history", err)
        }
    }

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
                latitude: geo.lat,
                longitude: geo.lon
            }, { headers })
            setSessionId(res.data.session_id)
            setMessages(prev => [...prev, { role: "assistant", content: res.data.reply }])
            loadSessions()
        } catch (err) {
            setMessages(prev => [...prev, { role: "assistant", content: "Sorry, something went wrong. Please try again." }])
        } finally {
            setLoading(false)
        }
    }

    function newChat() {
        setSessionId(null)
        setMessages([])
        setTab("chat")
    }

    const cur = weather?.current
    const daily = weather?.daily || []
    const resolvedName = weather?.resolved?.name || weather?.requested_location || farmerLocation
    const resolvedState = weather?.resolved?.state || mandi?.state || ""

    const filteredMandi = (mandi.records || []).filter(r => {
        if (!marketQuery.trim()) return true
        const q = marketQuery.toLowerCase()
        return [r.market, r.district, r.commodity, r.variety].some(v => (v || "").toLowerCase().includes(q))
    })

    return (
        <div style={styles.shell}>
            {/* ── Sidebar ── */}
            <aside className="skeuo-card anim-enter-1" style={styles.sidebar}>
                <div style={styles.sideBrand}>
                    <div style={styles.sideLogo}>🌾</div>
                    <div>
                        <div className="embossed" style={styles.sideTitle}>AnnaData</div>
                        <div style={styles.sideSub}>{farmerName ? `Namaste, ${farmerName}` : "Kisan Mitra"}</div>
                    </div>
                </div>

                <button onClick={newChat} className="skeuo-btn" style={styles.newChatBtn}>+ New Chat</button>

                <div style={styles.sideSectionLabel}>Tabs</div>
                <div style={styles.tabCol}>
                    <button onClick={() => setTab("chat")} className="skeuo-btn-ghost" style={{ ...styles.tabBtn, ...(tab === "chat" ? styles.tabActive : {}) }}>
                        💬 Chat
                    </button>
                    <button onClick={() => { setTab("mandi"); if (!mandi.records.length) loadMandi() }} className="skeuo-btn-ghost" style={{ ...styles.tabBtn, ...(tab === "mandi" ? styles.tabActive : {}) }}>
                        🧅 Mandi Prices
                    </button>
                </div>

                <div style={styles.sideSectionLabel}>History</div>
                <div style={styles.sessionList}>
                    {sessions.length === 0 && <p style={styles.noChats}>No chats yet</p>}
                    {sessions.map((s) => (
                        <div key={s.session_id} onClick={() => loadHistory(s.session_id)} style={{
                            ...styles.sessionItem,
                            ...(s.session_id === sessionId ? styles.sessionActive : {})
                        }}>
                            <div style={styles.sessionTitle}>{s.title}</div>
                            <div style={styles.sessionDate}>{new Date(s.created_at).toLocaleDateString()}</div>
                        </div>
                    ))}
                </div>

                <div className="skeuo-inset" style={styles.locPlate}>
                    📍 {farmerLocation || (geo.lat ? `${geo.lat.toFixed(2)}, ${geo.lon.toFixed(2)}` : "Locating…")}
                </div>
                <button onClick={onLogout} className="skeuo-btn-ghost" style={styles.logoutBtn}>Logout</button>
            </aside>

            {/* ── Main ── */}
            <main style={styles.main}>
                {/* Top bar: tabs left, weather top-right + theme */}
                <header className="skeuo-card anim-enter" style={styles.topbar}>
                    <div style={styles.topLeft}>
                        <div style={styles.tabRow}>
                            <button onClick={() => setTab("chat")} className="skeuo-btn-ghost" style={{ ...styles.topTab, ...(tab === "chat" ? styles.tabActive : {}) }}>💬 Chat</button>
                            <button onClick={() => { setTab("mandi"); if (!mandi.records.length) loadMandi() }} className="skeuo-btn-ghost" style={{ ...styles.topTab, ...(tab === "mandi" ? styles.tabActive : {}) }}>🧅 Mandi</button>
                        </div>
                        <div style={styles.topLoc}>📍 {resolvedName || farmerLocation || "—"}{resolvedState ? ` • ${resolvedState}` : ""}</div>
                    </div>

                    <div style={styles.topRight}>
                        {/* Realtime weather pill */}
                        <button
                            className="skeuo-inset anim-enter-2"
                            style={styles.weatherPill}
                            onClick={() => setShowForecast(v => !v)}
                            title={farmerLocation ? `Live weather for ${farmerLocation} — click for 7-day` : "Live weather — click for 7-day"}
                        >
                            {weatherLoading ? (
                                <span style={styles.weatherSmall}>⟳ Locating weather…</span>
                            ) : weatherError || !cur ? (
                                <span style={styles.weatherSmall}>🌤️ Weather N/A</span>
                            ) : (
                                <>
                                    <span style={{ fontSize: 20 }}>{weatherIcon(cur.condition, cur.weathercode, daily?.[0]?.rainfall_mm)}</span>
                                    <span style={styles.weatherTemp}>{cur.temp_c ?? "—"}°C</span>
                                    <span style={styles.weatherCond}>{cur.condition}</span>
                                    <span style={styles.weatherLoc}>{resolvedName}</span>
                                    <span style={styles.chev}>{showForecast ? "▲" : "▼"}</span>
                                </>
                            )}
                        </button>
                        <button onClick={toggle} className="skeuo-btn-ghost" style={styles.iconBtn} title="Toggle dark / light theme">
                            {theme === "light" ? "🌙" : "☀️"}
                        </button>
                    </div>
                </header>

                {/* Expandable 7-day forecast */}
                {showForecast && daily.length > 0 && (
                    <div className="skeuo-card anim-enter" style={styles.forecastCard}>
                        <div style={styles.forecastHead}>
                            <span style={styles.forecastTitle}>🌦️ 7-day forecast — {resolvedName}</span>
                            <span style={styles.forecastMeta}>
                                💧 {daily[0]?.rainfall_mm ?? 0} mm today • 🌡️ {daily[0]?.min_temp}–{daily[0]?.max_temp}°C
                                {cur?.humidity != null && ` • 💦 ${cur.humidity}%`}
                                {cur?.wind_kmh != null && ` • 💨 ${cur.wind_kmh} km/h`}
                            </span>
                        </div>
                        <div style={styles.forecastStrip}>
                            {daily.map(d => (
                                <div key={d.date} className="skeuo-inset" style={styles.dayCard}>
                                    <div style={styles.dayDate}>{new Date(d.date + "T00:00").toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}</div>
                                    <div style={{ fontSize: 22 }}>{weatherIcon(d.condition, d.weathercode, d.rainfall_mm)}</div>
                                    <div style={styles.dayTemp}>{d.max_temp}° / {d.min_temp}°</div>
                                    <div style={styles.dayRain}>🌧 {d.rainfall_mm} mm{d.rain_chance != null ? ` (${d.rain_chance}%)` : ""}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {tab === "chat" ? (
                    <section className="skeuo-card anim-enter-2" style={styles.chatCard}>
                        <div style={styles.messages}>
                            {messages.length === 0 && (
                                <div style={styles.welcome}>
                                    <p style={{ fontSize: 46 }}>🌾</p>
                                    <p className="embossed" style={styles.welcomeTitle}>Welcome to AnnaData{farmerName ? `, ${farmerName}` : ""}</p>
                                    <p style={styles.welcomeSub}>Ask about crops, weather, market prices, pest control…</p>
                                    <div style={styles.chips}>
                                        {["What crop should I grow?", "Onion price in Maharashtra?", "My tomato has pests", "How to increase soil fertility?"].map(q => (
                                            <button key={q} onClick={() => setInput(q)} className="skeuo-btn-ghost" style={styles.chip}>{q}</button>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {messages.map((m, i) => (
                                <div key={i} style={{ ...styles.msgRow, justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                                    <div style={m.role === "user" ? styles.bubbleUser : styles.bubbleBot}>
                                        {m.role === "assistant" ? <ReactMarkdown>{m.content}</ReactMarkdown> : m.content}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div style={{ ...styles.msgRow, justifyContent: "flex-start" }}>
                                    <div style={styles.bubbleBot}>Thinking…</div>
                                </div>
                            )}
                            <div ref={bottomRef} />
                        </div>
                        <div style={styles.inputBar}>
                            <input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === "Enter" && sendMessage()}
                                placeholder="Ask about crops, weather, market prices..."
                                className="skeuo-input"
                                style={styles.textInput}
                            />
                            <button onClick={sendMessage} disabled={loading} className="skeuo-btn" style={styles.sendBtn}>
                                {loading ? "…" : "Send"}
                            </button>
                        </div>
                    </section>
                ) : (
                    <section className="skeuo-card anim-enter-2" style={styles.mandiCard}>
                        <div style={styles.mandiHead}>
                            <div>
                                <h2 className="embossed" style={styles.mandiTitle}>🧅 Mandi Prices — {mandi.district || mandi.state || farmerLocation || "your area"}</h2>
                                <p style={styles.mandiSub}>
                                    Live from <b>data.gov.in</b> (Agri Ministry) • {mandi.count ?? filteredMandi.length} records
                                    {mandi.fallback_to_state && ` • district had no listings, showing whole ${mandi.state}`}
                                </p>
                            </div>
                            <button onClick={() => loadMandi()} disabled={mandiLoading} className="skeuo-btn" style={styles.refreshBtn}>
                                {mandiLoading ? "⟳…" : "↻ Refresh"}
                            </button>
                        </div>

                        <div style={styles.chipRow}>
                            {COMMODITIES.map(c => (
                                <button
                                    key={c}
                                    onClick={() => { setCommodity(c); loadMandi(c) }}
                                    className="skeuo-btn-ghost"
                                    style={{ ...styles.mchip, ...(commodity === c ? styles.tabActive : {}) }}
                                >{c}</button>
                            ))}
                        </div>

                        <div style={styles.mandiTools}>
                            <input
                                value={marketQuery}
                                onChange={e => setMarketQuery(e.target.value)}
                                placeholder="Filter by market / district / variety…"
                                className="skeuo-input"
                                style={styles.filterInput}
                            />
                        </div>

                        {mandiLoading && <p style={styles.mandiStatus}>⟳ Pulling live mandi data…</p>}
                        {mandiError && <p style={styles.mandiError}>⚠️ {mandiError}</p>}
                        {!mandiLoading && !mandiError && filteredMandi.length === 0 && (
                            <p style={styles.mandiStatus}>No listings found for this filter. Try “All” or Refresh.</p>
                        )}

                        <div style={styles.mandiGrid}>
                            {filteredMandi.map((r, i) => (
                                <article key={i} className="skeuo-inset anim-enter" style={styles.priceCard}>
                                    <div style={styles.priceTop}>
                                        <b style={styles.commName}>{r.commodity}</b>
                                        <span style={styles.arrival}>{r.arrival_date || ""}</span>
                                    </div>
                                    <div style={styles.marketLine}>🏪 {r.market || "—"}</div>
                                    <div style={styles.distLine}>{r.district || ""}{r.district && r.state ? ` • ${r.state}` : r.state || ""}</div>
                                    {r.variety && <div style={styles.variety}>🌱 {r.variety}{r.grade ? ` (${r.grade})` : ""}</div>}
                                    <div style={styles.priceRow}>
                                        <span style={styles.pillMin}>Min ₹{r.min_price}</span>
                                        <span style={styles.pillModal}>Modal ₹{r.modal_price}</span>
                                        <span style={styles.pillMax}>Max ₹{r.max_price}</span>
                                    </div>
                                    <div style={styles.perUnit}>per quintal</div>
                                </article>
                            ))}
                        </div>
                    </section>
                )}
            </main>
        </div>
    )
}

const styles = {
    shell: { display: "flex", minHeight: "100vh", gap: 12, padding: 12, alignItems: "stretch" },
    sidebar: { width: 250, padding: "1rem", display: "flex", flexDirection: "column", gap: 10, flexShrink: 0 },
    sideBrand: { display: "flex", gap: 10, alignItems: "center" },
    sideLogo: {
        width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22,
        background: "radial-gradient(circle at 35% 30%, #fff8dd 0%, #ecd98a 40%, #9c7414 75%, #5e4206 100%)",
        border: "2px solid var(--card-border)",
        boxShadow: "inset 0 2px 3px rgba(255,255,255,0.8), inset 0 -4px 8px rgba(90,60,5,0.5), 0 4px 10px rgba(0,0,0,0.3)",
    },
    sideTitle: { fontWeight: 700, fontSize: 17 },
    sideSub: { fontSize: 11, color: "var(--text-2)" },
    newChatBtn: { padding: "10px", fontSize: 14, fontFamily: "inherit" },
    sideSectionLabel: { fontSize: 10, fontWeight: 700, letterSpacing: 1.2, color: "var(--text-3)", textTransform: "uppercase", marginTop: 4 },
    tabCol: { display: "flex", flexDirection: "column", gap: 6 },
    tabBtn: { padding: "9px 12px", fontSize: 13, textAlign: "left", fontFamily: "inherit" },
    tabActive: { boxShadow: "var(--shadow-pressed)", outline: "2px solid rgba(67,160,71,0.5)", outlineOffset: 1 },
    sessionList: { flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6, minHeight: 80 },
    noChats: { fontSize: 12, opacity: 0.6, textAlign: "center", marginTop: 8, color: "var(--text-3)" },
    sessionItem: {
        padding: "9px 10px", borderRadius: 10, cursor: "pointer", fontSize: 12,
        background: "var(--card-bg)", border: "1px solid var(--card-border)",
        boxShadow: "inset 0 1px 0 var(--card-edge-hi), 0 2px 6px rgba(0,0,0,0.1)",
    },
    sessionActive: { boxShadow: "var(--shadow-pressed)", outline: "2px solid rgba(67,160,71,0.5)" },
    sessionTitle: { fontWeight: 600, marginBottom: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
    sessionDate: { opacity: 0.6, fontSize: 11 },
    locPlate: { fontSize: 11, padding: "8px 10px", color: "var(--text-2)", fontWeight: 600 },
    logoutBtn: { padding: 8, fontSize: 13, fontFamily: "inherit" },

    main: { flex: 1, display: "flex", flexDirection: "column", gap: 12, minWidth: 0 },
    topbar: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, padding: "10px 14px", flexWrap: "wrap" },
    topLeft: { display: "flex", flexDirection: "column", gap: 4 },
    tabRow: { display: "flex", gap: 8 },
    topTab: { padding: "8px 14px", fontSize: 13, fontFamily: "inherit" },
    topLoc: { fontSize: 11, color: "var(--text-2)", fontWeight: 600 },
    topRight: { display: "flex", alignItems: "center", gap: 8 },
    weatherPill: {
        display: "flex", alignItems: "center", gap: 8, padding: "8px 14px",
        cursor: "pointer", fontFamily: "inherit", color: "var(--text-1)",
    },
    weatherTemp: { fontWeight: 700, fontSize: 16 },
    weatherCond: { fontSize: 12, color: "var(--text-2)", fontWeight: 600 },
    weatherLoc: { fontSize: 11, color: "var(--text-3)", fontWeight: 600, maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
    weatherSmall: { fontSize: 12, color: "var(--text-2)", fontWeight: 600 },
    chev: { fontSize: 10, color: "var(--text-3)" },
    iconBtn: { padding: "8px 12px", fontSize: 15 },

    forecastCard: { padding: "12px 14px" },
    forecastHead: { display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap", marginBottom: 10 },
    forecastTitle: { fontSize: 13, fontWeight: 700 },
    forecastMeta: { fontSize: 11, color: "var(--text-2)", fontWeight: 600 },
    forecastStrip: { display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4 },
    dayCard: { minWidth: 128, padding: "8px 10px", fontSize: 11 },
    dayDate: { fontWeight: 700, marginBottom: 2 },
    dayTemp: { fontWeight: 700, fontSize: 12, marginTop: 2 },
    dayRain: { color: "var(--text-2)", marginTop: 2 },

    chatCard: { flex: 1, display: "flex", flexDirection: "column", minHeight: 420, overflow: "hidden" },
    messages: { flex: 1, overflowY: "auto", padding: "1.25rem" },
    welcome: { textAlign: "center", color: "var(--text-2)", marginTop: "3rem" },
    welcomeTitle: { fontSize: 19, marginBottom: 6, color: "var(--text-1)", fontWeight: 700 },
    welcomeSub: { fontSize: 13 },
    chips: { marginTop: "1.25rem", display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap" },
    chip: { borderRadius: 20, padding: "7px 14px", fontSize: 12, fontFamily: "inherit" },
    msgRow: { display: "flex", marginBottom: 12 },
    bubbleUser: {
        maxWidth: "70%", padding: "10px 14px", fontSize: 14, lineHeight: 1.6,
        borderRadius: "18px 18px 4px 18px", color: "#fff8e7",
        background: "linear-gradient(180deg, #5cb860, #2e7d32)",
        border: "1px solid #1b5e20",
        boxShadow: "inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -3px 6px rgba(0,0,0,0.25), 0 3px 10px rgba(0,0,0,0.25)",
        textShadow: "0 1px 1px rgba(0,0,0,0.35)",
    },
    bubbleBot: {
        maxWidth: "75%", padding: "10px 14px", fontSize: 14, lineHeight: 1.6,
        borderRadius: "18px 18px 18px 4px", color: "var(--text-1)",
        background: "var(--card-bg)", border: "1px solid var(--card-border)",
        boxShadow: "inset 0 1px 0 var(--card-edge-hi), 0 3px 10px rgba(0,0,0,0.12)",
    },
    inputBar: { padding: "0.9rem", borderTop: "1px solid var(--card-border)", display: "flex", gap: 8, background: "transparent" },
    textInput: { flex: 1, padding: "11px 16px", fontSize: 14, borderRadius: 24, fontFamily: "inherit" },
    sendBtn: { borderRadius: 24, padding: "10px 22px", fontSize: 14, fontFamily: "inherit" },

    mandiCard: { flex: 1, padding: "1.25rem", minHeight: 420 },
    mandiHead: { display: "flex", justifyContent: "space-between", gap: 10, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 12 },
    mandiTitle: { fontSize: 18, fontWeight: 700 },
    mandiSub: { fontSize: 12, color: "var(--text-2)", marginTop: 4 },
    refreshBtn: { padding: "9px 16px", fontSize: 13, fontFamily: "inherit" },
    chipRow: { display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 10 },
    mchip: { borderRadius: 20, padding: "6px 13px", fontSize: 12, fontFamily: "inherit" },
    mandiTools: { marginBottom: 12 },
    filterInput: { padding: "10px 14px", fontSize: 13, fontFamily: "inherit" },
    mandiStatus: { fontSize: 13, color: "var(--text-2)", padding: "1rem 0", textAlign: "center" },
    mandiError: { fontSize: 13, color: "#b3261e", background: "rgba(178,38,30,0.1)", border: "1px solid rgba(178,38,30,0.3)", borderRadius: 10, padding: "10px 14px" },
    mandiGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 10 },
    priceCard: { padding: "12px 13px" },
    priceTop: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
    commName: { fontSize: 14 },
    arrival: { fontSize: 10, color: "var(--text-3)", fontWeight: 600 },
    marketLine: { fontSize: 12, fontWeight: 600 },
    distLine: { fontSize: 11, color: "var(--text-2)" },
    variety: { fontSize: 11, color: "var(--text-2)", marginTop: 2 },
    priceRow: { display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" },
    pillMin: { fontSize: 11, fontWeight: 700, padding: "4px 9px", borderRadius: 20, background: "rgba(67,160,71,0.16)", border: "1px solid rgba(67,160,71,0.5)" },
    pillModal: { fontSize: 11, fontWeight: 700, padding: "4px 9px", borderRadius: 20, background: "rgba(200,150,20,0.18)", border: "1px solid rgba(200,150,20,0.55)" },
    pillMax: { fontSize: 11, fontWeight: 700, padding: "4px 9px", borderRadius: 20, background: "rgba(60,120,200,0.16)", border: "1px solid rgba(60,120,200,0.5)" },
    perUnit: { fontSize: 10, color: "var(--text-3)", marginTop: 4 },
}
