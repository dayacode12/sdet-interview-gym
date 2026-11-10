# Minimal JRE + JDK image for compiling and running candidate Java code.
# Used only by the backend's docker execution mode; the container is started
# with --network none --memory 512m --cpus 1 --read-only + tmpfs, so candidate
# code has no network, limited resources and no persistent filesystem.
FROM openjdk:17-jdk-slim

# A non-root user is unnecessary because the runtime flags already sandbox the
# process; keep the image tiny and deterministic.
WORKDIR /work

# Smoke check that the toolchain exists.
RUN javac -version && java -version
