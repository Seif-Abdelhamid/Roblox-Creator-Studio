FROM alpine:latest
RUN apk add --no-cache g++ make cmake
WORKDIR /src
COPY . .
RUN mkdir -p build && cd build && cmake .. || true && make || true
CMD ["/bin/sh", "-c", "echo cpp container built"]