FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/device-service-0.0.1-SNAPSHOT.jar app.jar
COPY firebase-adminsdk.json .
ENTRYPOINT ["java", "-jar", "app.jar"]