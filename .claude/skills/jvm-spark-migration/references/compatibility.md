# Compatibility assessment reference
Check official, exact-version sources before recommending any target:
- Apache Spark documentation: https://spark.apache.org/docs/latest/
- Scala compatibility: https://docs.scala-lang.org/overviews/jdk-compatibility/overview.html
- Java migration guides: https://docs.oracle.com/en/java/javase/21/migrate/
- Apache Maven plugins or sbt/Gradle official docs for the build in use.
- Official release notes of Spark Kafka/Cassandra/Hadoop connectors, Kryo, Jackson, Netty and any other observed libraries.
Evaluate: Spark-supported Java versions, Scala binary suffix (_2.12/_2.13), bytecode target, transitive dependencies, Java module encapsulation and add-opens, removed JDK APIs, driver/executor JVM consistency, serialization and checkpoint persistence. A successful compile does not establish runtime support. Cite URLs and exact version statements; record unknowns.
