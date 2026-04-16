<div align="center">

# 🌾 ANNADATA
### *अन्नदाता — The One Who Feeds the World*

**Empowering India's farmers with AI-driven insights, from soil to sale.**

[![Made with React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Powered by Node.js](https://img.shields.io/badge/Backend-Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![ML Powered](https://img.shields.io/badge/AI-ML%20Powered-FF6B35?style=for-the-badge&logo=python&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

> 🏆 *Built with passion for India's 140 million farmers.*"

</div>

---

## 🚜 The Problem

India's farmers face a brutal trifecta every single season:
- **What to grow?** — No data-backed guidance on which crops suit their soil and climate.
- **Is my crop healthy?** — Disease goes undetected until it's too late.
- **Am I getting a fair deal?** — No transparent cost-revenue breakdown before investing.

**Annadata fixes all of that.** In one platform.

---

## ⚡ Features

### 🤖 ML-Powered Crop Recommendation
> Feed in your soil type, location, and season — get back the *optimal crop* to grow, backed by data.

### 🔬 Plant Disease Detection
> Snap a photo of your crop. Our model identifies the disease and tells you exactly what to do next.

### 🌦️ Weather & Soil Analysis
> Real-time environmental data — temperature, humidity, rainfall, soil fertility — to make every farming decision smarter.

### 📊 Cost & Revenue Analysis
> Transparent financial breakdown: investment required, expected yield, potential revenue, and alternate income sources. No more guessing games.

### 🛒 Buy / Sell Farming Equipment
> A marketplace built *for* farmers — list your equipment, find what you need, no middlemen.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🖥️ Frontend | React.js |
| ⚙️ Backend | Node.js + Express |
| 🤖 ML Models | Python (served via API) |
| 🌐 APIs | Weather, Soil & Location APIs |

---

## 🚀 Getting Started

### Prerequisites
- Node.js `v16+`
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/GaouravPatil/annadata.git
cd annadata

# Install all dependencies (frontend + backend)
npm install

# Start both frontend and backend concurrently
npm run dev
```

### Environment Variables

Create a `.env` file in the root directory:

```env
PORT=5000
WEATHER_API_KEY=your_weather_api_key
MONGO_URI=your_mongodb_connection_string
```

---

## 📁 Project Structure

```
annadata/
├── client/               # React frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # App pages
│   │   └── utils/        # Helper functions
├── server/               # Node.js + Express backend
│   ├── routes/           # API routes
│   ├── controllers/      # Business logic
│   └── models/           # Data models
├── ml/                   # ML models & inference scripts
└── README.md
```

---

## 🌍 Impact

> *"There are 140 million farmers in India. Each one deserves access to the same intelligence that large agricultural corporations have."*

Annadata democratizes precision agriculture — no expensive equipment, no agronomist on speed dial. Just a phone and a will to grow.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
# Create your feature branch
git checkout -b feature/AmazingFeature

# Commit your changes
git commit -m 'Add some AmazingFeature'

# Push and open a PR
git push origin feature/AmazingFeature
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Made with ❤️ for the backbone of India.**

*Jai Kisan. 🌾*

</div>
