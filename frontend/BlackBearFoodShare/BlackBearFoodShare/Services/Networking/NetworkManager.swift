//
//  NetworkManager.swift
//  BlackBearFoodShare
//

import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL = "http://localhost:5000" // Should be configurable
    private let session = URLSession.shared
    
    private init() {}
    
    func request<T: Decodable>(_ endpoint: String, 
                               method: String = "GET", 
                               body: Data? = nil, 
                               requiresAuth: Bool = true) async throws -> T {
        
        guard let url = URL(string: baseURL + endpoint) else {
            throw BBFSError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if requiresAuth {
            if let token = SessionManager.shared.getToken() {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
        }
        
        if let body = body {
            request.httpBody = body
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw BBFSError.invalidResponse
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            do {
                let decoder = JSONDecoder()
                // Use ISO8601 with fractional seconds for the backend
                decoder.dateDecodingStrategy = .custom { decoder in
                    let container = try decoder.singleValueContainer()
                    let dateStr = try container.decode(String.self)
                    let formatter = ISO8601DateFormatter()
                    formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                    if let date = formatter.date(from: dateStr) {
                        return date
                    }
                    throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid date format: \(dateStr)")
                }
                return try decoder.decode(T.self, from: data)
            } catch {
                throw BBFSError.decodingError(error)
            }
        case 401: throw BBFSError.unauthorized
        case 403: throw BBFSError.forbidden
        case 429: throw BBFSError.rateLimited
        case 400:
            let errorMsg = String(data: data, encoding: .utf8) ?? "Unknown validation error"
            throw BBFSError.validationError(errorMsg)
        case 500:
            throw BBFSError.serverError("Internal Server Error")
        default:
            throw BBFSError.unknown
        }
    }
    
    // Support for multipart/form-data for image uploads
    func upload<T: Decodable>(_ endpoint: String, 
                              parameters: [String: String], 
                              image: Data, 
                              fileName: String) async throws -> T {
        
        guard let url = URL(string: baseURL + endpoint) else {
            throw BBFSError.invalidURL
        }
        
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        // TODO: Auth header
        
        var body = Data()
        
        for (key, value) in parameters {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"picture\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/webp\r\n\r\n".data(using: .utf8)!)
        body.append(image)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        let (data, response) = try await session.upload(for: request, from: body)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw BBFSError.invalidResponse
        }
        
        if httpResponse.statusCode == 200 || httpResponse.statusCode == 201 {
            return try JSONDecoder().decode(T.self, from: data)
        } else {
            throw BBFSError.serverError("Upload failed with status \(httpResponse.statusCode)")
        }
    }
}
