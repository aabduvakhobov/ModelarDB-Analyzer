

version := "0.1.0-SNAPSHOT"
scalaVersion := "2.12.15"
name := "Verifier"

libraryDependencies ++= Seq(
  /* Code Generation */
  "org.scala-lang" % "scala-compiler" % scalaVersion.value,

  /* Query Interface */
  "org.apache.arrow" % "flight-core" % "7.0.0",

  /* Query Engine */
  "com.h2database" % "h2" % "1.4.200",
  "org.apache.spark" %% "spark-core" % "3.3.0" % "provided",
  "org.apache.spark" %% "spark-streaming" % "3.3.0" % "provided",
  "org.apache.spark" %% "spark-sql" % "3.3.0" % "provided",

  /* Storage Layer */
  //H2 is a full RDBMS with both a query engine and a storage layer
  "com.datastax.spark" %% "spark-cassandra-connector" % "3.1.0" % "provided", //Requires Spark
  "org.apache.hadoop" % "hadoop-client" % "3.3.4", //Same as Apache Spark 3.1.2 due to javax.xml.bind conflicts
  "org.apache.parquet" % "parquet-hadoop" % "1.12.2", //Same as Apache Spark
  "org.apache.orc" % "orc-core" % "1.6.14", //Same as Apache Spark

  /* Testing */
  "org.scalatest" %% "scalatest" % "3.2.14" % Test,
  "org.scalacheck" %% "scalacheck" % "1.17.0" % Test,
  "org.scalamock" %% "scalamock" % "5.2.0" % Test
)

/* Make SBT include the dependencies marked as provided when executing sbt run */
Compile / run := Defaults.runTask(
  Compile / fullClasspath,
  Compile / run / mainClass,
  Compile / run / runner).evaluated


/* Prevent Apache Spark from overwriting dependencies with older incompatible versions */
assembly / assemblyShadeRules := Seq(
  ShadeRule.rename("com.google.**" -> "com.google.shaded.@1").inAll
)

/* Concat and discard duplicate metadata in the dependencies when creating an assembly */
assembly / assemblyMergeStrategy := {
  case "META-INF/io.netty.versions.properties" => MergeStrategy.concat
  case "git.properties" => MergeStrategy.discard
  case "module-info.class" => MergeStrategy.discard
  case x => MergeStrategy.first
}

/* Use Ivy instead of Coursier due to Coursier GitHub Issue #2016 */
ThisBuild / useCoursier := false

/* Show the duration of tests and complete stack traces with color */
Test / testOptions += Tests.Argument("-oDF")

/* Execute tests sequentially to reduce the amount of memory required */
Test / parallelExecution := false



