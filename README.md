# nq-api
[![docker-publish](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-publish.yml)
[![Docker Image CI](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-image.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-image.yml)
[![Rust](https://github.com/NatiqQuran/nq-api/actions/workflows/rust.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/rust.yml)

Natiq Quran open API \

# Docker

Start nq-api with docker-compose

```bash
sudo docker compose up
```

# Build

```bash
cargo build --release
```

# Run

```bash
./target/release/nq-api
```

API will listen to 0.0.0.0:8080
