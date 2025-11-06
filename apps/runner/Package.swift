import PackageDescription

let package = Package(
  name: "CoreQueueRunner",
  platforms: [
    .macOS(.v13)
  ],
  products: [
    .executable(name: "corequeue-runner", targets: ["Runner"])
  ],
  targets: [
    .executableTarget(
      name: "Runner",
      path: "Sources/Runner"
    )
  ]
)


