
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TradeDetails(BaseModel):
    buySellIndicator: str
    price: float
    quantity: int

class Trade(BaseModel):
    trade_id: str
    instrument_name: str
    instrument_id: str
    trader: str
    counterparty: Optional[str]
    trade_details: TradeDetails
    tradeDateTime: datetime

trades = [
    Trade(
        trade_id="1",
        instrument_name="CFTC",
        instrument_id="CFTC",
        trader="Bob Smith",
        counterparty="Goldman Sachs",
        trade_details=TradeDetails(
            buySellIndicator="BUY",
            price=100.0,
            quantity=10
        ),
        tradeDateTime=datetime(2022, 1, 1)
    ),
    Trade(
        trade_id="2",
        instrument_name="FINRA",
        instrument_id="FINRA",
        trader="John Doe",
        counterparty=None,
        trade_details=TradeDetails(
            buySellIndicator="SELL",
            price=200.0,
            quantity=5
        ),
        tradeDateTime=datetime(2021, 9, 4)
    ),
    Trade(
        trade_id="3",
        instrument_name="IIROC",
        instrument_id="IIROC",
        trader="Olivia Brown",
        counterparty=None,
        trade_details=TradeDetails(
            buySellIndicator="SELL",
            price=560.0,
            quantity=4
        ),
        tradeDateTime=datetime(2022, 10, 6)
    ),
    Trade(
        trade_id="4",
        instrument_name="BAR",
        instrument_id="BAR",
        trader="Ethan Davis",
        counterparty=None,
        trade_details=TradeDetails(
            buySellIndicator="SELL",
            price=480.0,
            quantity=2
        ),
        tradeDateTime=datetime(2021, 1, 11)
    ),
    Trade(
        trade_id="5",
        instrument_name="MIFID II",
        instrument_id="MIFID II",
        trader="Ava Garcia",
        counterparty=None,
        trade_details=TradeDetails(
            buySellIndicator="SELL",
            price=700.0,
            quantity=7
        ),
        tradeDateTime=datetime(2023, 5, 4)
    )
]

@app.get("/trades", response_model=List[Trade])
async def get_trades(search: Optional[str] = None):
    if search:
        search = search.lower()
        result = []
        for trade in trades:
            if (search in trade.instrument_name.lower() or
                search in trade.instrument_id.lower() or
                search in trade.trader.lower() or
                (trade.counterparty and search in trade.counterparty.lower())):
                result.append(trade)
        return result
    else:
        return trades


@app.get("/trades/")
async def get_trades(
    assetClass: Optional[str] = None,
    end: Optional[str] = None,
    maxPrice: Optional[float] = None,
    minPrice: Optional[float] = None,
    start: Optional[str] = None,
    tradeType: Optional[str] = None
):
    filtered_trades = trades
    if assetClass:
        filtered_trades = [trade for trade in filtered_trades if trade.instrument_name == assetClass]
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d')
        filtered_trades = [trade for trade in filtered_trades if trade.tradeDateTime <= end_date]
    if maxPrice:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price <= maxPrice]
    if minPrice:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price >= minPrice]
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        filtered_trades = [trade for trade in filtered_trades if trade.tradeDateTime >= start_date]
    if tradeType:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.buySellIndicator == tradeType]
    return filtered_trades

@app.get("/trades", response_model=List[Trade])
async def get_trades(
    assetClass: Optional[str] = None,
    end: Optional[datetime] = None,
    maxPrice: Optional[float] = Query(None, alias="max-price"),
    minPrice: Optional[float] = Query(None, alias="min-price"),
    start: Optional[datetime] = None,
    tradeType: Optional[str] = Query(None, alias="trade-type"),
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None
):
    result = trades
    if assetClass:
        result = [trade for trade in result if trade.instrument_name == assetClass]
    if end:
        result = [trade for trade in result if trade.tradeDateTime <= end]
    if maxPrice:
        result = [trade for trade in result if trade.trade_details.price <= maxPrice]
    if minPrice:
        result = [trade for trade in result if trade.trade_details.price >= minPrice]
    if start:
        result = [trade for trade in result if trade.tradeDateTime >= start]
    if tradeType:
        result = [trade for trade in result if trade.trade_details.buySellIndicator == tradeType]
    
    # Sort the results
    if sort_by:
        reverse = False
        if sort_by.startswith("-"):
            reverse = True
            sort_by = sort_by[1:]
        
        result.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
    
    # Paginate the results
    start_index = skip
    end_index = skip + limit
    result = result[start_index:end_index]
    
    return result

@app.get("/trades/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    for trade in trades:
        if trade.trade_id == trade_id:
            return trade
    raise HTTPException(status_code=404, detail="Trade not found")