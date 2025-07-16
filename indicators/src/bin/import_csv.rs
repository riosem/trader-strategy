use serde::Deserialize;
use std::error::Error;

#[derive(Debug, Deserialize)]
struct Candle {
    timestamp: String,
    open: String,
    high: String,
    low: String,
    close: String,
    volume: String,
}

fn main() -> Result<(), Box<dyn Error>> {
    let mut rdr = csv::Reader::from_path("btc_data.csv")?;
    for result in rdr.deserialize() {
        let record: Candle = result?;
        println!("{:?}", record);
    }
    Ok(())
}