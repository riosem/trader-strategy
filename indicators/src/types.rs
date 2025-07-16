use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Candle {
    pub close: String,
    pub start: String,
    pub low: String,
    pub high: String,
    pub open: String,
    pub volume: String,
}