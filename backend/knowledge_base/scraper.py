import requests
from bs4 import BeautifulSoup
import json
import os

# Free agricultural knowledge from government and trusted sources
KNOWLEDGE_DATA = [
    {
        "topic": "PM-Kisan Scheme",
        "content": """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme:
- Financial benefit of Rs 6000 per year to farmer families
- Amount paid in 3 installments of Rs 2000 each every 4 months
- Eligibility: All landholding farmer families with cultivable land
- Exclusion: Institutional land holders, farmer families holding constitutional posts
- Exclusion: Current and former holders of ministerial posts, income tax payers
- How to apply: Visit Common Service Centre (CSC) or pmkisan.gov.in
- Documents needed: Aadhaar card, bank account details, land records
- Helpline: 155261 or 1800115526 (Toll Free)"""
    },
    {
        "topic": "PMFBY Crop Insurance",
        "content": """Pradhan Mantri Fasal Bima Yojana (PMFBY):
- Comprehensive crop insurance scheme for farmers
- Premium rates: Kharif crops 2%, Rabi crops 1.5%, annual commercial crops 5%
- Coverage: Natural calamities, pests, diseases
- Coverage includes: Prevented sowing, mid-season adversity, post harvest losses
- How to apply: Through bank branches, CSC centers, or insurance company agents
- Eligibility: All farmers growing notified crops in notified areas
- Documents: Land records, bank account, Aadhaar, sowing certificate
- Claim process: Notify within 72 hours of crop loss to bank or insurance company"""
    },
    {
        "topic": "Soil Health Card",
        "content": """Soil Health Card Scheme:
- Government provides soil health card every 2 years to farmers
- Card contains information on 12 soil parameters
- Parameters: NPK, pH, organic carbon, micronutrients like Zinc, Iron, Copper
- Based on card recommendations, farmers can use fertilizers efficiently
- How to get: Contact local agriculture department or Krishi Vigyan Kendra
- Benefits: Reduces fertilizer cost by using only what is needed
- Improves crop yield by maintaining proper soil nutrition"""
    },
    {
        "topic": "Wheat Cultivation",
        "content": """Wheat Cultivation Guide:
- Sowing time: October-November (Rabi season)
- Suitable soil: Loamy soil with good drainage, pH 6-7.5
- Seed rate: 100-125 kg per hectare
- Varieties: HD-2967, GW-496, K-307, PBW-343
- Irrigation: 4-6 irrigations needed, first at 20-25 days after sowing
- Fertilizer: 120 kg Nitrogen, 60 kg Phosphorus, 40 kg Potassium per hectare
- Major pests: Aphids, Brown mite - use recommended pesticides
- Major diseases: Rust, Powdery mildew - use fungicides
- Harvesting: When grain moisture is 20-25%, April-May
- Yield: 40-50 quintals per hectare under good management"""
    },
    {
        "topic": "Rice Cultivation",
        "content": """Rice Cultivation Guide:
- Sowing time: June-July (Kharif season)
- Suitable soil: Clay loam, heavy soils that retain water
- Seed rate: 20-25 kg per hectare for transplanting
- Varieties: IR-64, Swarna, Jaya, Basmati 370, Pusa Basmati
- Nursery: Prepare 30 days before transplanting
- Transplanting: 25-30 day old seedlings, 2-3 seedlings per hill
- Water management: Maintain 5cm water during vegetative stage
- Fertilizer: 120 kg N, 60 kg P, 40 kg K per hectare
- Major pests: Brown planthopper, stem borer, leaf folder
- Harvesting: When 80% grains turn golden yellow, September-October
- Yield: 50-60 quintals per hectare"""
    },
    {
        "topic": "Onion Cultivation",
        "content": """Onion Cultivation Guide:
- Sowing time: Kharif June-July, Rabi October-November, Summer January-February
- Suitable soil: Well drained loamy soil, pH 6-7
- Seed rate: 8-10 kg per hectare
- Varieties: Nasik Red, Agrifound Light Red, Pusa Red, N-53
- Nursery: Raised beds of 1m width, sow seeds thinly
- Transplanting: 6-8 week old seedlings at 15x10 cm spacing
- Irrigation: 7-10 day intervals, stop 10 days before harvest
- Fertilizer: 100 kg N, 50 kg P, 50 kg K per hectare
- Pest control: Thrips - use Spinosad or Imidacloprid
- Disease: Purple blotch - use Mancozeb or Chlorothalonil
- Harvesting: When tops fall and necks dry, bulbs cured for 3-5 days
- Storage: Cool dry place with good ventilation, can store 3-6 months
- Yield: 250-300 quintals per hectare"""
    },
    {
        "topic": "Tomato Cultivation",
        "content": """Tomato Cultivation Guide:
- Sowing time: June-July (Kharif), November-December (Rabi)
- Suitable soil: Well drained sandy loam, pH 6-7
- Varieties: Pusa Ruby, Arka Vikas, Hybrid varieties
- Nursery: Raised beds, transplant at 4-5 leaf stage
- Spacing: 60x45 cm or 75x60 cm
- Irrigation: Drip irrigation preferred, regular watering needed
- Fertilizer: 120 kg N, 80 kg P, 80 kg K per hectare
- Major pests: Fruit borer - use Bt spray or Spinosad
- Major diseases: Early blight, Late blight - use Mancozeb
- Staking: Provide support when plant is 30cm tall
- Harvesting: 60-80 days after transplanting
- Yield: 200-300 quintals per hectare"""
    },
    {
        "topic": "Pest Control General",
        "content": """General Pest Control Guidelines:
- Integrated Pest Management (IPM) is recommended approach
- First use biological control: Neem based pesticides, Bt spray
- Use pheromone traps to monitor and trap insects
- Yellow sticky traps for whiteflies and aphids
- Neem oil spray (5ml per liter water) effective for many pests
- Chemical pesticides as last resort only
- Always read label before using any pesticide
- Wear protective gear when spraying pesticides
- Do not spray on windy days or before rain
- Maintain pre-harvest interval as mentioned on label
- Contact local KVK for pest identification and advice
- Helpline: Kisan Call Centre 1800-180-1551 (Toll Free)"""
    },
    {
        "topic": "Post Harvest Storage",
        "content": """Post Harvest Storage Guidelines:
- Store grains at moisture content below 12-14%
- Use clean, dry, pest-free storage structures
- Treat storage bins with malathion before storing
- Use hermetic storage bags for small quantities
- Warehouse Receipt System available at WDRA registered warehouses
- Cold storage facilities available for fruits and vegetables
- Onion storage: Well ventilated bamboo/brick structures
- Potato storage: Cool dark place, avoid light exposure
- Grain storage: Use PAU bin or mud bin with proper treatment
- Government cold storage schemes available under NHM
- e-NAM platform for trading stored produce online"""
    },
    {
        "topic": "Kisan Call Centre",
        "content": """Kisan Call Centre and Farmer Helplines:
- Kisan Call Centre: 1800-180-1551 (Toll Free, 24x7)
- PM-Kisan Helpline: 155261 or 1800115526
- Soil Health Card: Contact local agriculture department
- Crop Insurance PMFBY: Contact nearest bank or insurance office
- Krishi Vigyan Kendra (KVK): Present in every district
- KVK services: Training, demonstrations, soil testing, seed distribution
- mKisan portal: SMS based advisory service
- Kisan Suvidha app: Weather, market prices, plant protection info
- IFFCO Kisan app: Agri advisory in local languages"""
    }
]

def save_knowledge_base():
    os.makedirs("knowledge_base/data", exist_ok=True)
    with open("knowledge_base/data/agricultural_knowledge.json", "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_DATA, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(KNOWLEDGE_DATA)} knowledge entries")

if __name__ == "__main__":
    save_knowledge_base()
