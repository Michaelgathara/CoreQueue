// I'm not the best at Swift, so code here might be a bit messy
import Foundation

struct HTTP {
    static func request(_ url: URL, method: String = "GET", jsonBody: [String: Any]? = nil) async throws -> Data {
        var req = URLRequest(url: url)
        req.httpMethod = method
        if let body = jsonBody {
            req.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw NSError(domain: "HTTP", code: 1)
        }
        return data
    }
}

@main
enum RunnerMain {
    static func main() async {
        let apiBase = URL(string: ProcessInfo.processInfo.environment["API_BASE"] ?? "http://localhost:8000")!
        let name = Host.current().localizedName ?? UUID().uuidString
        let host = name
        let arch = "arm64"
        let gpuClass = "apple-silicon"

        do {
            let regURL = apiBase.appendingPathComponent("/runners/register")
            let regBody: [String: Any] = [
                "name": name,
                "host": host,
                "arch": arch,
                "gpu_class": gpuClass,
            ]
            let regData = try await HTTP.request(regURL, method: "POST", jsonBody: regBody)
            let reg = try JSONSerialization.jsonObject(with: regData) as? [String: Any]
            guard let runnerId = reg?["id"] as? String else { return }

            Task {
                await heartbeatLoop(apiBase: apiBase, runnerId: runnerId)
            }

            while true {
                if let job = try await claim(apiBase: apiBase, runnerId: runnerId) {
                    try await runJob(apiBase: apiBase, runnerId: runnerId, job: job)
                } else {
                    try await Task.sleep(nanoseconds: 1_000_000_000)
                }
            }
        } catch {
            // exit on fatal error
        }
    }

    static func heartbeatLoop(apiBase: URL, runnerId: String) async {
        while true {
            let hbURL = apiBase.appendingPathComponent("/runners/telemetry")
            let payload: [String: Any] = [
                "runner_id": runnerId,
                "cpu_usage": 0.1,
                "gpu_usage": 0.1,
                "mem_gb": 4.0,
                "thermal_state": "nominal",
            ]
            _ = try? await HTTP.request(hbURL, method: "POST", jsonBody: payload)
            try? await Task.sleep(nanoseconds: 5_000_000_000)
        }
    }

    struct ClaimedJob {
        let jobId: String
        let spec: [String: Any]
    }

    static func claim(apiBase: URL, runnerId: String) async throws -> ClaimedJob? {
        let url = apiBase.appendingPathComponent("/runners/claim")
        let data = try await HTTP.request(url, method: "POST", jsonBody: ["runner_id": runnerId])
        let obj = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let jobId = obj?["job_id"] as? String, let spec = obj?["spec"] as? [String: Any] else {
            return nil
        }
        return ClaimedJob(jobId: jobId, spec: spec)
    }

    static func runJob(apiBase: URL, runnerId: String, job: ClaimedJob) async throws {
        let startedURL = apiBase.appendingPathComponent("/runners/started")
        _ = try await HTTP.request(startedURL, method: "POST", jsonBody: ["job_id": job.jobId, "runner_id": runnerId])

        var exitCode: Int32 = 0
        if let runtime = job.spec["runtime"] as? [String: Any], let entry = runtime["entrypoint"] as? String {
            exitCode = await spawnShell(command: entry, apiBase: apiBase, jobId: job.jobId)
        }

        let finishedURL = apiBase.appendingPathComponent("/runners/finished")
        _ = try await HTTP.request(finishedURL, method: "POST", jsonBody: ["job_id": job.jobId, "runner_id": runnerId, "exit_code": exitCode])

        if let artifacts = job.spec["artifacts"] as? [String] {
            for pattern in artifacts {
                // naive glob expansion for demo: support single file paths
                let path = NSString(string: pattern).expandingTildeInPath
                if FileManager.default.fileExists(atPath: path) {
                    let url = apiBase.appendingPathComponent("/jobs/\(job.jobId)/artifacts")
                    if let data = FileManager.default.contents(atPath: path) {
                        var req = URLRequest(url: url)
                        req.httpMethod = "POST"
                        let filename = URL(fileURLWithPath: path).lastPathComponent
                        let boundary = "Boundary-\(UUID().uuidString)"
                        req.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
                        var body = Data()
                        body.append("--\(boundary)\r\n".data(using: .utf8)!)
                        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
                        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
                        body.append(data)
                        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
                        req.httpBody = body
                        let _ = try? await URLSession.shared.data(for: req)
                    }
                }
            }
        }
    }

    static func spawnShell(command: String, apiBase: URL, jobId: String) async -> Int32 {
        let process = Process()
        process.launchPath = "/bin/zsh"
        process.arguments = ["-lc", command]
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        try? process.run()

        let handle = pipe.fileHandleForReading
        handle.readabilityHandler = { fh in
            let data = fh.availableData
            if data.count > 0, let s = String(data: data, encoding: .utf8) {
                Task {
                    let url = apiBase.appendingPathComponent("/jobs/\(jobId)/logs/append")
                    _ = try? await HTTP.request(url, method: "POST", jsonBody: ["line": s])
                }
            }
        }

        process.waitUntilExit()
        handle.readabilityHandler = nil
        return process.terminationStatus
    }
}


