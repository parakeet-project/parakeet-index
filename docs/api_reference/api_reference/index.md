 <div align="center">
 <img alt="Parakeet Index Logo" src="_static/assets/favicon.png" width="80px">
  <h2>🦜 Parakeet Index</h2>
  <p><strong>Build production-ready AI applications with modular, composable components.</strong></p>
</div>

## ⚡ Starter
The quickest way to get up and running is with the starter bundle, which includes the core framework plus our most popular integrations:

=== "pip"

    ```bash
    $ pip install parakeet-index
    ```

=== "uv"

    ```bash
    $ uv add parakeet-index
    ```

## 🔧 Advanced (recommended for production)
For production deployments, we recommend installing only the core package plus the specific integrations you actually use:

=== "pip"

    ```bash
    $ pip install parakeet-index-core
    $ pip install parakeet-index-llms-*
    $ pip install parakeet-index-vector-stores-*
    ```

=== "uv"

    ```bash
    $ uv add parakeet-index-core
    $ uv add parakeet-index-llms-*
    $ uv add parakeet-index-vector-stores-*
    ```
<small>
Installing individual packages instead of the full bundle keeps your environment lean:

- **Smaller footprint** — Fewer dependencies means smaller Docker images and faster cold starts.
- **Fewer conflicts** — Avoid pulling in transitive dependencies from integrations you never use. 
- **Security surface** — Less third-party code to audit, patch, and monitor for vulnerabilities.
- **Predictable upgrades** — Control exactly which integrations get updated and when.
</small>

## ✨ Highlight features

- **Modular Architecture** — Pick only the components you need. Each integration is its own installable package.
- **Enterprise Integrations** — First-class support for watsonx.ai, Elasticsearch, Chroma, Hugging Face, and more.
- **Built-in Observability** — Instrument your pipelines with OpenTelemetry-compatible tracing and custom metrics.
- **Guardrails** — Apply input/output guardrails to keep your AI applications safe and compliant.
- **Async-First Workflows** — Event-driven workflow engine with fan-out/fan-in, shared state, and built-in HTTP server.

## 👋 Contributing

We welcome contributions! Please see our [issue templates](https://github.com/parakeet-project/parakeet-index/issues/new/choose) to get started.

## License

[Apache License 2.0](LICENSE).
