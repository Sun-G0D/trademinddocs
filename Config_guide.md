# TradeMind Configuration Guide

## Introduction

This document provides a comprehensive overview of the configuration file system for the TradeMind algorithmic trading platform. It is intended for technical personnel responsible for the deployment, operational management, and fine-tuning of the platform in various environments, from development to production.

## Configuration File Overview

TradeMind utilizes a primary YAML (`.yaml`) formatted configuration file, typically named `config.yaml`, located in the `config/` directory of the project. This file governs the behavior of most platform components.

### 1. Loading Custom Configuration

The platform can be launched with a specific configuration file using the `--config` command-line argument:

```bash
$ ./bin/trademind --config /path/to/your/custom_config.yaml
```

### 2. Top-Level Configuration Sections

The `config.yaml` is structured into several top-level keys, each configuring a major aspect of the platform.

#### 2.1. `system`
Basic system-wide settings.

*   `name`: (String) An identifier for this system instance (e.g., QuantTrading, MyHFTSystem).
*   `log_level`: (String) Default logging verbosity for the system. Common values: `debug`, `info`, `warning`, `error`, `critical`.
*   `log_file`: (String) Path to the main system log file (e.g., `logs/system.log`). Ensure the directory exists and is writable.

#### 2.2. `message_bus`
Configuration for the internal messaging infrastructure (ZeroMQ).

*   `publisher_endpoint`: (String) The network endpoint (e.g., `tcp://*:5555`) where internal components publish messages.
*   `subscriber_endpoint`: (String) The network endpoint (e.g., `tcp://localhost:5555`) that internal components connect to for subscribing to messages. In a distributed setup, this might be the address of a central message broker or a known publisher.

#### 2.3. `service_manager`
Configuration parameters responsible for service health monitoring/coordination.

*   `id`: (String) Unique identifier for this service manager instance.
*   `heartbeat_interval_ms`: (Integer) Interval in milliseconds at which the service manager expects or sends heartbeats.

#### 2.4. `exchanges`
A list of configurations, where each item defines a connection to a specific trading exchange.

*   `name`: (String) A user-defined name for this exchange connection (e.g., Exchange1, MyBrokerFIX).
*   `host`: (String) The hostname or IP address of the exchange's gateway server.
*   `port`: (Integer) The port number for the exchange connection.
*   `sender_comp_id`: (String) Your FIX SenderCompID.
*   `target_comp_id`: (String) The exchange's FIX TargetCompID.
*   `username`: (String) Username for the FIX session, if required.
*   `password`: (String) Password for the FIX session, if required.
*   `fix_version`: (String) The FIX protocol version (e.g., FIX.4.2, FIX.4.4).
*   `heartbeat_interval`: (Integer) FIX HeartBtInt(108) in seconds.
*   `reset_seq_num`: (Boolean) If true, will send ResetSeqNumFlag(Y) on logon. Manage with caution in production.
*   `symbols`: (List of Strings) A list of instrument symbols that can be traded via this exchange connection.

#### 2.5. `data_sources`
A list of configurations for market data feeds.

*   `type`: (String) The type of data source protocol (e.g., `fix`, `websocket`).
*   `endpoint`: (String) The connection endpoint for the data source.
    *   For `fix`: e.g., `tcp://marketdata.example.com:8001`
    *   For `websocket`: e.g., `wss://realtime.example.com/feed`
*   `parameters`: (Object) A map of parameters specific to the data source type:
    *   For `fix`:
        *   `username`: (String) Username for the market data FIX session.
        *   `password`: (String) Password for the market data FIX session.
        *   `symbols`: (String, comma-separated) List of symbols to subscribe to for market data.
    *   For `websocket`:
        *   `api_key`: (String) API key for authentication.
        *   `subscription`: (String) Subscription message or channel details (e.g., `level2`, specific subscription JSON string).
        *   `symbols`: (String, comma-separated) List of symbols to subscribe to.

#### 2.6. `strategies`
A list defining the trading strategies to be loaded and run by the platform.

*   `id`: (String) A unique identifier for this strategy instance (e.g., `sma_crossover_1`).
*   `type`: (String) The type or class name of the strategy to be loaded (e.g., `sma_crossover`, `market_making`). Should correspond to a Python class.
*   `symbol`: (String) The primary instrument symbol this strategy instance will trade.
*   `active`: (Boolean) Whether this strategy instance should be active (`true`) or inactive (`false`) upon platform start.
*   `parameters`: (Object) A map of key-value pairs specific to the strategy type. These are passed to the strategy for its initialization and runtime logic.
    *   Examples: `fast_period`, `slow_period`, `trade_size`, `min_spread`, `max_position`.

#### 2.7. `risk_management`
Global pre-trade risk limits and controls.

*   `max_order_value`: (Numeric) Maximum notional value allowed for a single order.
*   `max_daily_loss`: (Numeric) Maximum permissible loss for the trading day before potential automated shutdown or alert.
*   `max_position_value`: (Numeric) Maximum total notional value allowed for any single position or across all positions.
*   `max_order_quantity`: (Numeric) Maximum quantity allowed for a single order.
*   `max_open_orders`: (Integer) Maximum number of live, open orders allowed concurrently.

#### 2.8. `performance`
Parameters for tuning internal queue sizes and threading, impacting system throughput and latency.

*   `order_book_queue_size`: (Integer) Size of internal queues related to order book updates.
*   `message_queue_size`: (Integer) Size of general internal message queues.
*   `thread_pool_size`: (Integer) Number of worker threads in key thread pools (e.g., for event processing, network I/O).

#### 2.9. `database`
Configuration for connecting to a database, used for storing trades, historical data, or strategy states.

*   `type`: (String) Type of database (e.g., `postgresql`, `mysql`, `sqlite`).
*   `host`: (String) Database server hostname or IP address.
*   `port`: (Integer) Database server port.
*   `database`: (String) Name of the database/schema.
*   `username`: (String) Database user.
*   `password`: (String) Database password.

#### 2.10. `logging` (Detailed logging settings, separate from `system.log_level`)
More fine-grained control over logging behavior.

*   `console_level`: (String) Logging level for console output (e.g., `info`, `debug`).
*   `file_level`: (String) Logging level for file output.
*   `max_file_size_mb`: (Integer) Maximum size in megabytes before a log file is rotated.
*   `max_files`: (Integer) Maximum number of rotated log files to keep.

### 3. Configuration in Containerized Environments (Docker/Kubernetes)

#### Docker
*   Mount configuration files into containers using volumes:
    ```bash
    docker run -v /path/on/host/config_prod.yaml:/app/config/config.yaml ... your_image_name
    ```
*   Inject secrets and dynamic parameters using Docker environment variables (`-e`).

#### Kubernetes
*   Store non-sensitive configuration in ConfigMaps and mount them as files or populate environment variables.
*   Store sensitive data in Kubernetes Secrets and mount them similarly.
*   Utilize Kubernetes service discovery for endpoints like `message_bus` or `database` hosts, rather than hardcoding IPs, by using internal Kubernetes DNS service names.
