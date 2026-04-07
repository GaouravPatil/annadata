import { useState } from "react"
import Auth from "./components/Auth"
import Chat from "./components/Chat"

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [farmerId, setFarmerId] = useState(localStorage.getItem("farmer_id"))

  function handleLogin(token, farmerId) {
    localStorage.setItem("token", token)
    localStorage.setItem("farmer_id", farmerId)

    setToken(token)
    setFarmerId(farmerId)
  }

  function handleLogout() {
    localStorage.clear()
    setToken(null)
    setFarmerId(null)
  }

  return (
    <div>
      {token
        ? <Chat token={token} onLogout={handleLogout} />
        : <Auth onLogin={handleLogin} />
      }
    </div>
  )
}