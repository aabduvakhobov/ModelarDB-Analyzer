lazy val root = project.in(file("."))
  .settings(name := "downsampler", version := "0.1.0-SNAPSHOT")

libraryDependencies ++= Seq(
  "org.apache.hadoop" % "hadoop-client" % "3.2.0", //Same as ModelarDB Legacy
  "org.apache.orc" % "orc-core" % "1.6.14", //Same as ModelarDB Legacy
)
