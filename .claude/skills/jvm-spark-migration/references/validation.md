# Validation reference
Compare identical inputs and configuration with the Java 11 baseline where practical.
1. Build/test: clean compilation, unit tests, dependency resolution and packaging.
2. Runtime: driver and executors, classpath, module access, serializers, connectors.
3. Spark batch: deterministic output, error behavior, throughput, skew and resource use.
4. Streaming if present: checkpoint recovery, restarts, offsets, duplicates/loss semantics, backpressure, stateful operators and watermark behavior.
5. Infrastructure: container base image, CI toolchain, Kubernetes or VM runtime and rollback images.
6. Performance: record workload, hardware, JVM flags, latency, throughput, GC, CPU and memory. Avoid comparing unlike environments.
Return PASS / FAIL / NOT RUN per check, evidence, residual risks, Go/No-Go and rollback prerequisites. Do not modify checkpoints or production state for testing.
