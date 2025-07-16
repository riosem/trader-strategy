pub mod event_handler;
pub mod historical_data;
pub mod types;

use lambda_runtime::{run, service_fn, tracing, Error};

use crate::event_handler::function_handler;

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
