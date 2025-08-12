FROM golang:1.21-alpine AS build
WORKDIR /src
COPY . .
RUN go mod download
RUN go build -o /out/server ./server

FROM alpine
WORKDIR /app
COPY --from=build /out/server /app/server
EXPOSE 8080
CMD ["/app/server"]