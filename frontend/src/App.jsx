import { useState } from "react"
import Auth from "./components/Auth"
import Chat from "./components/Chat"

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [farmer, setFarmer] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("farmer") || "null")
    } catch {
      return null
    }
  })

  function handleLogin(payload) {
    // payload: { token, farmer_id, name, location, language }
    localStorage.setItem("token", payload.token)
    localStorage.setItem("farmer_id", payload.farmer_id)
    const profile = {
      name: payload.name || "",
      location: payload.location || "",
      language: payload.language || "en",
      farmer_id: payload.farmer_id,
    }
    localStorage.setItem("farmer", JSON.stringify(profile))
    // legacy key used by weather/mandi widgets
    if (profile.location) localStorage.setItem("farmer_location", profile.location)
    setToken(payload.token)
    setFarmer(profile)
  }

  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("farmer_id")
    localStorage.removeItem("farmer")
    localStorage.removeItem("farmer_location")
    setToken(null)
    setFarmer(null)
  }

  return (
    <div>
      {token
        ? <Chat token={token} farmer={farmer} onLogout={handleLogout} />
        : <Auth onLogin={handleLogin} />
      }
    </div>
  )
}
