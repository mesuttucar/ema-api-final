from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ema_calculator import find_best_ema_combination

app = FastAPI()

class EmaRequest(BaseModel):
    symbols: List[str]
    interval: str
    short_min: int
    short_max: int
    long_min: int
    long_max: int

@app.get("/")
def root():
    return {"status": "✅ API çalışıyor", "info": "POST /multi_ema_scan ile sorgu yapabilirsiniz."}

@app.post("/multi_ema_scan")
def multi_ema_scan(req: EmaRequest):
    print(f"🔍 Tarama Başlatıldı: {req.symbols}, Interval: {req.interval}, Aralıklar: short[{req.short_min}-{req.short_max}], long[{req.long_min}-{req.long_max}]")
    
    results = []
    for symbol in req.symbols:
        try:
            result = find_best_ema_combination(
                symbol,
                req.interval,
                req.short_min,
                req.short_max,
                req.long_min,
                req.long_max,
            )
            result["symbol"] = symbol
            results.append(result)
            print(f"✅ {symbol} tamamlandı → En iyi: short={result['short']}, long={result['long']}, kar={result['profit']}")
        except Exception as e:
            error_message = f"{symbol} için hata oluştu: {str(e)}"
            print(f"❌ {error_message}")
            results.append({"symbol": symbol, "error": error_message})
    return results
