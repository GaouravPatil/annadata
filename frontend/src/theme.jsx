import { createContext, useContext, useEffect, useState } from "react"

const ThemeContext = createContext({ theme: "light", toggle: () => {} })

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(() => localStorage.getItem("annadata-theme") || "light")

    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme)
        localStorage.setItem("annadata-theme", theme)
    }, [theme])

    function toggle() {
        setTheme(t => (t === "light" ? "dark" : "light"))
    }

    return (
        <ThemeContext.Provider value={{ theme, toggle }}>
            {children}
        </ThemeContext.Provider>
    )
}

export function useTheme() {
    return useContext(ThemeContext)
}
